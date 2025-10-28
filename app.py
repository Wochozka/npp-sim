from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from sim.loop import SimLoop


app = Flask(__name__)
socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")


# Globální simulační smyčka
sim_loop = SimLoop(socketio)


@app.route("/")
def index():
return render_template("index.html")


@app.route("/api/state")
def api_state():
return jsonify(sim_loop.export_state())


@app.post("/api/command")
def api_command():
data = request.get_json(force=True)
cmd = data.get("cmd")
args = data.get("args", {})
ok, msg = sim_loop.handle_command(cmd, **args)
return jsonify({"ok": ok, "msg": msg, "state": sim_loop.export_state()})


if __name__ == "__main__":
sim_loop.start()
socketio.run(app, host="0.0.0.0", port=5000)
