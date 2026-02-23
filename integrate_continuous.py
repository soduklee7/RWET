#!/usr/bin/env python3
"""
Write python script without using matlab.engine to make matlab continuous time integration of the input signals.

Continuous-time integration of input signals (x_dot = u(t)) using Python/Numpy.

- Integrates sampled signals over a time vector using Euler or trapezoidal rule.
- Optional output limits emulate a limited (saturating) integrator with
  hold-at-limits behavior (no further integration when at a limit and pushed outward).
- No MATLAB Engine required.

Author: (your name)
"""

import numpy as np


def integrate_continuous(
    t,
    u,
    x0=0.0,
    method="trapezoid",
    y_min=None,
    y_max=None,
    hold_at_limits=True,
):
    """
    Integrate x_dot = u(t) over time t, with optional output limits.

    Parameters
    ----------
    t : (N,) array_like
        Strictly increasing time vector.
    u : (N,) or (N,M) array_like
        Input signal sampled at times t (scalar or M-channel).
    x0 : float or (M,) array_like, optional
        Initial condition(s) for the integrator state at t[0].
    method : {"euler","trapezoid"}, optional
        Numerical scheme:
        - "euler":      x[k+1] = x[k] + dt * u[k]
        - "trapezoid":  x[k+1] = x[k] + dt * 0.5 * (u[k] + u[k+1])
    y_min : float or (M,) array_like or None, optional
        Lower saturation limit(s). None => -inf (no lower limit).
    y_max : float or (M,) array_like or None, optional
        Upper saturation limit(s). None => +inf (no upper limit).
    hold_at_limits : bool, optional
        If True and limits are provided, when x is at a limit and u would push
        it further outward, the state is held (no integration on that step).
        If False, integration proceeds and the result is then clamped.

    Returns
    -------
    x : (N,) or (N,M) ndarray
        State trajectory x(t), same length as t.

    Notes
    -----
    - Accuracy depends on time resolution and smoothness of u(t).
      Use a sufficiently fine t for your application.
    """
    # Validate and normalize inputs
    t = np.asarray(t, dtype=float).reshape(-1)
    if t.ndim != 1 or t.size < 2:
        raise ValueError("t must be a 1D array with at least two points.")
    if np.any(np.diff(t) <= 0):
        raise ValueError("t must be strictly increasing.")

    u = np.asarray(u, dtype=float)
    if u.ndim == 1:
        u = u[:, None]  # (N,1)
    elif u.ndim != 2:
        raise ValueError("u must be 1D (N,) or 2D (N,M).")
    if u.shape[0] != t.size:
        raise ValueError("t and u must have the same number of samples (axis 0).")

    N, M = u.shape

    def _to_vec(val, default):
        if val is None:
            arr = np.full(M, default, dtype=float)
        else:
            arr = np.asarray(val, dtype=float)
            if arr.ndim == 0:
                arr = np.full(M, float(arr), dtype=float)
            elif arr.shape != (M,):
                raise ValueError(f"value must be scalar or length-{M} vector.")
        return arr

    x0 = _to_vec(x0, 0.0)
    y_min = _to_vec(y_min, -np.inf)
    y_max = _to_vec(y_max, +np.inf)
    if np.any(y_max < y_min):
        raise ValueError("Each y_max must be >= y_min.")

    x = np.empty((N, M), dtype=float)
    # Clamp initial condition into limits
    x[0] = np.minimum(np.maximum(x0, y_min), y_max)

    # Integration loop
    for k in range(N - 1):
        dt = t[k + 1] - t[k]
        uk = u[k]
        xk = x[k]

        if method.lower() in ("euler", "forward_euler"):
            incr = dt * uk
        elif method.lower() in ("trapezoid", "trapezoidal"):
            incr = dt * 0.5 * (uk + u[k + 1])
        else:
            raise ValueError("method must be 'euler' or 'trapezoid'.")

        if np.isfinite(y_min).any() or np.isfinite(y_max).any():
            if hold_at_limits:
                # Hold if at limit and moving outward
                hold_mask = ((xk >= y_max) & (uk > 0)) | ((xk <= y_min) & (uk < 0))
                x_next = np.where(hold_mask, xk, xk + incr)
            else:
                # Integrate then clamp (possible windup outside limits during step)
                x_next = xk + incr
            # Clamp to limits
            x[k + 1] = np.minimum(np.maximum(x_next, y_min), y_max)
        else:
            # No limits
            x[k + 1] = xk + incr

    return x.squeeze()


if __name__ == "__main__":
    # Demo: integrate two input channels and plot results.
    import matplotlib.pyplot as plt

    # Time base (nonuniform example also works)
    t = np.linspace(0.0, 5.0, 2001)  # 2 kHz sampling

    # Inputs:
    #  - u0(t) = 1 (constant) -> x0(t) = t (until it hits limit)
    #  - u1(t) = sin(2π·0.5·t)
    u = np.column_stack([
        np.ones_like(t),
        np.sin(2 * np.pi * 0.5 * t),
    ])

    # Integrate with trapezoidal rule, limited to [-0.5, 1.0]
    x = integrate_continuous(
        t, u,
        x0=[0.0, 0.0],
        method="trapezoid",
        y_min=-0.5,
        y_max=1.0,
        hold_at_limits=True,
    )

    # Plot
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(8, 6))
    axs[0].plot(t, u[:, 0], label="u0(t) = 1.0")
    axs[0].plot(t, u[:, 1], label="u1(t) = sin(2π·0.5·t)")
    axs[0].set_ylabel("Input u(t)")
    axs[0].legend()
    axs[0].grid(True, alpha=0.3)

    axs[1].plot(t, x[:, 0], label="x0(t)")
    axs[1].plot(t, x[:, 1], label="x1(t)")
    axs[1].hlines([-0.5, 1.0], t[0], t[-1], colors='k', linestyles='dashed', alpha=0.4, label="limits")
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("State x(t)")
    axs[1].legend()
    axs[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()