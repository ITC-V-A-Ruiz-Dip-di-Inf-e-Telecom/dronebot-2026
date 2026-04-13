# Changelog — DroneBot 2026

Il progetto segue un'evoluzione per versioni successive. Ogni versione rilevante sarà taggata e, quando utile, pubblicata come Release.

## [2.0] — 2026-04-13

### Added
- Integrazione sensore ToF VL53L0X frontale per rilevamento ostacoli
- Sistema di telemetria: trasmissione distanza frontale al Raspberry Pi in tempo reale
- Dashboard di controllo aggiornata con indicatore distanza
- Logica di sicurezza (veto): blocco automatico avanzamento se ostacolo < 20 cm
- Script PC per rilevamento fuoco tramite YOLO e marker ArUco

### Fixed
- Gestione errori apertura porta seriale nel software Raspberry Pi

## [1.0] — 2026-03-23

### Added
- Prima versione firmware Arduino Mega per controllo motori tramite driver L298N
- Ricezione comandi di movimento (W/A/S/D/X) via porta seriale dal Raspberry Pi
- Prima versione software controllo Raspberry Pi con server web Flask
- Interfaccia HTML con bottoni per invio comandi di movimento al rover

## [0.0] — Creazione account Organization e Setup repository
- Creata repository e struttura cartelle iniziale.
- Aggiunti README, changelog e decision log.
- Definite regole d'oro per alimentazione e affidabilità.
