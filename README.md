# Rilevamento Gesti della Mano con MediaPipe e ESP32

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Framework: MediaPipe](https://img.shields.io/badge/Framework-MediaPipe-green.svg)](https://mediapipe.dev/)

Un sistema completo per il rilevamento di gesti in tempo reale che utilizza modelli pre-addestrati di Google MediaPipe e si integra con hardware ESP32 per notifiche istantanee.

## Descrizione del Progetto

Questo progetto implementa un sistema per il riconoscimento in tempo reale dello stato delle mani (mano destra, mano sinistra, entrambe, o nessuna) catturate da una webcam. Il sistema sfrutta la potenza e l'efficienza dei modelli pre-addestrati di **Google MediaPipe** per l'analisi dei frame video.

Il flusso video viene gestito tramite una pipeline RTSP locale (utilizzando FFmpeg e Mediamtx) per garantire flessibilità e disaccoppiamento. Uno script Python si occupa di leggere lo stream, eseguire l'inferenza con MediaPipe, e inviare lo stato del gesto riconosciuto a un ESP32. Il dispositivo hardware, a sua volta, visualizza lo stato ricevuto sia sul Serial Monitor sia su una pagina web servita dal dispositivo stesso.

L'obiettivo è dimostrare un flusso di lavoro efficiente per un'applicazione di Computer Vision in tempo reale, integrando un modello IA allo stato dell'arte con un dispositivo IoT.

## Architettura del Sistema

Il flusso dei dati segue questa architettura:

```mermaid
graph TD
    A[<i class='fa fa-camera'></i> Webcam USB] -->|Flusso video raw| B(FFmpeg);
    B -->|Stream H.264 RTSP| C{Mediamtx Server};
    C -->|Stream RTSP| D[<i class='fa fa-python'></i> Script Python con MediaPipe];
    D -- Inferenza --> D;
    D -->|Stato Gesto (HTTP POST)| E[<i class='fa fa-microchip'></i> ESP32];
    E -->|Output| F(Serial Monitor);
    E -->|Pagina Web| G[<i class='fa fa-globe'></i> Browser Utente];
