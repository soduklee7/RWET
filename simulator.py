import numpy as np
import scipy.io as spio
import matplotlib.pyplot as plt
import sys
# from scipy.interpolate import interp1d
from scipy import interpolate

veh_data = spio.loadmat('data/veh_data.mat', squeeze_me=True)
veh_data_t = veh_data['t']
veh_data_tract_force_N = veh_data['tract_force_N']
veh_data_mass_kg = veh_data['mass_kg']
veh_data_spd_mps_in = veh_data['spd_mps_in']
vehspd_mps = veh_data['spd_mps']
veh_data_dist_m = veh_data['dist_m']
dt = veh_data_t[1] - veh_data_t[0]

vehspd_mps1 = np.zeros(len(veh_data_t))
veh_data_dist_m1 = np.zeros(len(veh_data_t))
print('dt =', dt, ' size of t_cyc =', len(veh_data_t))

vehspd_mps1[0] = vehspd_mps[0]
veh_data_dist_m1[0] = veh_data_dist_m[0]
for i in range(1, len(veh_data_t)):
    a_out = veh_data_tract_force_N[i] / veh_data_mass_kg[i]
    vehspd_mps1[i] = Vehicle.speed_integrator(dt, a_out, vehspd_mps1[i-1], vehspd_mps[i])
    veh_data_dist_m1[i] = veh_data_dist_m1[i - 1] + vehspd_mps1[i] * dt

fig1 = plt.figure(figsize=(11, 8.5))
plt.plot(veh_data_t, vehspd_mps, 'b-')
plt.plot(veh_data_t, vehspd_mps1, 'r--')

plt.grid()
plt.xlabel('Elapsed Time (s)')
plt.ylabel('Vehicle Speeds')
plt.legend(['by Matlab', 'by Python'], fontsize=14, loc='upper right')

fig1 = plt.figure(figsize=(11, 8.5))
plt.plot(veh_data_t, veh_data_dist_m, 'b-')
plt.plot(veh_data_t, veh_data_dist_m1, 'r--')

plt.grid()
plt.xlabel('Elapsed Time (s)')
plt.ylabel('VMT (m)')
plt.legend(['by Matlab', 'by Python'], fontsize=14, loc='upper left')

plt.show()
