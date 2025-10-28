from dataclasses import dataclass
class ReactorParams:
# Bodová kinetika s jednou zpožděnou skupinou
beta: float = 0.0065 # efektivní podíl zpožděných neutronů
Lambda: float = 1e-4 # generační doba [s]
lambda_d: float = 0.08 # rozpad prekurzorů [1/s]
alpha_T: float = -3.0e-5 # teplotní koeficient reaktivity [1/K]
k_heat: float = 0.9 # převod výkon -> ohřev paliva
h_cool: float = 0.25 # odvod tepla do chladiva
T_cool_in: float = 560.0 # vstupní teplota chladiva [K]
rho_rod_max: float = 0.01 # max "+" reaktivita při úplném vysunutí
scram_rho: float = -0.03 # reaktivita při SCRAM


@dataclass
class ReactorState:
P: float = 1.0 # relativní výkon
C: float = 0.08125 # prekurzory
T_fuel: float = 600.0 # teplota paliva [K]
rod_pos: float = 0.5 # 0..1 (0 plně zasunuto, 1 plně vytaženo)
coolant_flow: float = 1.0 # 0..2 relativní průtok
scrammed: bool = False


class Reactor:
def __init__(self, params: ReactorParams | None = None):
self.p = params or ReactorParams()
self.s = ReactorState()
# odvoď C pro stacionární stav při P=1: C = beta/(Lambda*lambda_d)
self.s.C = self.p.beta / (self.p.Lambda * self.p.lambda_d)


def reactivity(self) -> float:
if self.s.scrammed:
return self.p.scram_rho
rho_rods = (self.s.rod_pos - 0.5) * 2 * self.p.rho_rod_max # -max..+max
rho_temp = self.p.alpha_T * (self.s.T_fuel - 600.0)
return rho_rods + rho_temp


def step(self, dt: float):
# jednoduchá ODE integrace (Euler)
rho = self.reactivity()
dP = ((rho - self.p.beta) / self.p.Lambda) * self.s.P + self.p.lambda_d * self.s.C
dC = (self.p.beta / self.p.Lambda) * self.s.P - self.p.lambda_d * self.s.C
# Teplo paliva
T_cool = self.p.T_cool_in + 15.0 / max(1e-3, self.s.coolant_flow)
dT = self.p.k_heat * self.s.P - self.p.h_cool * (self.s.T_fuel - T_cool) * self.s.coolant_flow


self.s.P = max(0.0, self.s.P + dP * dt)
self.s.C = max(0.0, self.s.C + dC * dt)
self.s.T_fuel = max(273.0, self.s.T_fuel + dT * dt)


# ovládání
def set_rod_pos(self, pos: float):
self.s.rod_pos = min(1.0, max(0.0, pos))


def set_flow(self, flow: float):
self.s.coolant_flow = min(2.0, max(0.0, flow))


def scram(self):
self.s.scrammed = True


def reset(self):
self.__init__(self.p)


def export(self) -> dict:
return {
"P": self.s.P,
"C": self.s.C,
"T_fuel": self.s.T_fuel,
"rod_pos": self.s.rod_pos,
"coolant_flow": self.s.coolant_flow,
"rho": self.reactivity(),
"scrammed": self.s.scrammed,
}
