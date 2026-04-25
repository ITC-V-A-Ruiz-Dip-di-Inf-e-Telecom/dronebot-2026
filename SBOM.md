# SBOM — Software Bill of Materials

Lista completa delle librerie e dipendenze software utilizzate nel progetto Dronebot 2026 — Team Holly.

---

## PC — Script di Rilevamento

Gestito con **Pixi** (conda-forge + pip). File di riferimento: `pc/pixi.toml`.

| Pacchetto | Versione | Uso |
|-----------|----------|-----|
| Python | 3.12.x | Linguaggio base |
| ultralytics | >= 8.0.0 | YOLOv8 — rilevamento fuoco in tempo reale |
| opencv | >= 4.10.0 | Acquisizione video, rilevamento ArUco, rendering |
| pytorch | >= 2.0.0 | Backend inferenza neurale (+ CUDA 12.1) |
| torchvision | >= 0.15.0 | Trasformazioni immagine per YOLOv8 |
| numpy | >= 1.24 | Calcoli geometrici (cerchio di fuoco, distanze) |
| requests | (via pip) | HTTP POST verso il server Flask del rover |
| rich | >= 13.0.0 | Output console formattato |
| python-dotenv | >= 1.0.0 | Gestione variabili d'ambiente |
| v4l2loopback | kernel module | Webcam virtuale `/dev/video10` |
| scrcpy | sistema (apt/pacman) | Streaming schermo Android verso v4l2 |
| ffmpeg | sistema | Server RTMP per streaming da DJI FLY |
| adb | sistema | Android Debug Bridge |

---

## Rover — Raspberry Pi 5

Sistema Operativo: **Raspberry Pi OS Lite 64-bit**.
Gestito con **Python venv**. Avvio automatico tramite systemd (`holly_rover.service`).

### Pacchetti di Sistema (apt)

| Pacchetto | Uso |
|-----------|-----|
| python3-pip | Gestore pacchetti Python |
| i2c-tools | Diagnostica bus I2C (`i2cdetect`) |
| git | Version control |
| libcamera-dev | Librerie fotocamera Raspberry Pi |

### Librerie Python (pip / venv)

| Pacchetto | Versione | Uso |
|-----------|----------|-----|
| Python | 3.11+ | Linguaggio base |
| Flask | >= 2.x | Dashboard web, API REST (`/start`, `/stop`, `/telemetria`) |
| pyserial | >= 3.x | Comunicazione seriale UART con Arduino Mega |
| opencv-headless | >= 4.x | Elaborazione frame MJPEG, threshold, findContours |
| numpy | >= 1.24 | Calcoli LiDAR (media punti, ricerca varchi) |
| ydlidar | Python SDK | Interfaccia YDLiDAR X4 Pro su `/dev/ttyUSB0` |
| adafruit-ads1x15 | >= 2.x | Driver ADS1115 16-bit ADC via I2C |
| adafruit-blinka | >= 8.x | HAL hardware Adafruit per Raspberry Pi |

### Tool di Sistema

| Tool | Uso |
|------|-----|
| rpicam-vid | Acquisizione MJPEG dalla Pi Camera 3 NoIR Wide |
| systemd | Avvio automatico al boot (`holly_rover.service`) |

---

## Rover — Arduino Mega Keyestudio

Firmware: `rover/arduino/holly_mega_v12.11.ino`
IDE: **Arduino IDE** (versione 2.x).
Librerie installate tramite Arduino IDE Library Manager:

| Libreria | Versione | Autore | Uso |
|----------|----------|--------|-----|
| Wire | built-in | Arduino | Bus I2C per comunicazione con i 4 sensori ToF VL53L0X |
| VL53L0X | >= 1.3.x | Pololu | Driver sensori Time-of-Flight — distanze in mm |
