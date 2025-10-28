class PID:
    def __init__(self, kp=0.5, ki=0.05, kd=0.02, out_min=0.0, out_max=1.0):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.out_min, self.out_max = out_min, out_max
        self.i = 0.0
        self.prev_e = 0.0


    def step(self, sp, pv, dt):
        e = sp - pv
        self.i += e * dt
        d = (e - self.prev_e) / dt if dt > 0 else 0.0
        u = self.kp * e + self.ki * self.i + self.kd * d
        self.prev_e = e
        return max(self.out_min, min(self.out_max, u))
