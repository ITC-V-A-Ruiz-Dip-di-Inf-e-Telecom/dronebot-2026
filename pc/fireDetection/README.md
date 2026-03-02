<div align="center">
  <h1>Fire Detection 🔥</h1>
  
  Rilevamento in tempo reale di target "fuoco" utilizzando YOLO e streaming della fotocamera dello smartphone Android.
</div>

---

## Confronto Metodi di Acquisizione ⚡

Questo progetto supporta due metodi per catturare i frame dal tuo dispositivo Android:

### 1. ADB Screencap (`adb_capture.py`)
- **FPS**: 0.2 - 0.4 frame al secondo
- **Metodo**: Utilizza `adb exec-out screencap -p` per catturare screenshot
- **Pro**: Semplice, nessuna configurazione aggiuntiva richiesta
- **Contro**: Molto lento, overhead di subprocess per ogni frame
- **Caso d'uso**: Test o quando la configurazione della webcam virtuale non è disponibile

### 2. Webcam Virtuale via scrcpy (Consigliato) 🚀
- **FPS**: 30-40 frame al secondo (con accelerazione GPU)
- **Metodo**: Utilizza scrcpy per trasmettere lo schermo del telefono a un dispositivo virtuale v4l2loopback
- **Pro**: 25-50x più veloce della cattura ADB, rilevamento in tempo reale con GPU
- **Contro**: Richiede la configurazione del modulo kernel v4l2loopback
- **Caso d'uso**: Uso in produzione, rilevamento fuoco in tempo reale

