from flask import Flask, render_template_string, jsonify
import serial
import threading
import time

app = Flask(__name__)

# Configurazione Seriale verso Arduino Mega
try:
    ser = serial.Serial('/dev/serial0', 115200, timeout=1)
    ser.flush()
except:
    print("Errore: Impossibile aprire la porta seriale.")

# Variabili globali per la telemetria
distanza_frontale = 0
running = True

# Thread per la lettura dei dati da Arduino
def read_telemetry():
    global distanza_frontale
    while running:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith("DATA:"):
                    # Estrae il valore dopo "DATA:"
                    distanza_frontale = int(line.split(":")[1])
            except:
                pass
        time.sleep(0.01)

# Avvio del Thread
t = threading.Thread(target=read_telemetry, daemon=True)
t.start()

# Interfaccia Dashboard Semplice
HTML_UI = """
<!DOCTYPE html>
<html>
<head>
    <title>Holly Milestone 2</title>
    <style>
        body { font-family: Arial; text-align: center; background: #222; color: white; }
        .btn { padding: 20px; font-size: 18px; margin: 10px; width: 100px; cursor: pointer; }
        #data { font-size: 24px; color: #ffc107; }
    </style>
</head>
<body>
    <h1>HOLLY CONTROL - MILESTONE 2</h1>
    <div id="data">Distanza Frontale: <span id="dist">0</span> mm</div>
    <br>
    <button class="btn" onclick="cmd('W')">AVANTI</button><br>
    <button class="btn" onclick="cmd('A')">SX</button>
    <button class="btn" onclick="cmd('X')">STOP</button>
    <button class="btn" onclick="cmd('D')">DX</button><br>
    <button class="btn" onclick="cmd('S')">DIETRO</button>

    <script>
        function cmd(v) { fetch('/control/' + v); }
        setInterval(() => {
            fetch('/get_data').then(r => r.json()).then(d => {
                document.getElementById('dist').innerText = d.dist;
            });
        }, 200);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_UI)

@app.route('/control/<v>')
def control(v):
    ser.write(v.encode())
    return "OK"

@app.route('/get_data')
def get_data():
    return jsonify({"dist": distanza_frontale})

if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    finally:
        running = False
        ser.close()