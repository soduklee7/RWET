import numpy as np
import pandas as pd

from differentiate_continuous import differentiate_continuous

def limited_integrator(t, u, x0=0.0, y_min=None, y_max=None, method="euler"):
    """
    Write python script to make matlab continuous time integrator Limited of the input signals.
    
    Emulate Simulink's continuous-time 'Integrator, Limited' for sampled inputs.

    Parameters
    ----------
    t : (N,) array_like
        Monotonic time vector.
    u : (N,) or (N,M) array_like
        Input signal(s) sampled at t. N samples, M channels.
    x0 : float or (M,) array_like, optional
        Initial condition for the integrator state per channel.
    y_min : float or (M,) array_like or None, optional
        Lower saturation limit(s). None -> -inf (no lower limit).
    y_max : float or (M,) array_like or None, optional
        Upper saturation limit(s). None -> +inf (no upper limit).
    method : {"euler","trapezoid"}, optional
        Discrete-time integration scheme:
        - "euler": x[k+1] = x[k] + dt * u[k]
        - "trapezoid": x[k+1] = x[k] + dt * 0.5 * (u[k] + u[k+1])

    Returns
    -------
    x : (N,) or (N,M) ndarray
        Integrated and saturated state trajectory.

    Notes
    -----
    - State-limited semantics: when the state is at a limit and the input would
      push it further into saturation, the derivative is forced to zero (hold).
    - After the hold decision, the next state is clamped into [y_min, y_max].
    - Accuracy depends on the time step spacing; use sufficiently fine t.
    """
    t = np.asarray(t).reshape(-1)
    if t.ndim != 1 or t.size < 2:
        raise ValueError("t must be a 1D array with at least two points.")
    if np.any(np.diff(t) <= 0):
        raise ValueError("t must be strictly increasing.")

    u = np.asarray(u)
    if u.ndim == 1:
        u = u[:, None]  # (N,1)
    elif u.ndim != 2:
        raise ValueError("u must be 1D (N,) or 2D (N,M).")

    N, M = u.shape
    if t.size != N:
        raise ValueError("t and u must have the same length along axis 0.")

    # Broadcast limits and x0
    def _as_vec(val, default):
        if val is None:
            arr = np.full(M, default, dtype=float)
        else:
            arr = np.asarray(val, dtype=float)
            if arr.ndim == 0:
                arr = np.full(M, float(arr), dtype=float)
            elif arr.shape != (M,):
                raise ValueError(f"value must be scalar or length-{M} vector.")
        return arr

    y_min = _as_vec(y_min, -np.inf)
    y_max = _as_vec(y_max, +np.inf)
    if np.any(y_max < y_min):
        raise ValueError("Each y_max must be >= y_min.")

    x = np.empty((N, M), dtype=float)
    x0 = _as_vec(x0, 0.0)
    # Clamp initial state inside limits
    x[0] = np.minimum(np.maximum(x0, y_min), y_max)

    # Integration loop
    for k in range(N - 1):
        dt = t[k + 1] - t[k]
        uk = u[k]
        xk = x[k]

        # Determine hold regions (state at limit and input pushes further out)
        hold_mask = ((xk >= y_max) & (uk > 0)) | ((xk <= y_min) & (uk < 0))

        # Compute unconstrained increment
        if method.lower() in ("euler", "forward_euler"):
            dx = dt * uk
        elif method.lower() in ("trapezoid", "trapezoidal", "trapezium"):
            dx = dt * 0.5 * (uk + u[k + 1])
        else:
            raise ValueError("method must be 'euler' or 'trapezoid'.")

        # Apply hold semantics: no change where held
        x_next = np.where(hold_mask, xk, xk + dx)

        # Clamp to limits
        x[k + 1] = np.minimum(np.maximum(x_next, y_min), y_max)

    # Return squeezed if single channel
    return x.squeeze()


if __name__ == "__main__":
    # Example usage
    import matplotlib.pyplot as plt

    # Time base
    # t = np.linspace(0, 5.0, 1001)  # 1 kHz sampling

    # # Two input channels:
    # #  - Channel 0: constant 1.0 (should ramp and saturate at 1.0 after 1 s)
    # #  - Channel 1: sinusoid (will integrate and hit limits)
    # u = np.column_stack([
    #     np.ones_like(t),
    #     np.sin(2 * np.pi * 0.5 * t)
    # ])

    df_vehaccel = pd.read_csv('veh_accel.csv')
    df_vehspd = pd.read_csv('vehspd.csv')
    
    t = df_vehaccel['Time'].values
    u = df_vehaccel['Data'].values  # (N,1)
    # Integrate with limits [-0.5, 1.0] on both channels
    x = limited_integrator(t, u, x0=0.0, y_min=0.0, y_max=np.inf, method="trapezoid")

    # Derivatives using different methods
    y_grad = differentiate_continuous(t, x, method="gradient")
    y_savgol = differentiate_continuous(t, x, method="savgol", savgol_window=101, savgol_polyorder=3)
    y_lsim = differentiate_continuous(t, x, method="lsim")
    
    # Plot
    fig, axs = plt.subplots(2, 1, sharex=True, figsize=(19.2, 10.8))
    axs[0].plot(df_vehspd['Time'].values, df_vehspd['Data'].values, 'b-', label="vehspd_data")
    axs[0].plot(t, x, 'r--', label="Limited Integrator Output of veh_accel") # should match vehspd_data closely, except for noise and any initial condition mismatch
    # axs[0].hlines([ -0.5, 1.0 ], t[0], t[-1], colors='k', linestyles='dashed', alpha=0.5, label="limits")
    axs[0].set_ylabel("Vehicle Speed (kph)")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(t, u, 'b-', label="veh_accel_data")
    axs[1].plot(t, y_lsim, 'r--', label="lsim derivative of vehspd") # lsim is best here, as it is designed for noisy data and has a tunable cutoff frequency (default ≈ 0.8*Nyquist)   
    # axs[1].plot(t, y_grad, 'k--', label="gradient derivative of vehspd")
    # axs[1].plot(t, y_savgol, 'g--', label="savgol derivative of vehspd") # GPS data is noisy, so savgol is very good for GPS data
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Acceleration (m/s²)")
    axs[1].legend()
    axs[1].grid(True)

    plt.tight_layout()
    plt.show()
    print("Done.")