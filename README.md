# Rilevamento Gesti della Mano con MediaPipe e ESP32

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Framework: MediaPipe](https://img.shields.io/badge/Framework-MediaPipe-green.svg)](https://mediapipe.dev/)

Un sistema completo per il rilevamento di gesti in tempo reale che utilizza modelli pre-addestrati di Google MediaPipe e si integra con hardware ESP32 per notifiche istantanee.

## Descrizione del Progetto

Questo progetto implementa un sistema per il riconoscimento in tempo reale dello stato delle mani (mano destra, mano sinistra, entrambe, o nessuna) catturate da una webcam. Il sistema sfrutta la potenza e l'efficienza dei modelli pre-addestrati di **Google MediaPipe** per l'analisi dei frame video.

Il flusso video viene gestito tramite una pipeline RTSP locale (utilizzando FFmpeg e Mediamtx) per garantire flessibilità e disaccoppiamento. Uno script Python si occupa di leggere lo stream, eseguire l'inferenza con MediaPipe, e inviare lo stato del gesto riconosciuto a un ESP32. Il dispositivo hardware, a sua volta, visualizza lo stato ricevuto sia sul Serial Monitor sia su una pagina web servita dal dispositivo stesso.

L'obiettivo è dimostrare un flusso di lavoro efficiente per un'applicazione di Computer Vision in tempo reale, integrando un modello IA allo stato dell'arte con un dispositivo IoT.

## Componenti Principali del Sistema

1.  **Webcam USB:** Sorgente video primaria.
2.  **FFmpeg:** Utilizzato per catturare il flusso video dalla webcam, specificare il formato e la risoluzione, e inviarlo a un server RTSP.
3.  **Mediamtx:** Funge da server RTSP locale, ricevendo lo stream da FFmpeg e rendendolo disponibile per la connessione da parte di client (come lo script Python).
4.  **Script Python (PC):**
6.  **ESP32:**

## Prerequisiti Software

**Sul PC (Arch Linux):**
* Python 3 (l'ambiente è stato sviluppato con Python 3.12.4 perchè la versione 3.13 non supportava mediapipe)
* `pacman` per installare pacchetti di sistema.
* Ambiente virtuale Python (`.venv_`).
* Librerie Python (installate tramite `pacman` o `pip` nell'ambiente virtuale):
    * `mediapipe` (da `pacman`)
    * `python-opencv` (da `pacman`, per OpenCV)
* `ffmpeg` (installato con `sudo pacman -S ffmpeg`)
* Mediamtx (scaricato manualmente da GitHub e avviato localmente).

**Per l'ESP32:**
* IDE Arduino o PlatformIO con il core ESP32 installato.
* Librerie Arduino: `WiFi.h`, `WebServer.h`.

## Guida all'Avvio Passo Passo

È necessario eseguire i componenti in un ordine specifico e spesso in terminali separati.

**Fase A: Setup Iniziale (da fare una volta, se non già fatto)**

1.  **Clonare il repository:**
    ```bash
    git clone [https://github.com/tuo-username/mediapipe-hand-control-esp32.git](https://github.com/tuo-username/mediapipe-hand-control-esp32.git)
    cd mediapipe-hand-control-esp32
    ```
2.  **Installare Dipendenze di Sistema su PC:**
    ```bash
    sudo pacman -Syu
    sudo pacman -S git ffmpeg v4l-utils
    ```

3.  **Creare e Configurare l'Ambiente Virtuale Python:**
   sulla cartella principale:
   ```bash
    # Crea un ambiente virtuale chiamato '.venv'
    python -m venv .venv

    # Attiva l'ambiente virtuale
    source .venv/bin/activate

    # Installa tutte le librerie Python necessarie leggendo il file requirements.txt
    pip install -r python_client/requirements.txt
   ```

4.  **Scaricare Mediamtx:**
    Scaricare l'archivio `.tar.gz` di Mediamtx per Linux amd64 da [GitHub Releases](https://github.com/bluenviron/mediamtx/releases) ed estrarlo.

4.  **Programmare l'ESP32:**
    * Aprire lo sketch da `esp32_server/server_ESP32.ino` .
    * Modificare le credenziali Wi-Fi (`IL_TUO_SSID` e `LA_TUA_PASSWORD_WIFI`).
    * Selezionare la scheda ESP32 corretta e la porta seriale.
    * Caricare lo sketch sull'ESP32 (tenendo premuto il pulsante BOOT su ESP32).
    * Aprire il Serial Monitor (baud rate 115200) e annotare l'indirizzo IP dell'ESP32.
    * Modificare la variabile `ESP32_IP` nello script `det.py` con l'IP annotato.

**Fase B: Esecuzione del sistema**

1.  **Terminale 1 (Server RTSP):** Avviare Mediamtx.
    ```bash
    cd percorso/alla/cartella/mediamtx/
    ./mediamtx
    ```
    *Lasciare in esecuzione.*

2.  **Terminale 2 (Streaming Webcam):** Avviare FFmpeg per inviare lo stream della webcam a Mediamtx.
    * Verificare il dispositivo webcam corretto (es. `/dev/video0`, `/dev/video2`).
    ```bash
    ffmpeg -f v4l2 -video_size 640x480 -r 30 -i /dev/video0 -c:v h264_nvenc -b:v 2M -preset fast -pix_fmt yuv420p -zerolatency true -an -f rtsp -rtsp_transport udp rtsp://localhost:8554/webcam_stream
    ```
    *Lasciare in esecuzione.*

3.  **Terminale 3 (PyCharm - Ambiente `.venv_` Attivo):** Eseguire lo script principale del sistema.
    ```bash
    # Navigare in codice_python/
    python det.py
    ```
    *Si aprirà una finestra OpenCV mostrando il video con la predizione del gesto. Lo stato verrà inviato in tempo reale all'ESP32.*

4.  **Verifica**
    * **Finestra OpenCV**: Mostra il video live con lo stato sovrimpresso.
    * **Terminale Python**: Mostra i log di cambio stato e le conferme di invio all'ESP32.
    * **Serial Monitor (Arduino)**: Mostra i log dei nuovi stati ricevuti.
    * **Browser Web**: Visitando l'indirizzo IP dell'ESP32, si vedrà una pagina web che si aggiorna automaticamente con lo stato corrente.
