import serial, threading, time, sys, cv2, numpy as np, subprocess, shlex, os, ydlidar
from flask import Flask, request, jsonify, Response, render_template_string
import board, busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# --- CONFIGURAZIONE FLASK ---
app = Flask(__name__)
os.system("sudo pkill rpicam-vid > /dev/null 2>&1")

# --- STATI E VARIABILI GLOBALI ---
running = True
stato_gara = "ATTESA"
comando_led = "X"
punti_lidar = [5000] * 360
tof_f, tof_l, tof_r, tof_b = 0, 0, 0, 0
b_sx, b_dx = 0, 0
v_batteria_totale = 0.0
v_su_a0 = 0.0
ser = serial.Serial('/dev/serial0', 115200, timeout=0.05)
ultimo_frame_jpg = None
frame_lock = threading.Lock()

# --- INTERFACCIA HTML (Identica alla 13.5) ---
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Holly Control Center</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; text-align: center; background: #1a1a1a; color: white; padding: 10px; }
        .btn { padding: 20px 40px; font-size: 20px; margin: 10px; cursor: pointer; border: none; border-radius: 8px; font-weight: bold; }
        .start { background: #28a745; color: white; }
        .stop { background: #dc3545; color: white; }
        #video { width: 100%; max-width: 640px; border: 3px solid #444; border-radius: 10px; }
        .status-bar { background: #333; padding: 15px; margin-bottom: 20px; font-size: 1.2em; border-radius: 5px; }
        .val { color: #ffc107; font-weight: bold; }
    </style>
</head>
<body>
    <div class="status-bar">
        STATO: <span id="stato_txt" class="val">ATTESA</span> |
        BATT TOTALE: <span id="batt_txt" class="val">0.0V</span>
    </div>
    <button class="btn start" onclick="manda('start')">START RACE</button>
    <button class="btn stop" onclick="manda('stop')">EMERGENCY STOP</button>
    <br><br>
    <img id="video" src="/video_feed">
    <script>
        function manda(azione) {
            fetch('/' + azione, { method: 'POST' })
            .then(r => r.json())
            .then(d => document.getElementById('stato_txt').innerText = d.message.toUpperCase());
        }
        setInterval(() => {
            fetch('/telemetria').then(r => r.json()).then(d => {
                document.getElementById('batt_txt').innerText = d.batt_tot;
                document.getElementById('stato_txt').innerText = d.stato;
            });
        }, 2000);
    </script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML_PAGE)

@app.route('/start', methods=['POST'])
def start_gara():
    global stato_gara
    stato_gara = "IN_MARCIA"
    return jsonify({"status": "ok", "message": "IN_MARCIA"})

@app.route('/stop', methods=['POST'])
def stop_gara():
    global stato_gara
    stato_gara = "ATTESA"
    return jsonify({"status": "ok", "message": "ATTESA"})

@app.route('/telemetria', methods=['GET'])
def get_telemetria():
    return jsonify({
        "stato": stato_gara,
        "v_a0": f"{v_su_a0:.3f}V",
        "batt_tot": f"{v_batteria_totale:.2f}V",
        "tof": {"F": tof_f, "L": tof_l, "R": tof_r, "B": tof_b},
        "bump": {"SX": b_sx, "DX": b_dx},
        "cmd": comando_led
    })

def gen_frames():
    global ultimo_frame_jpg
    while running:
        with frame_lock:
            if ultimo_frame_jpg is None: continue
            frame = ultimo_frame_jpg
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        time.sleep(0.05)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def ads_thread():
    global v_batteria_totale, v_su_a0, running
    try:
        i2c = busio.I2C(board.SCL, board.SDA); ads = ADS.ADS1115(i2c); chan = AnalogIn(ads, 0)
        while running:
            v_su_a0 = chan.voltage
            v_batteria_totale = v_su_a0 * 3.082
            time.sleep(1.0)
    except Exception as e: print(f"\n[ERRORE ADS]: {e}")

def listener():
    global tof_f, tof_l, tof_r, tof_b, b_sx, b_dx, running
    while running:
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if "DATA:" in line:
                    p = line.replace("DATA:", "").split(",")
                    if len(p) >= 6:
                        tof_f, tof_l, tof_r, tof_b = int(p[0]), int(p[1]), int(p[2]), int(p[3])
                        b_sx, b_dx = int(p[4]), int(p[5])
            except: pass
        time.sleep(0.01)

def lidar_thread():
    global punti_lidar, running
    laser = ydlidar.CYdLidar()
    laser.setlidaropt(ydlidar.LidarPropSerialPort, "/dev/ttyUSB0")
    laser.setlidaropt(ydlidar.LidarPropSerialBaudrate, 128000)
    if laser.initialize() and laser.turnOn():
        scan = ydlidar.LaserScan()
        while running:
            if laser.doProcessSimple(scan):
                for p in scan.points:
                    ang = int(np.degrees(p.angle)) % 360
                    punti_lidar[ang] = p.range * 1000
            time.sleep(0.05)

def vision_logic():
    global comando_led, ultimo_frame_jpg, running
    cmd_video = "rpicam-vid -t 0 --shutter 2000 --gain 1 --width 640 --height 480 -n --codec mjpeg -o -"
    proc = subprocess.Popen(shlex.split(cmd_video), stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    bytes_buffer = b""
    try:
        while running:
            bytes_buffer += proc.stdout.read(4096)
            a, b = bytes_buffer.find(b'\xff\xd8'), bytes_buffer.find(b'\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes_buffer[a:b+2]; bytes_buffer = bytes_buffer[b+2:]
                with frame_lock: ultimo_frame_jpg = jpg
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                if frame is not None:
                    _, maschera = cv2.threshold(frame, 248, 255, cv2.THRESH_BINARY)
                    cnts, _ = cv2.findContours(maschera, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    if cnts:
                        c = max(cnts, key=cv2.contourArea)
                        if 15 < cv2.contourArea(c) < 2000:
                            M = cv2.moments(c); posX = int(M["m10"] / M["m00"])
                            # --- NUOVE ZONE 13.7 (CENTRO PIU LARGO) ---
                            if posX < 200: comando_led = "A"
                            elif posX > 440: comando_led = "D"
                            else: comando_led = "W"
                        else: comando_led = "X"
                    else: comando_led = "X"
    finally: proc.terminate()

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# --- AVVIO SISTEMA ---
threading.Thread(target=listener, daemon=True).start()
threading.Thread(target=vision_logic, daemon=True).start()
threading.Thread(target=lidar_thread, daemon=True).start()
threading.Thread(target=ads_thread, daemon=True).start()
threading.Thread(target=run_flask, daemon=True).start()

timer_recupero = 0
last_side_hit = ""

try:
    print("\n" + "="*50)
    print("      HOLLY V13.9 - BASE 13.5 STABLE + LOGICA 13.7")
    print("="*50)
    while True:
        # 1. LOGICA SASSO (Se perde LED o ATTESA -> STOP)
        if stato_gara == "ATTESA" or comando_led == "X":
            cmd_finale = "X"
            # Recupero fisico (Baffetti)
            if b_dx or b_sx or timer_recupero > 0:
                if b_sx: (timer_recupero, last_side_hit) = (6, "SX")
                if b_dx: (timer_recupero, last_side_hit) = (6, "DX")
                cmd_finale = "Q" if last_side_hit == "SX" else "E"
                timer_recupero -= 1
        else:
            # Siamo in marcia e il LED è visibile
            cmd_finale = comando_led
            dist_f_lidar = np.mean(punti_lidar[175:185])

            # A. Stop Emergenza ToF Frontale (10cm)
            if (0 < tof_f < 100):
                cmd_finale = "X"

            # B. ToF NUDGE (Correzione attiva laterale)
            elif comando_led == "W":
                if (0 < tof_l < 150): cmd_finale = "D"
                elif (0 < tof_r < 150): cmd_finale = "A"

            # C. Aggiramento Lidar (30cm) e Varco (35cm)
            if cmd_finale == "W" and (dist_f_lidar < 300):
                varchi = [ang for ang in range(130, 230) if punti_lidar[ang] > 350]
                if varchi:
                    miglior = min(varchi, key=lambda x: abs(x - 180))
                    cmd_finale = "A" if miglior > 180 else "D"
                else: cmd_finale = "S"

        ser.write(cmd_finale.encode())
        sys.stdout.write(
            f"\r[BATT: {v_batteria_totale:4.2f}V] | TOF L:{tof_l:4} R:{tof_r:4} | CMD:{cmd_finale} | LED:{comando_led} | {stato_gara:9}"
        )
        sys.stdout.flush()
        time.sleep(0.05)

except KeyboardInterrupt: pass
finally:
    running = False; ser.write(b'X'); time.sleep(0.2); ser.close()
    print("\n[INFO] Sistema arrestato correttamente."); sys.exit(0)

