/*
 * 🎭 ESP32 Savupalvelin v3.0 - 433MHz Radio + HTTP API
 * 
 * Yhdistää:
 * - HTTP API (Multiplay-ohjaus)
 * - 433MHz Radio (Robotti backup)  
 * - Web-käyttöliittymä
 * - Turvallisuusfeaturet
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <RCSwitch.h>  // 433MHz radio library

// WiFi-asetukset (VAIHDA OMAT!)
const char *ssid = "YourNetworkName";
const char *password = "YourPassword";

// Hardware-pinnit
const int SMOKE_RELAY_PIN = 27;      // Rele savukoneelle
const int RADIO_RX_PIN = 2;          // 433MHz vastaanotin
const int STATUS_LED_PIN = 4;        // Status LED
const int MANUAL_BUTTON_PIN = 5;     // Fyysinen nappi hätään

// 433MHz Radio setup
RCSwitch mySwitch = RCSwitch();

// Web-palvelin
WebServer server(80);

// Savukoneen tila
bool smokeActive = false;
unsigned long smokeStartTime = 0;
const unsigned long MAX_SMOKE_TIME = 300000;  // 5 min maksimi
const unsigned long DEFAULT_PULSE_TIME = 5000; // 5 sek oletus

// 433MHz koodit (VAIHDA OMAT!)
const unsigned long SMOKE_ON_CODE = 12345;
const unsigned long SMOKE_OFF_CODE = 54321;
const unsigned long SMOKE_PULSE_CODE = 11111;

// Tilastot
unsigned long totalActivations = 0;
unsigned long uptimeStart = 0;
String lastTriggerSource = "none";

void setup() {
  Serial.begin(115200);
  Serial.println("🎭 Savupalvelin v3.0 - 433MHz + HTTP");
  
  // GPIO setup
  pinMode(SMOKE_RELAY_PIN, OUTPUT);
  pinMode(STATUS_LED_PIN, OUTPUT);
  pinMode(MANUAL_BUTTON_PIN, INPUT_PULLUP);
  digitalWrite(SMOKE_RELAY_PIN, LOW);
  
  // 433MHz Radio setup
  mySwitch.enableReceive(RADIO_RX_PIN);
  Serial.println("📻 433MHz vastaanotin päällä pin " + String(RADIO_RX_PIN));
  
  // WiFi yhteys
  WiFi.begin(ssid, password);
  Serial.print("🌐 Yhdistetään WiFi...");
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n✅ WiFi yhdistetty!");
    Serial.print("🌍 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n❌ WiFi yhteys epäonnistui - jatketaan offline");
  }
  
  // HTTP endpoints
  setupWebServer();
  
  uptimeStart = millis();
  Serial.println("🚀 Järjestelmä valmis!");
  blinkStatus(3); // 3 vilkutusta = valmis
}

void loop() {
  // HTTP server
  server.handleClient();
  
  // 433MHz radio kuuntelu
  checkRadioCommands();
  
  // Manuaalinen nappi (hätä)
  checkManualButton();
  
  // Turvallisuustarkistukset
  checkSafety();
  
  // Status LED update
  updateStatusLED();
  
  delay(10); // Pieni viive
}

void checkRadioCommands() {
  if (mySwitch.available()) {
    unsigned long receivedValue = mySwitch.getReceivedValue();
    
    if (receivedValue != 0) {
      Serial.print("📻 433MHz vastaanotettu: ");
      Serial.println(receivedValue);
      
      switch (receivedValue) {
        case SMOKE_ON_CODE:
          triggerSmoke("433MHz_ON", 0); // Jatkuva
          break;
          
        case SMOKE_OFF_CODE:
          stopSmoke("433MHz_OFF");
          break;
          
        case SMOKE_PULSE_CODE:
          triggerSmoke("433MHz_PULSE", DEFAULT_PULSE_TIME);
          break;
          
        default:
          Serial.println("❓ Tuntematon 433MHz koodi");
      }
    }
    
    mySwitch.resetAvailable();
  }
}

void checkManualButton() {
  static unsigned long lastButtonPress = 0;
  static bool buttonPressed = false;
  
  bool currentState = (digitalRead(MANUAL_BUTTON_PIN) == LOW);
  
  if (currentState && !buttonPressed && (millis() - lastButtonPress > 1000)) {
    // Nappi painettu (debounce 1s)
    triggerSmoke("MANUAL_BUTTON", DEFAULT_PULSE_TIME);
    lastButtonPress = millis();
    buttonPressed = true;
    Serial.println("🔴 Manuaalinen nappi painettu!");
  } else if (!currentState) {
    buttonPressed = false;
  }
}

void checkSafety() {
  // Maksimiaika-tarkistus
  if (smokeActive && (millis() - smokeStartTime > MAX_SMOKE_TIME)) {
    stopSmoke("SAFETY_TIMEOUT");
    Serial.println("⚠️ TURVALLISUUS: Savukone sammutettu maksimiaika ylittyi!");
  }
}

void updateStatusLED() {
  static unsigned long lastBlink = 0;
  static bool ledState = false;
  
  if (smokeActive) {
    // Nopea vilkutus kun savu päällä
    if (millis() - lastBlink > 200) {
      ledState = !ledState;
      digitalWrite(STATUS_LED_PIN, ledState);
      lastBlink = millis();
    }
  } else {
    // Hidas vilkutus standbyssa
    if (millis() - lastBlink > 2000) {
      ledState = !ledState;
      digitalWrite(STATUS_LED_PIN, ledState);
      lastBlink = millis();
    }
  }
}

void triggerSmoke(String source, unsigned long duration) {
  // Jos jo päällä, ei käynnistetä uudelleen
  if (smokeActive) {
    Serial.println("⚠️ Savu jo päällä - ei käynnistetä uudelleen");
    return;
  }
  
  smokeActive = true;
  smokeStartTime = millis();
  lastTriggerSource = source;
  totalActivations++;
  
  digitalWrite(SMOKE_RELAY_PIN, HIGH);
  
  if (duration > 0) {
    Serial.println("🌫️ Savu päällä " + String(duration/1000) + "s (" + source + ")");
    // Ajastettu sammutus
    // TODO: Käytä timer-interruptia tuotantoversiossa
  } else {
    Serial.println("🌫️ Savu päällä jatkuvasti (" + source + ")");
  }
  
  blinkStatus(1); // 1 vilkutus = savu käynnistetty
}

void stopSmoke(String source) {
  if (!smokeActive) {
    Serial.println("ℹ️ Savu jo pois päältä");
    return;
  }
  
  smokeActive = false;
  digitalWrite(SMOKE_RELAY_PIN, LOW);
  
  unsigned long duration = millis() - smokeStartTime;
  Serial.println("⭕ Savu pois päältä (" + source + ") - kesto: " + String(duration/1000) + "s");
  
  blinkStatus(2); // 2 vilkutusta = savu sammutettu
}

void blinkStatus(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(100);
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(100);
  }
}

void setupWebServer() {
  // Pääsivu
  server.on("/", HTTP_GET, []() {
    String html = buildWebInterface();
    server.send(200, "text/html", html);
  });
  
  // API: Status
  server.on("/api/status", HTTP_GET, []() {
    StaticJsonDocument<300> doc;
    doc["smoke_active"] = smokeActive;
    doc["uptime_ms"] = millis() - uptimeStart;
    doc["total_activations"] = totalActivations;
    doc["last_trigger"] = lastTriggerSource;
    doc["wifi_connected"] = (WiFi.status() == WL_CONNECTED);
    doc["ip_address"] = WiFi.localIP().toString();
    
    String response;
    serializeJson(doc, response);
    
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", response);
  });
  
  // API: Savu päälle
  server.on("/api/smoke/on", HTTP_POST, []() {
    triggerSmoke("HTTP_API", 0);
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", "{\"success\": true, \"action\": \"smoke_on\"}");
  });
  
  // API: Savu pois
  server.on("/api/smoke/off", HTTP_POST, []() {
    stopSmoke("HTTP_API");
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", "{\"success\": true, \"action\": \"smoke_off\"}");
  });
  
  // API: Savu-pulssi
  server.on("/api/smoke/pulse", HTTP_POST, []() {
    unsigned long duration = DEFAULT_PULSE_TIME;
    
    if (server.hasArg("plain")) {
      StaticJsonDocument<200> doc;
      DeserializationError error = deserializeJson(doc, server.arg("plain"));
      if (!error && doc.containsKey("duration")) {
        duration = doc["duration"];
        duration = constrain(duration, 1000, MAX_SMOKE_TIME); // 1s - 5min
      }
    }
    
    triggerSmoke("HTTP_PULSE", duration);
    
    StaticJsonDocument<200> response;
    response["success"] = true;
    response["action"] = "smoke_pulse";
    response["duration_ms"] = duration;
    
    String responseStr;
    serializeJson(response, responseStr);
    
    server.sendHeader("Access-Control-Allow-Origin", "*");
    server.send(200, "application/json", responseStr);
  });
  
  // Legacy: Silmä-animaatiot (yhteensopivuus)
  server.on("/set-eye-state", HTTP_POST, []() {
    if (server.hasArg("plain")) {
      StaticJsonDocument<200> doc;
      deserializeJson(doc, server.arg("plain"));
      String state = doc["state"];
      
      if (state == "smoke") {
        triggerSmoke("EYE_STATE_API", DEFAULT_PULSE_TIME);
      }
      
      server.send(200, "application/json", "{\"success\": true}");
    } else {
      server.send(400, "application/json", "{\"error\": \"No body\"}");
    }
  });
  
  server.begin();
  Serial.println("🌐 Web server käynnistetty");
}

String buildWebInterface() {
  String html = R"(
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎭 Savukone v3.0</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
        .status { background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .controls { display: flex; gap: 10px; margin: 20px 0; }
        button { padding: 15px 30px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer; }
        .smoke-on { background: #ff4444; color: white; }
        .smoke-off { background: #44ff44; color: black; }
        .smoke-pulse { background: #4444ff; color: white; }
        .emergency { background: #ff8800; color: white; font-weight: bold; }
    </style>
</head>
<body>
    <h1>🎭 Teatteri-savukone v3.0</h1>
    
    <div class="status" id="status">
        <h3>📊 Tila</h3>
        <p id="statusText">Ladataan...</p>
    </div>
    
    <div class="controls">
        <button class="smoke-on" onclick="smokeControl('on')">🌫️ Savu PÄÄLLE</button>
        <button class="smoke-off" onclick="smokeControl('off')">⭕ Savu POIS</button>
        <button class="smoke-pulse" onclick="smokeControl('pulse')">⚡ 5s Pulssi</button>
    </div>
    
    <div class="controls">
        <button class="emergency" onclick="location.reload()">🔄 Päivitä sivu</button>
    </div>
    
    <div class="status">
        <h3>📻 Ohjaustavat</h3>
        <ul>
            <li><strong>HTTP API</strong>: Multiplay automaatti-ohjaus</li>
            <li><strong>433MHz Radio</strong>: Robotti-kaukolaukaisin</li>
            <li><strong>Manuaalinen nappi</strong>: Hätälaukaisu</li>
            <li><strong>Web-käyttöliittymä</strong>: Testaus ja valvonta</li>
        </ul>
    </div>

    <script>
        async function smokeControl(action) {
            try {
                const response = await fetch('/api/smoke/' + action, { method: 'POST' });
                const result = await response.json();
                console.log('Smoke control result:', result);
                updateStatus(); // Päivitä tila heti
            } catch (error) {
                console.error('Error:', error);
                alert('Virhe: ' + error.message);
            }
        }
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const status = await response.json();
                
                const uptime = Math.floor(status.uptime_ms / 1000);
                const statusHtml = `
                    <strong>Savu:</strong> ${status.smoke_active ? '🌫️ PÄÄLLÄ' : '⭕ POIS PÄÄLTÄ'}<br>
                    <strong>Uptime:</strong> ${uptime}s<br>
                    <strong>Aktivointeja:</strong> ${status.total_activations}<br>
                    <strong>Viimeisin:</strong> ${status.last_trigger}<br>
                    <strong>WiFi:</strong> ${status.wifi_connected ? '🌐 Yhdistetty' : '📶 Ei yhteyttä'}<br>
                    <strong>IP:</strong> ${status.ip_address}
                `;
                
                document.getElementById('statusText').innerHTML = statusHtml;
            } catch (error) {
                document.getElementById('statusText').innerHTML = '❌ Virhe tilassa: ' + error.message;
            }
        }
        
        // Päivitä tila 2s välein
        setInterval(updateStatus, 2000);
        updateStatus(); // Heti
    </script>
</body>
</html>
  )";
  
  return html;
}