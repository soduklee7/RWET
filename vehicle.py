import numpy as np
from first_order_filter import MinMaxSlewRateFilter

v_slew = MinMaxSlewRateFilter(-2, 2)

    @staticmethod 
    def speed_integrator(delta_t, acceleration, velocity_pre, v_cyc):
        # acceleration = (velocity - velocity_pre)/delta_t
        vehspd_mps = velocity_pre + acceleration * delta_t
        # vehspd_mps = np.max([0, v_slew.filter(vehspd_mps, delta_t)])

        v_delta = vehspd_mps - v_cyc
        acceleration_t = (vehspd_mps - velocity_pre)/delta_t
        a_delta = acceleration_t - acceleration

        if (vehspd_mps > 0) and (a_delta != 0) and (v_delta > 0.1):
            if (v_delta > 0) and (abs(a_delta <= 0.01)):
                vehspd_mps -= v_delta # 0.01
            elif (v_delta < 0) and (abs(a_delta <= 0.01)):
                vehspd_mps += v_delta # 0.01

        if vehspd_mps < 0: vehspd_mps = 0.0
        
        if (vehspd_mps < 0.5) and (v_cyc < 2.0) and (acceleration_t < 0): 
            vehspd_mps = v_cyc

        return vehspd_mps