> [!IMPORTANT]
> Il metodo webcam virtuale con accelerazione GPU fornisce prestazioni **2-3x migliori** rispetto alla sola CPU,
> e **25-50x volte più veloce rispetto alla cattura ADB** rendendolo l'unica opzione praticabile per il rilevamento fuoco in tempo reale.
> Vedi [Configurazione GPU](#2-installazione-dipendenze-con-supporto-gpu) per abilitare l'accelerazione CUDA.

---

## Installazione

### Prerequisiti

- **Pixi** (Package manager) - Scarica da [qui](https://pixi.prefix.dev/latest/)
- **scrcpy** - Installa tramite il tuo package manager (`apt install scrcpy`, `pacman -S scrcpy`, ecc.)
- **adb** (Android Debug Bridge) - Solitamente incluso con scrcpy, o installa tramite package manager
- **modulo kernel v4l2loopback** (per webcam virtuale)
- **Dispositivo Android** con debug USB abilitato

### Passaggi di Installazione

#### 1. Clona il Repository
```bash
git clone https://github.com/Ra77a3l3-jar/fireDetection.git
cd fireDetection
```

#### 2. Installazione Dipendenze con Supporto GPU

Esegui lo script di configurazione automatico:
```bash
./setup.sh
```

Questo script:
- Installerà tutte le dipendenze pixi
- Disinstallerà PyTorch solo CPU
- Installerà PyTorch con supporto CUDA 12.1 per l'accelerazione GPU
- Verificherà che CUDA funzioni e mostrerà le informazioni della GPU

**Installazione Manuale (se lo script di configurazione fallisce):**
```bash
# Installa dipendenze pixi
pixi install

# Rimuovi PyTorch solo CPU e installa la versione CUDA
pixi run pip uninstall torch torchvision -y
pixi run pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# Installa dipendenze mancanti
pixi run pip install ultralytics-thop
```

> [!NOTE]
> L'accelerazione GPU fornisce prestazioni 2-3x più veloci rispetto alla modalità solo CPU.
> Lo script di configurazione assicura che PyTorch sia installato con il supporto CUDA.

#### 3. Configurazione Webcam Virtuale

> [!NOTE]
> Puoi creare la webcam virtuale su qualsiasi numero `/dev/videoX`. Scelte comuni sono
> `/dev/video10` (se hai già una webcam esistente su `/dev/video0`) o `/dev/video0` (se non hai una webcam fisica).

Carica il modulo kernel v4l2loopback:
```bash
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1
```

**Parametri spiegati:**
- `devices=1` - Crea 1 dispositivo camera virtuale
- `video_nr=10` - Crea il dispositivo su `/dev/video10` (può essere qualsiasi numero, es. 0, 2, 10, 20, ecc.)
- `card_label="PhoneCam"` - Nome descrittivo per il dispositivo
- `exclusive_caps=1` - Richiesto per la compatibilità con alcune applicazioni

#### 4. Collega il tuo Dispositivo Android

1. Abilita il Debug USB sul tuo dispositivo Android
2. Collega tramite cavo USB
3. Verifica la connessione: `adb devices`

#### 5. Avvia lo Streaming della Fotocamera

**Se usi `/dev/video10`:**
```bash
scrcpy --v4l2-sink=/dev/video10 --no-playback
```

**Se usi `/dev/video0` (o qualsiasi altro dispositivo video):**
```bash
scrcpy --v4l2-sink=/dev/video0 --no-playback
```

**Flag spiegati:**
- `--v4l2-sink=/dev/videoX` - Output verso il dispositivo video specificato
- `--no-playback` - Esegue senza aprire una finestra di visualizzazione (modalità headless)

---

## Utilizzo 🚀

### Esecuzione del Rilevatore

#### 1. Assicurati che la webcam virtuale sia in esecuzione:
```bash
scrcpy --v4l2-sink=/dev/video10 --no-playback
```

#### 2. Aggiorna il dispositivo video in `src/main.py:19` se necessario:
```python
# Se usi /dev/video10 (predefinito)
cap = cv2.VideoCapture("/dev/video10")

# OPPURE se usi /dev/video0 o qualsiasi altro dispositivo
cap = cv2.VideoCapture("/dev/video0")
```

#### 3. Esegui il rilevatore di fuoco:
```bash
pixi run python src/main.py
```

> [!WARNING]
> Assicurati di avviare scrcpy **prima** di eseguire il rilevatore,
> altrimenti OpenCV non riuscirà ad aprire il dispositivo video.

### Output

- **Feed Video Live**: Visualizzazione in tempo reale dello stream della fotocamera
- **Box di Rilevamento**: Rettangoli di selezione disegnati attorno ai fuochi rilevati
- **Contatore FPS**: Frame al secondo correnti e rilevamenti totali
- **Avvisi Fuoco**: Overlay "FIRE DETECTED" quando il fuoco è confermato
- **Cattura Evidenze**: Salvataggio automatico degli screenshot nella directory `evidence/`

### Controlli

- **ESC**: Esci dall'applicazione

---

## Configurazione ⚙️

### Regolare la Sensibilità di Rilevamento

In `src/main.py:22`, modifica il parametro `confirm_frames`:
```python
# Più sensibile (avvisi più veloci, più falsi positivi)
controller = DetectionController(confirm_frames=1)

# Predefinito (bilanciato)
controller = DetectionController(confirm_frames=3)

# Più conservativo (avvisi più lenti, meno falsi positivi)
controller = DetectionController(confirm_frames=5)
```

> [!TIP]
> Inizia con `confirm_frames=3` e regola in base al tuo ambiente.
> Valori più alti riducono i falsi positivi ma possono ritardare gli avvisi.

### Cambiare Dispositivo Video

In `src/main.py:19`, aggiorna il percorso del dispositivo video:
```python
cap = cv2.VideoCapture("/dev/video10")  # oppure /dev/video0, /dev/video2, ecc.
```

### Dimensioni Finestra di Visualizzazione

In `src/main.py:25-26`, regola le dimensioni della finestra:
```python
cv2.namedWindow("Fire Detector", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Fire Detector", 900, 600)  # larghezza, altezza
```

---

## Risoluzione Problemi 🔧

### Problemi GPU / CUDA

**Problema**: L'UI mostra `[CPU]` invece di `[GPU]` o prestazioni lente

Il PyTorch predefinito da conda-forge è solo CPU. Devi installare la versione CUDA:

```bash
# Esegui lo script di configurazione
./setup.sh

# Oppure installa manualmente PyTorch CUDA
pixi run pip uninstall torch torchvision -y
pixi run pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

**Verifica che CUDA funzioni:**
```bash
pixi run python -c "import torch; print(f'CUDA disponibile: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"
```

Output atteso:
```
CUDA disponibile: True
GPU: NVIDIA GeForce RTX 3060 Laptop GPU
```

### Problemi Webcam Virtuale

**Problema**: `/dev/video10` non trovato o camera virtuale non creata

```bash
# Controlla i dispositivi video esistenti
ls -l /dev/video*

# Controlla se v4l2loopback è caricato
lsmod | grep v4l2loopback

# Se non è caricato, caricalo
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1

# Verifica che il dispositivo sia stato creato
ls -l /dev/video*
```

**Problema**: Il dispositivo camera virtuale esiste già ma non funziona

```bash
# Scarica e ricarica il modulo
sudo rmmod v4l2loopback
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1

# Controlla se qualche processo sta usando il dispositivo
sudo fuser /dev/video10

# Aggiungi il tuo utente al gruppo video (se ci sono problemi di permessi)
sudo usermod -aG video $USER
# Disconnettiti e riconnettiti affinché abbia effetto
```

**Problema**: Modulo v4l2loopback non disponibile (Fedora/RHEL)

Su Fedora 43 e distribuzioni simili, hai bisogno dei repository RPM Fusion:

```bash
# Installa repository RPM Fusion
sudo dnf install https://mirrors.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm

# Installa v4l2loopback
sudo dnf install v4l2loopback akmod-v4l2loopback

# Costruisci i moduli kernel
sudo akmods --force

# Aggiorna le dipendenze dei moduli
sudo depmod -a

# Disconnettiti e riconnettiti
sudo reboot

# Carica il modulo
sudo modprobe v4l2loopback devices=1 video_nr=10 card_label="PhoneCam" exclusive_caps=1
```

**Problema**: Il modulo si carica ma la camera non funziona ancora

```bash
# Controlla i log del kernel per errori
dmesg | grep v4l2loopback

# Prova un numero diverso di dispositivo video (es. video0, video2, video20)
sudo rmmod v4l2loopback
sudo modprobe v4l2loopback devices=1 video_nr=0 card_label="PhoneCam" exclusive_caps=1

# Aggiorna main.py per corrispondere al nuovo numero del dispositivo
# Modifica linea 19: cap = cv2.VideoCapture("/dev/video0")
```

**Problema**: Connessione scrcpy fallisce
```bash
# Controlla connessione ADB
adb devices

# Riavvia server ADB
adb kill-server
adb start-server
```

### Problemi di Prestazioni

**Prestazioni Attese:**
- **Solo CPU**: 10-20 FPS
- **GPU (CUDA)**: 30-40 FPS

**Problema**: FPS bassi anche con GPU

Assicurati di usare il metodo webcam virtuale (`scrcpy`), non `adb_capture.py`.

**Problema**: Lag scrcpy o FPS bassi

Prova a ridurre la risoluzione dello schermo del telefono o il bitrate:
```bash
scrcpy --v4l2-sink=/dev/video10 --no-playback --max-size=1024 --bit-rate=2M
```

---

## Struttura del Progetto 📂

```
fireDetection/
├── src/
│   ├── main.py                      # Entry point e loop principale
│   ├── capture/
│   │   └── adb_capture.py          # Cattura ADB screencap (metodo lento)
│   ├── detection/
│   │   └── yolo_detector.py        # Logica rilevamento fuoco YOLO
│   ├── logic/
│   │   └── controller.py           # Controller conferma rilevamento
│   ├── ui/
│   │   └── render.py               # Rendering e visualizzazione
│   └── utils/
│       └── evidence_saver.py       # Utility salvataggio screenshot
├── evidence/                        # Screenshot auto-generati rilevamenti fuoco
├── pixi.toml                        # Dipendenze Pixi
└── README.md
```

---

## Licenza 📄

MIT License - Copyright (c) 2026 Raffaele Meo

Vedi [LICENSE](LICENSE) per i dettagli completi.
