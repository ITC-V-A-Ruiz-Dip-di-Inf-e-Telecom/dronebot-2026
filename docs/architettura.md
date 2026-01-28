# Architettura (bozza)

## Componenti
- PC (video drone + detection target + validazione arrivo)
- Rover: Raspberry Pi (vision + LiDAR + controller)
- Rover: Arduino (motori + safety)

## Interfacce
- Raspberry ↔ Arduino: USB Serial (comandi v/w + watchdog)
- Raspberry: Camera rover (tracking drone beacon)
- Raspberry: YDLIDAR X4 Pro (scansione 2D 360°)
