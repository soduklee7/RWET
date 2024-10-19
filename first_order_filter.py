### Code Source:

import numpy as np
from scipy.signal import butter, lfilter

'''
Code Source:
https://www.google.com/search?q=low+pass+first+order+filter+python&sca_esv=a705397e3bbcc753&rlz=1C1GCEA_enUS926US926&ei=7rMTZ97fHa_gp84PoJCdoA4&ved=0ahUKEwjejqeixpqJAxUv8MkDHSBIB-QQ4dUDCBA&uact=5&oq=low+pass+first+order+filter+python&gs_lp=Egxnd3Mtd2l6LXNlcnAiImxvdyBwYXNzIGZpcnN0IG9yZGVyIGZpbHRlciBweXRob24yBhAAGAgYHjILEAAYgAQYhgMYigUyCxAAGIAEGIYDGIoFMgsQABiABBiGAxiKBTIIEAAYgAQYogQyCBAAGIAEGKIESPVAUPImWJE-cAJ4AJABAJgBRaABkwWqAQIxMbgBA8gBAPgBAZgCDKACgwXCAgoQABiwAxjWBBhHwgIIEAAYBxgIGB7CAggQABgIGA0YHsICCBAAGKIEGIkFmAMAiAYBkAYIkgcCMTKgB71J&sclient=gws-wiz-serp
'''
def first_order_filter(data, alpha):
    """Applies a first-order low-pass filter to the data.

    Args:
        data: The input data array.
        alpha: The smoothing factor (0 < alpha < 1).

    Returns:
        The filtered data array.
    """

    filtered_data = np.zeros_like(data)
    filtered_data[0] = data[0]

    for i in range(1, len(data)):
        filtered_data[i] = alpha * data[i] + (1 - alpha) * filtered_data[i - 1]

    return filtered_data

def lpf(x, omega_c, T):
    """Implement a first-order low-pass filter.

    The input data is x, the filter's cutoff frequency is omega_c
    [rad/s] and the sample time is T [s].  The output is y.
    """
    y = x
    alpha = (2 - T * omega_c) / (2 + T * omega_c)
    beta = T * omega_c / (2 + T * omega_c)
    for k in range(1, N):
        y[k] = alpha * y[k - 1] + beta * (x[k] + x[k - 1])
    return y

### Code Source: https://stackoverflow.com/questions/25191620/creating-lowpass-filter-in-scipy-understanding-methods-and-units
def butter_lowpass(cutoff, fs, order=1):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=1):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

class MinMaxSlewRateFilter:
    def __init__(self, min_slew_rate, max_slew_rate, initial_value=0):
        self.min_slew_rate = min_slew_rate
        self.max_slew_rate = max_slew_rate
        self.last_value = initial_value

    def filter(self, value, dt):
        # Calculate the maximum allowed change based on the slew rate
        max_change = self.max_slew_rate * dt  # Assuming dt is the time step
        min_change = self.min_slew_rate * dt

        # Limit the change to be within the allowed range
        change = max(min(value - self.last_value, max_change), min_change)

        # Update the last value and return the filtered value
        self.last_value += change
        return self.last_value

# # Generate a noisy signal
#     fs = 1000  # Sampling rate
#     t = np.arange(0, 1, 1/fs)
#     signal = np.sin(2*np.pi*50*t) + 0.5*np.sin(2*np.pi*200*t)
#
#     # Filter the signal
#     cutoff = 100  # Cutoff frequency
#     filtered_signal = butter_lowpass_filter(signal, cutoff, fs)

'''
Code Source: 
https://www.google.com/search?q=first+order+filter+scipy&sca_esv=a705397e3bbcc753&rlz=1C1GCEA_enUS926US926&ei=iK0TZ4PZI5mmptQPjIH3uQ8&ved=0ahUKEwiDvaWVwJqJAxUZk4kEHYzAPfcQ4dUDCBA&uact=5&oq=first+order+filter+scipy&gs_lp=Egxnd3Mtd2l6LXNlcnAiGGZpcnN0IG9yZGVyIGZpbHRlciBzY2lweTIGEAAYFhgeMgYQABgWGB4yBhAAGBYYHjIGEAAYFhgeMgYQABgWGB4yCxAAGIAEGIYDGIoFMgsQABiABBiGAxiKBTILEAAYgAQYhgMYigUyCxAAGIAEGIYDGIoFMggQABiABBiiBEikLVCcCFijKXACeACQAQCYAUegAZ8GqgECMTO4AQPIAQD4AQGYAg6gAogGwgIKEAAYsAMY1gQYR8ICCxAAGIAEGJECGIoFwgIFEAAYgATCAggQABgWGAoYHsICCBAAGKIEGIkFmAMAiAYBkAYIkgcCMTSgB8FH&sclient=gws-wiz-serp
'''
#
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# Generate a noisy signal
t = np.linspace(0, 1, 1000, endpoint=False)
x = np.sin(2 * np.pi * 10 * t) + np.random.normal(0, 0.5, 1000)

# Design the filter
fs = 1000  # Sampling frequency
cutoff = 50  # Cutoff frequency
b, a = signal.butter(1, cutoff / (fs / 2), 'lowpass')

# Apply the filter
y = signal.lfilter(b, a, x)
y1 = first_order_filter(x, 0.25)
# Plot the results
# plt.plot(t, x, 'b-', label='Noisy signal')
plt.plot(t, y, 'b-', label='Filtered signal')
plt.plot(t, y1, 'r--', label='First-order filter signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.legend()
plt.show()