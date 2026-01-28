# dronebot-2026
# DroneBot 2026 — ITC/VA Ruiz (Corso di Robotica)

Repository ufficiale del progetto per la competizione DroneBot 2026.
L’obiettivo è sviluppare un sistema integrato **drone + rover** in grado di:
1) individuare il target “fuoco” (immagine a terra),
2) guidare il rover fino a entrare **completamente** nel cerchio del target,
3) gestire ostacoli e condizioni reali di gara in modo affidabile.

## Filosofia di progetto
- **Sviluppo iterativo**: il progetto evolve per versioni successive (tag e release).
- **Tracciabilità**: decisioni tecniche motivate e registrate in `docs/decision-log.md`.
- **Affidabilità prima della complessità**: preferiamo soluzioni semplici e robuste, poi ottimizziamo.

## Architettura (high level)
- **PC (laptop)**: acquisizione video dal drone, riconoscimento target “fuoco + cerchio”, strumenti di debug/overlay, validazione “rover dentro il cerchio”.
- **Rover — Raspberry Pi 4/5**: visione per tracking del drone (beacon) + lettura LiDAR 2D (YDLIDAR X4 Pro) per evitamento ostacoli.
- **Rover — Arduino (UNO/MEGA)**: controllo motori (Motor Shield R3 L298P), safety real-time (watchdog, stop di emergenza), sensori di prossimità (es. VL53L0X).

## Struttura repository
- `pc/` — software lato PC (video drone, detection target, strumenti di gara)
- `rover/raspberry/` — software lato rover su Raspberry (vision + LiDAR + controller)
- `rover/arduino/` — firmware lato rover su Arduino (motori + safety)
- `docs/` — documentazione, decisioni, test, organizzazione team
- `media/` — foto/video/test evidence

## Come contribuiamo
- Tutte le modifiche passano da commit con messaggi chiari (`feat:`, `fix:`, `docs:`).
- Ogni milestone genera un **tag** e, quando opportuno, una **release** con note.

## Stato del progetto
Vedi `CHANGELOG.md` per la cronologia delle versioni e `docs/decision-log.md` per le decisioni tecniche.

---
**Licenza**: TBD (da definire)

