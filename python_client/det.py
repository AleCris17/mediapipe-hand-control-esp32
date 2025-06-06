"""
Client per il rilevamento delle mani che comunica con un server su ESP32.

Questo script esegue le seguenti operazioni:
1. Avvia un thread in background per catturare un flusso video RTSP in modo efficiente.
2. Nel thread principale, preleva i frame video più recenti.
3. Utilizza la libreria MediaPipe per rilevare la presenza e il tipo di mani (destra, sinistra, entrambe).
4. Determina lo stato corrente ('No Hand', 'Left Hand', 'Right Hand', 'Both Hands').
5. Se lo stato rilevato è diverso dall'ultimo stato inviato, invia il nuovo stato
   tramite una richiesta HTTP POST a un server web su un ESP32.
6. Mostra il video con lo stato corrente sovrimpresso.
"""

# Import delle librerie di sistema e di terze parti
import threading
import queue
import cv2
import mediapipe as mp
import requests
import time

# ==============================================================================
# SEZIONE DI CONFIGURAZIONE
# ==============================================================================

# Indirizzo IP del server ESP32.
# !!! MODIFICARE QUESTO VALORE CON L'IP MOSTRATO DAL SERIAL MONITOR DELL'ARDUINO IDE !!!
ESP32_IP = "192.168.205.67"
ESP32_URL = f"http://{ESP32_IP}/update_status"

# URL dello stream video RTSP fornito da ffmpeg.
RTSP_URL = "rtsp://localhost:8554/webcam_stream"

# ==============================================================================
# GESTIONE DELLO STREAMING VIDEO CON THREADING
# ==============================================================================

# Coda per disaccoppiare la cattura video dall'elaborazione.
# maxsize=1 garantisce che si elabori sempre il frame più recente, eliminando la latenza.
frame_queue = queue.Queue(maxsize=1)


def video_capture_thread(url):
    """
    Funzione eseguita in un thread separato per la cattura dei frame video.

    Legge continuamente i frame dallo stream e li inserisce nella 'frame_queue'.
    Se la coda è piena, il frame più vecchio viene scartato per far posto a quello nuovo.

    Args:
        url (str): L'URL dello stream RTSP.
    """
    cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    while True:
        success, frame = cap.read()
        if not success:
            print("Stream video terminato o errore di cattura.")
            break

        # Gestione della coda per mantenere solo l'ultimo frame
        if frame_queue.full():
            try:
                frame_queue.get_nowait()  # Rimuove il frame obsoleto
            except queue.Empty:
                pass
        frame_queue.put(frame)

    cap.release()


# ==============================================================================
# INIZIALIZZAZIONE DEL MODELLO E DELLO STATO
# ==============================================================================

# Inizializzazione del modello MediaPipe Hands.
# model_complexity=0 è l'opzione più veloce, ideale per applicazioni in tempo reale.
mp_hands = mp.solutions.hands
hands_detector = mp_hands.Hands(
    static_image_mode=False,
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    max_num_hands=2)

# Variabile per memorizzare l'ultimo stato inviato all'ESP32.
# Serve a evitare di inviare dati ridondanti ad ogni frame.
last_sent_status = None

# ==============================================================================
# ESECUZIONE PRINCIPALE
# ==============================================================================

# Creazione e avvio del thread per la cattura video.
# Viene impostato come 'daemon' per terminare automaticamente alla chiusura del programma.
capture_thread = threading.Thread(target=video_capture_thread, args=(RTSP_URL,))
capture_thread.daemon = True
capture_thread.start()

print("Avvio client. In attesa del primo frame dallo stream video...")

# Loop principale dell'applicazione.
while True:
    # Se la coda è vuota, il thread di cattura non ha ancora fornito un nuovo frame.
    # Si attende brevemente e si continua, senza bloccare l'esecuzione.
    if frame_queue.empty():
        cv2.waitKey(1)
        continue

    # Preleva il frame più recente disponibile.
    image_frame = frame_queue.get()
    if image_frame is None:
        continue

    # Elaborazione preliminare dell'immagine
    image_frame = cv2.flip(image_frame, 1)  # Effetto specchio
    image_rgb = cv2.cvtColor(image_frame, cv2.COLOR_BGR2RGB)  # Conversione per MediaPipe

    # Rilevamento delle mani
    results = hands_detector.process(image_rgb)

    # Determinazione dello stato corrente
    current_status = "No Hand"
    if results.multi_hand_landmarks:
        if len(results.multi_handedness) == 2:
            current_status = "Both Hands"
        elif len(results.multi_handedness) == 1:
            label = results.multi_handedness[0].classification[0].label
            current_status = f"{label} Hand"

    # Invia lo stato all'ESP32 via HTTP POST solo se è cambiato
    if current_status != last_sent_status:
        print(f"INFO: Rilevato cambio di stato -> '{current_status}'. Invio in corso...")
        try:
            response = requests.post(ESP32_URL, data=current_status.encode('utf-8'), timeout=1)
            if response.status_code == 200:
                print("INFO: Stato inviato all'ESP32 con successo.")
                last_sent_status = current_status  # Aggiorna lo stato solo dopo un invio riuscito
            else:
                print(f"ERRORE: Risposta inattesa dall'ESP32 (Codice: {response.status_code})")

        except requests.exceptions.RequestException as e:
            print(f"ERRORE: Impossibile connettersi all'ESP32 a {ESP32_IP}. Dettagli: {e}")

    # Visualizzazione dell'output video
    cv2.putText(image_frame, current_status, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
    cv2.imshow('Hand Tracking Client', image_frame)

    # Interruzione del loop alla pressione del tasto 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Chiusura e pulizia delle risorse
cv2.destroyAllWindows()
print("Programma terminato.")