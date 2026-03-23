from flask import Flask, render_template_string
import serial

app = Flask(__name__)
ser = serial.Serial('/dev/serial0', 115200)

HTML = """
<button onclick="fetch('/W')">AVANTI</button>
<button onclick="fetch('/S')">INDIETRO</button>
<button onclick="fetch('/X')">STOP</button>
<script>function fetch(url){ navigator.sendBeacon(url); }</script>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/<cmd>')
def move(cmd):
    ser.write(cmd.encode())
    return "OK"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)