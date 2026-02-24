#!/usr/bin/env python3
"""
Write python script to make Matlab continuous time integration of the input signals.
Write python script to make Matlab continuous time derivatives of the input signals.

Continuous-time derivatives of input signals (MATLAB-like) in Python.

Features:
- Numerical gradient (nonuniform sampling supported)
- Savitzky–Golay smoothed derivative (uniform sampling required)
- Proper LTI differentiator approximation via lsim with H(s) = ωc s / (s + ωc)

Requires:
- numpy
- scipy
- matplotlib (only for the demo plot)

Usage example:
    python differentiate_signals.py
"""

from typing import Union, Iterable, Optional
import numpy as np
from scipy import signal as sp_signal
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt


def _is_strictly_increasing(t: np.ndarray) -> bool:
    dt = np.diff(t)
    return np.all(dt > 0)


def _is_uniform_time(t: np.ndarray, rtol: float = 1e-3) -> bool:
    dt = np.diff(t)
    return np.allclose(dt, dt[0], rtol=rtol, atol=0)


def _make_odd(n: int) -> int:
    return n if n % 2 == 1 else n - 1


def differentiate_continuous(
    t: np.ndarray,
    u: np.ndarray,
    method: str = "gradient",
    savgol_window: Optional[int] = None,
    savgol_polyorder: int = 3,
    lsim_wc: Optional[float] = None,
) -> np.ndarray:
    """
    Differentiate input signal(s) over time, approximating continuous-time derivative.

    Parameters
    ----------
    t : array_like, shape (N,)
        Time vector (must be strictly increasing).
    u : array_like, shape (N,) or (N, M)
        Input signal(s). If 2D, each column is a separate signal to differentiate.
    method : {'gradient', 'savgol', 'lsim'}, optional
        - 'gradient': Uses numpy.gradient(u, t). Works with nonuniform sampling.
        - 'savgol'  : Savitzky–Golay smoothed differentiator. Requires (nearly) uniform sampling.
        - 'lsim'    : LTI differentiator approximation H(s) = ωc s/(s + ωc) via scipy.signal.lsim.
                      Choose ωc high relative to signal bandwidth (but below Nyquist) to approximate du/dt.
    savgol_window : int, optional
        Window length for Savitzky–Golay filter (odd integer). If None, a reasonable default is chosen.
        Must be >= (savgol_polyorder + 2) and < N.
    savgol_polyorder : int, optional
        Polynomial order for Savitzky–Golay filter (e.g., 2 or 3).
    lsim_wc : float, optional
        Cutoff frequency ωc (rad/s) for the LTI differentiator approximation. If None, a default based
        on the sampling interval is chosen (≈ 0.8 * Nyquist rad/s for near-uniform sampling).

    Returns
    -------
    y : ndarray, shape (N,) or (N, M)
        Estimated derivative(s) du/dt. Same shape as input u.

    Notes
    -----
    - Numerical differentiation is noise-amplifying. If inputs are noisy, prefer 'savgol' or 'lsim' with
      appropriate ωc to limit high-frequency gain.
    - 'gradient' is simple and supports nonuniform t; 'savgol' gives smoother results but requires uniform t.
    - The 'lsim' approach uses a proper continuous-time system H(s) = ωc s/(s + ωc), which approximates a
      differentiator for frequencies well below ωc and bounds gain at high frequencies.

    """
    t = np.asarray(t).reshape(-1)
    u = np.asarray(u)
    if u.ndim == 1:
        u = u[:, None]  # make 2D
    if u.shape[0] != t.size:
        raise ValueError("u must have the same number of rows/samples as t length.")
    if not np.all(np.isfinite(t)) or not np.all(np.isfinite(u)):
        raise ValueError("Inputs contain non-finite values.")
    if not _is_strictly_increasing(t):
        raise ValueError("Time vector t must be strictly increasing.")

    N, M = u.shape
    y = np.zeros_like(u)

    if method.lower() == "gradient":
        # Numerical gradient supports nonuniform t
        for i in range(M):
            y[:, i] = np.gradient(u[:, i], t)

    elif method.lower() == "savgol":
        # Requires uniform sampling
        if not _is_uniform_time(t):
            raise ValueError("Savgol method requires (nearly) uniform sampling in t.")
        dt = float(t[1] - t[0])
        # Choose default window if not provided
        if savgol_window is None:
            # Aim for ~50-101 samples; ensure odd and valid
            target = min(max(51, int(N // 10) * 2 + 1), N - 1)
            savgol_window = _make_odd(target)
        # Validate window
        if savgol_window >= N:
            savgol_window = _make_odd(max(5, N - 1))
        if savgol_window <= savgol_polyorder:
            savgol_window = savgol_polyorder + 3
            savgol_window = _make_odd(savgol_window)

        for i in range(M):
            y[:, i] = savgol_filter(
                u[:, i],
                window_length=savgol_window,
                polyorder=savgol_polyorder,
                deriv=1,
                delta=dt,
                mode="interp",
            )

    elif method.lower() == "lsim":
        # Proper differentiator approximation: H(s) = ωc s / (s + ωc)
        # Choose default ωc if not provided (near Nyquist, but below to avoid noise blow-up)
        dt_avg = float(np.mean(np.diff(t)))
        nyquist_rad_s = np.pi / dt_avg
        wc = lsim_wc if lsim_wc is not None else 0.8 * nyquist_rad_s
        if wc <= 0:
            raise ValueError("lsim_wc must be positive.")

        # Transfer function: numerator = [ωc, 0], denominator = [1, ωc]
        num = np.array([wc, 0.0])
        den = np.array([1.0, wc])
        # Convert to state-space
        A, B, C, D = sp_signal.tf2ss(num, den)

        for i in range(M):
            sys = sp_signal.StateSpace(A, B, C, D)
            # lsim: yout is the filter output; no state initialization needed (x0 = 0)
            _, yout, _ = sp_signal.lsim(sys, U=u[:, i], T=t)
            y[:, i] = yout.reshape(-1)
    else:
        raise ValueError("method must be 'gradient', 'savgol', or 'lsim'.")

    return y.squeeze()  # return 1D if input was 1D


def demo():
    """Demonstration: differentiate a sine plus ramp, with and without noise."""
    # Time base (uniform sampling)
    t = np.linspace(0, 5, 5001)  # 5 seconds @ ~1 kHz
    dt = t[1] - t[0]

    # Signals
    f = 2.0  # Hz
    u1 = np.sin(2 * np.pi * f * t)             # smooth sinusoid
    u2 = 0.3 * t + 0.5 * np.sin(2 * np.pi * 0.5 * t)  # ramp + low-frequency sinusoid
    # Add some noise
    rng = np.random.default_rng(123)
    noise = 0.05 * rng.standard_normal(t.size)
    u_noisy = u1 + noise

    U = np.column_stack([u1, u2, u_noisy])

    # Derivatives using different methods
    y_grad = differentiate_continuous(t, U, method="gradient")
    y_savgol = differentiate_continuous(t, U, method="savgol", savgol_window=101, savgol_polyorder=3)
    y_lsim = differentiate_continuous(t, U, method="lsim")  # default ωc ≈ 0.8*Nyquist

    # Ground-truth for comparison (for u1 and u2 only)
    true_du1 = 2 * np.pi * f * np.cos(2 * np.pi * f * t)
    true_du2 = 0.3 + 0.5 * 2 * np.pi * 0.5 * np.cos(2 * np.pi * 0.5 * t)

    # Plot
    fig, axs = plt.subplots(4, 1, sharex=True, figsize=(10, 10))
    axs[0].plot(t, U[:, 0], label="u1 (sin)", color="C0")
    axs[0].plot(t, U[:, 1], label="u2 (ramp+sin)", color="C1")
    axs[0].plot(t, U[:, 2], label="u_noisy", color="C2", alpha=0.7)
    axs[0].set_ylabel("Input")
    axs[0].legend(loc="upper right")
    axs[0].grid(True)

    axs[1].plot(t, y_grad[:, 0], label="grad: du1/dt", color="C0")
    axs[1].plot(t, y_grad[:, 1], label="grad: du2/dt", color="C1")
    axs[1].plot(t, y_grad[:, 2], label="grad: d(noisy)/dt", color="C2", alpha=0.7)
    axs[1].set_ylabel("Derivative (gradient)")
    axs[1].legend(loc="upper right")
    axs[1].grid(True)

    axs[2].plot(t, y_savgol[:, 0], label="savgol: du1/dt", color="C0")
    axs[2].plot(t, y_savgol[:, 1], label="savgol: du2/dt", color="C1")
    axs[2].plot(t, y_savgol[:, 2], label="savgol: d(noisy)/dt", color="C2", alpha=0.7)
    axs[2].set_ylabel("Derivative (savgol)")
    axs[2].legend(loc="upper right")
    axs[2].grid(True)

    axs[3].plot(t, y_lsim[:, 0], label="lsim: du1/dt", color="C0")
    axs[3].plot(t, y_lsim[:, 1], label="lsim: du2/dt", color="C1")
    axs[3].plot(t, y_lsim[:, 2], label="lsim: d(noisy)/dt", color="C2", alpha=0.7)
    axs[3].plot(t, true_du1, "--", label="true d(u1)/dt", color="k", alpha=0.6)
    axs[3].plot(t, true_du2, "--", label="true d(u2)/dt", color="gray", alpha=0.6)
    axs[3].set_xlabel("Time [s]")
    axs[3].set_ylabel("Derivative (lsim approx)")
    axs[3].legend(loc="upper right")
    axs[3].grid(True)

    plt.tight_layout()
    plt.show()

    print(f"Sampling interval dt ≈ {dt:.6f} s")


if __name__ == "__main__":
    demo()