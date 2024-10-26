import numpy as np
from first_order_filter import MinMaxSlewRateFilter

v_slew = MinMaxSlewRateFilter(-2, 2)

class Vehicle(object):
    def __init__(self, mass, density_air, c_drag, frontal_area, delta_t=0.01):
        self.mass = mass
        self.delta_t = delta_t
        self.density_air = 1.29
        self.c_drag = c_drag
        self.frontal_area = frontal_area
        self.gravity = 9.8
        self.aero_drag = 0

        self.velocity = 0
        self.acceleration = 0
        self.position = 0

        self.velocity_pre = 0

    def compute_step(self, force_at_wheel, road_load, v_cyc):
        # self.v_cyc = v_cyc
        self.acceleration = (force_at_wheel - self.aero_drag) / self.mass
        self.velocity = self.velocity + self.acceleration * self.delta_t

        if self.velocity < 0:
            self.velocity = 0

        self.velocity = self.speed_integrator(self.delta_t, self.acceleration, self.velocity_pre, v_cyc)
        self.velocity_pre = self.velocity

        self.aero_drag = self.compute_areo_drag(self.velocity)
        self.position = self.position + self.velocity * self.delta_t

        return {
            "acceleration": self.acceleration,
            "velocity": self.velocity,
            "position": self.position
        }

    def compute_areo_drag(self, velocity):
        return np.power(velocity, 2) * 0.5 * self.density_air * self.c_drag * self.frontal_area

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