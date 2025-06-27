
import os
import sys
import time
import threading

import subprocess
try:
    import clr
except ModuleNotFoundError:
    print("pythonnet not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pythonnet"])
    import clr


subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "flask"])


# === Load .NET DLL ===
dll_name = "OstatFeedHandlerFramework48.dll"
dll_path = os.path.join(os.getcwd(), dll_name)

if not os.path.exists(dll_path):
    print(f"ERROR: DLL not found at {dll_path}")
    sys.exit(1)

sys.path.append(os.getcwd())
clr.AddReference(dll_path)

from OstatFeedHandlerFramework48 import OstatPythonBridge



from flask import Flask, request, jsonify
import threading

from datetime import datetime, time as dtime


bridge = None
# --- Background thread to start bridge at 9:30 ---
def init_at_930():
    global bridge
    while True:
        now = datetime.now().time()
        if now >= dtime(9, 30):
            print("[Init] Time reached 09:30. Initializing bridge...")
            bridge = OstatPythonBridge()
            bridge.StartListening()
            break
        time.sleep(10)

threading.Thread(target=init_at_930, daemon=True).start()

# --- Flask setup ---
app = Flask(__name__)

@app.route('/order_exists', methods=['POST'])
def order_exists():
    data = request.get_json()
    symbol = data.get("symbol")
    side = data.get("side")
    price = data.get("price")
    if not all([symbol, side, price]):
        return jsonify({"error": "Missing parameters"}), 400

    try:
        exists = bridge.OrderExists(symbol, side, price)
    except:
        exists = False
    return jsonify({"exists": exists})

@app.route('/traded_volume', methods=['GET'])
def traded_volume():
    symbol = request.args.get("symbol")
    if not symbol:
        return jsonify({"error": "Missing symbol"}), 400

    try:
        volume = bridge.GetTradedVolume(symbol)
    except:
        volume =0
    return jsonify({"volume": volume})

if __name__ == '__main__':
    app.run(port=8000)