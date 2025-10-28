import time


class SimLoop:
def __init__(self, socketio):
self.socketio = socketio
self.reactor = Reactor()
self.dt = 0.1 # s
self.running = False
# regulátory
self.power_sp = 1.0
self.power_pid = PID(kp=0.3, ki=0.02, kd=0.05, out_min=0.0, out_max=1.0)
self.flow_sp = 1.0
self.flow_pid = PID(kp=0.6, ki=0.05, kd=0.02, out_min=0.2, out_max=1.6)


def thread_fn(self):
last = time.perf_counter()
while self.running:
now = time.perf_counter()
dt = min(0.25, now - last)
last = now
# řízení
rod_cmd = self.power_pid.step(self.power_sp, self.reactor.s.P, dt)
flow_cmd = self.flow_pid.step(self.flow_sp, self.reactor.s.coolant_flow, dt)
self.reactor.set_rod_pos(rod_cmd)
self.reactor.set_flow(flow_cmd)
# simulace
self.reactor.step(self.dt)
# broadcast
self.socketio.emit("state", self.export_state())
time.sleep(self.dt)


def start(self):
if self.running:
return
self.running = True
threading.Thread(target=self.thread_fn, daemon=True).start()


def stop(self):
self.running = False


def export_state(self):
st = self.reactor.export()
st.update({
"power_sp": self.power_sp,
"flow_sp": self.flow_sp,
})
return st


# příkazy z UI
def handle_command(self, cmd: str, **args):
try:
if cmd == "set_power_sp":
self.power_sp = max(0.0, float(args.get("value", 1.0)))
elif cmd == "set_flow_sp":
self.flow_sp = max(0.1, float(args.get("value", 1.0)))
elif cmd == "scram":
self.reactor.scram()
elif cmd == "reset":
self.reactor.reset()
self.power_pid = PID()
self.flow_pid = PID(out_min=0.2, out_max=1.6)
else:
return False, f"unknown cmd: {cmd}"
return True, "ok"
except Exception as e:
return False, str(e)
