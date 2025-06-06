/**
 * @file server_esp32.ino
 * @brief Sketch per ESP32 che avvia un server web per ricevere e visualizzare stati di gesti.
 * * Il dispositivo si connette a una rete Wi-Fi specificata e avvia un server sulla porta 80.
 * Espone tre endpoint:
 * - GET "/":            Serve una pagina HTML che mostra lo stato corrente.
 * - GET "/get_status":  Utilizzato da uno script sulla pagina HTML per l'aggiornamento asincrono.
 * - POST "/update_status": Utilizzato da un client esterno (es. Python) per aggiornare lo stato.
 */

// Inclusione delle librerie necessarie
#include <WiFi.h>
#include <WebServer.h>

//==============================================================================
// SEZIONE DI CONFIGURAZIONE
//==============================================================================

// Credenziali della rete Wi-Fi a cui l'ESP32 si connetterà.
// !!! MODIFICARE CON LE PROPRIE CREDENZIALI !!!
const char* ssid = "Alex il Leone";
const char* password = "NapoliColera";

//==============================================================================
// VARIABILI GLOBALI E OGGETTI
//==============================================================================

// Istanza del server web sulla porta 80 (HTTP).
WebServer server(80);

// Stringa per memorizzare lo stato del gesto corrente ricevuto dal client.
String currentGesture = "In attesa...";

//==============================================================================
// GESTORI DEGLI ENDPOINT HTTP
//==============================================================================

/**
 * @brief Gestisce le richieste GET alla radice del server ("/").
 * * Invia al client una pagina HTML base. La pagina contiene uno script JavaScript
 * che effettua una richiesta GET all'endpoint "/get_status" ogni secondo
 * per aggiornare dinamicamente il contenuto senza ricaricare la pagina.
 */
void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <title>Stato Gesto ESP32</title>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f0f0f0; }
    h1 { color: #333; }
    #gesture { color: #007BFF; font-size: 2.5em; font-weight: bold; }
  </style>
  <script>
    function getStatus() {
      var xhttp = new XMLHttpRequest();
      xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
          document.getElementById('gesture').innerHTML = this.responseText;
        }
      };
      xhttp.open('GET', '/get_status', true);
      xhttp.send();
    }
    setInterval(getStatus, 1000); // Esegue la funzione getStatus() ogni 1000ms.
  </script>
</head>
<body onload="getStatus()">
  <h1>Stato Gesto Corrente:</h1>
  <div id="gesture">In attesa...</div>
</body>
</html>
)rawliteral";
  server.send(200, "text/html", html);
}

/**
 * @brief Gestisce le richieste GET all'endpoint "/get_status".
 * * Utilizzato dallo script JavaScript per ottenere il valore corrente della
 * variabile 'currentGesture' e aggiornare la pagina web.
 */
void handleGetStatus() {
  server.send(200, "text/plain", currentGesture);
}

/**
 * @brief Gestisce le richieste POST all'endpoint "/update_status".
 * * Utilizzato dal client Python per inviare un nuovo stato. Il corpo (payload)
 * della richiesta POST viene letto e utilizzato per aggiornare la variabile 'currentGesture'.
 */
void handleUpdateStatus() {
  if (server.hasArg("plain") == false) {
    server.send(400, "text/plain", "Bad Request: POST body is missing.");
    return;
  }
  
  String gestureFromBody = server.arg("plain");
  currentGesture = gestureFromBody;
  
  Serial.print("Nuovo stato ricevuto: ");
  Serial.println(currentGesture);
  
  server.send(200, "text/plain", "OK");
}

//==============================================================================
// FUNZIONE DI SETUP
//==============================================================================

/**
 * @brief Funzione di setup, eseguita una sola volta all'avvio del dispositivo.
 * * Inizializza la comunicazione seriale, si connette alla rete Wi-Fi,
 * imposta le route del server web e avvia il server.
 */
void setup() {
  Serial.begin(115200);
  delay(100);
  Serial.println("\n--- Avvio ESP32 Hand Gesture Server ---");

  WiFi.begin(ssid, password);
  Serial.print("Connessione alla rete Wi-Fi '");
  Serial.print(ssid);
  Serial.print("'...");
  
  int attempt = 0;
  while (WiFi.status() != WL_CONNECTED && attempt < 20) {
    delay(500);
    Serial.print(".");
    attempt++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\nConnessione Riuscita!");
    Serial.print("Indirizzo IP del server: http://");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nConnessione Wi-Fi Fallita. Riavvio necessario.");
    while(1) delay(1000); // Blocca l'esecuzione in caso di fallimento
  }

  // Associazione degli URL alle funzioni di gestione corrispondenti
  server.on("/", HTTP_GET, handleRoot);
  server.on("/get_status", HTTP_GET, handleGetStatus);
  server.on("/update_status", HTTP_POST, handleUpdateStatus);

  server.begin();
  Serial.println("Server HTTP avviato. In attesa di richieste.");
}

//==============================================================================
// LOOP PRINCIPALE
//==============================================================================

/**
 * @brief Loop principale, eseguito continuamente dopo il setup.
 * * La sua unica responsabilità è chiamare il gestore dei client del server
 * per processare eventuali richieste HTTP in arrivo.
 */
void loop() {
  server.handleClient();
  delay(5);
}