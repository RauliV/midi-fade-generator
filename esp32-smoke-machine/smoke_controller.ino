/*
 * 🌫️ ESP32 Smoke Machine Controller
 * 
 * WiFi-ohjattu savukone relay-kontrolli näytelmäkäyttöön.
 * HTTP REST API Multiplay-integraatiota varten.
 * 
 * Hardware:
 * - ESP32 Dev Board
 * - 5V Relay Module  
 * - Savukone (12V/24V)
 * 
 * API Endpoints:
 * - POST /api/smoke/on
 * - POST /api/smoke/off  
 * - POST /api/pulse/{seconds}
 * - GET  /api/status
 * 
 * Author: Rauli Virtanen
 * Part of: MIDI Fade Generator Theater Control System
 */

#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>
#include <Preferences.h>

// Hardware pins
const int RELAY_PIN = 2;        // GPIO2 → Relay control
const int STATUS_LED = LED_BUILTIN;  // Built-in LED

// WiFi credentials (modify these!)
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Web server
WebServer server(80);
Preferences preferences;

// State tracking
bool smokeActive = false;
unsigned long smokeStartTime = 0;
unsigned long smokeDuration = 0;
bool pulseMode = false;

// Statistics
unsigned long totalOperations = 0;
unsigned long totalSmokeTime = 0;  // seconds

void setup() {
  Serial.begin(115200);
  Serial.println("🌫️ ESP32 Smoke Machine Controller Starting...");
  
  // Hardware setup
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(STATUS_LED, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Relay OFF (safe start)
  digitalWrite(STATUS_LED, LOW);
  
  // Load preferences
  preferences.begin("smoke", false);
  totalOperations = preferences.getULong("operations", 0);
  totalSmokeTime = preferences.getULong("smoketime", 0);
  
  // WiFi setup
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    digitalWrite(STATUS_LED, !digitalRead(STATUS_LED));  // Blink while connecting
  }
  
  Serial.println();
  Serial.print("✅ WiFi connected! IP: ");
  Serial.println(WiFi.localIP());
  digitalWrite(STATUS_LED, HIGH);  // Solid on when connected
  
  // Setup HTTP routes
  setupRoutes();
  
  // Start web server
  server.begin();
  Serial.println("🌐 HTTP Server started on port 80");
  Serial.println("📋 API Endpoints:");
  Serial.println("   POST /api/smoke/on");
  Serial.println("   POST /api/smoke/off");
  Serial.println("   POST /api/pulse/{seconds}");
  Serial.println("   GET  /api/status");
  Serial.println("   GET  /api/config");
  Serial.println();
  Serial.println("🎭 Ready for Multiplay integration!");
}

void loop() {
  server.handleClient();
  
  // Handle pulse timing
  if (pulseMode && smokeActive) {
    if (millis() - smokeStartTime >= smokeDuration * 1000) {
      turnSmokeOff();
      Serial.println("⏰ Pulse completed");
    }
  }
  
  // Safety timeout (10 minutes max)
  if (smokeActive && (millis() - smokeStartTime >= 600000)) {
    turnSmokeOff();
    Serial.println("🚨 Safety timeout - smoke turned off after 10 minutes");
  }
  
  delay(100);
}

void setupRoutes() {
  // CORS headers for web interface
  server.onNotFound([]() {
    if (server.method() == HTTP_OPTIONS) {
      sendCORSHeaders();
      server.send(200);
    } else {
      server.send(404, "text/plain", "Endpoint not found");
    }
  });
  
  // Smoke control endpoints
  server.on("/api/smoke/on", HTTP_POST, handleSmokeOn);
  server.on("/api/smoke/off", HTTP_POST, handleSmokeOff);
  
  // Pulse endpoint with duration
  server.on("/api/pulse", HTTP_POST, handlePulse);
  
  // Status and info
  server.on("/api/status", HTTP_GET, handleStatus);
  server.on("/api/config", HTTP_GET, handleGetConfig);
  server.on("/api/config", HTTP_POST, handleSetConfig);
  
  // Root page
  server.on("/", HTTP_GET, handleRoot);
  
  Serial.println("📡 HTTP routes configured");
}

void handleSmokeOn() {
  sendCORSHeaders();
  
  if (smokeActive) {
    server.send(200, "application/json", "{\"status\":\"already_on\",\"message\":\"Smoke already active\"}");
    return;
  }
  
  turnSmokeOn(0);  // Indefinite duration
  totalOperations++;
  saveStats();
  
  Serial.println("🌫️ Smoke ON (manual)");
  server.send(200, "application/json", "{\"status\":\"success\",\"message\":\"Smoke activated\"}");
}

void handleSmokeOff() {
  sendCORSHeaders();
  
  if (!smokeActive) {
    server.send(200, "application/json", "{\"status\":\"already_off\",\"message\":\"Smoke already inactive\"}");
    return;
  }
  
  turnSmokeOff();
  totalOperations++;
  saveStats();
  
  Serial.println("🌫️ Smoke OFF (manual)");
  server.send(200, "application/json", "{\"status\":\"success\",\"message\":\"Smoke deactivated\"}");
}

void handlePulse() {
  sendCORSHeaders();
  
  if (!server.hasArg("plain")) {
    server.send(400, "application/json", "{\"error\":\"Missing JSON payload\"}");
    return;
  }
  
  // Parse JSON payload
  DynamicJsonDocument doc(1024);
  deserializeJson(doc, server.arg("plain"));
  
  int duration = doc["duration"] | 3;  // Default 3 seconds
  int intensity = doc["intensity"] | 100;  // Default 100% (not used for relay, but logged)
  
  // Validate duration
  if (duration < 1 || duration > 60) {
    server.send(400, "application/json", "{\"error\":\"Duration must be 1-60 seconds\"}");
    return;
  }
  
  if (smokeActive) {
    server.send(409, "application/json", "{\"error\":\"Smoke already active\"}");
    return;
  }
  
  // Start pulse
  turnSmokeOn(duration);
  totalOperations++;
  saveStats();
  
  Serial.printf("🌫️ Smoke PULSE: %d seconds @ %d%% intensity\n", duration, intensity);
  
  DynamicJsonDocument response(512);
  response["status"] = "success";
  response["message"] = "Smoke pulse started";
  response["duration"] = duration;
  response["intensity"] = intensity;
  
  String responseStr;
  serializeJson(response, responseStr);
  server.send(200, "application/json", responseStr);
}

void handleStatus() {
  sendCORSHeaders();
  
  DynamicJsonDocument doc(1024);
  doc["device"] = "ESP32 Smoke Machine";
  doc["version"] = "1.0.0";
  doc["wifi_ssid"] = WiFi.SSID();
  doc["ip_address"] = WiFi.localIP().toString();
  doc["uptime_ms"] = millis();
  
  doc["smoke"]["active"] = smokeActive;
  doc["smoke"]["pulse_mode"] = pulseMode;
  
  if (smokeActive) {
    doc["smoke"]["running_time"] = (millis() - smokeStartTime) / 1000;
    if (pulseMode) {
      doc["smoke"]["remaining_time"] = smokeDuration - ((millis() - smokeStartTime) / 1000);
    }
  }
  
  doc["statistics"]["total_operations"] = totalOperations;
  doc["statistics"]["total_smoke_time"] = totalSmokeTime;
  
  doc["hardware"]["relay_pin"] = RELAY_PIN;
  doc["hardware"]["status_led"] = STATUS_LED;
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleGetConfig() {
  sendCORSHeaders();
  
  DynamicJsonDocument doc(512);
  doc["wifi_ssid"] = WiFi.SSID();
  doc["device_name"] = "ESP32-Smoke";
  doc["api_version"] = "1.0";
  doc["max_pulse_duration"] = 60;
  doc["safety_timeout"] = 600;
  
  String response;
  serializeJson(doc, response);
  server.send(200, "application/json", response);
}

void handleSetConfig() {
  sendCORSHeaders();
  server.send(501, "application/json", "{\"error\":\"Configuration updates not implemented yet\"}");
}

void handleRoot() {
  String html = R"(
<!DOCTYPE html>
<html>
<head>
    <title>🌫️ ESP32 Smoke Machine</title>
    <style>
        body { font-family: Arial; margin: 20px; }
        button { padding: 10px 20px; margin: 5px; font-size: 16px; }
        .on { background: #4CAF50; color: white; }
        .off { background: #f44336; color: white; }
        .pulse { background: #ff9800; color: white; }
        .status { margin: 20px 0; padding: 10px; border: 1px solid #ccc; }
    </style>
</head>
<body>
    <h1>🌫️ ESP32 Smoke Machine Controller</h1>
    
    <div class="status" id="status">
        Loading status...
    </div>
    
    <button class="on" onclick="smokeOn()">Smoke ON</button>
    <button class="off" onclick="smokeOff()">Smoke OFF</button>
    <button class="pulse" onclick="smokePulse()">Pulse 3s</button>
    
    <h3>Manual Pulse:</h3>
    <input type="number" id="pulseSeconds" value="5" min="1" max="60"> seconds
    <button class="pulse" onclick="customPulse()">Custom Pulse</button>
    
    <h3>API Documentation:</h3>
    <pre>
POST /api/smoke/on       - Turn smoke on
POST /api/smoke/off      - Turn smoke off
POST /api/pulse          - Pulse smoke (JSON: {"duration": N})
GET  /api/status         - Get device status
    </pre>
    
    <script>
        function updateStatus() {
            fetch('/api/status')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('status').innerHTML = 
                        `<strong>Status:</strong> ${data.smoke.active ? '🌫️ ACTIVE' : '💤 INACTIVE'}<br>` +
                        `<strong>IP:</strong> ${data.ip_address}<br>` +
                        `<strong>Operations:</strong> ${data.statistics.total_operations}<br>` +
                        `<strong>Total Smoke Time:</strong> ${data.statistics.total_smoke_time}s`;
                });
        }
        
        function smokeOn() { 
            fetch('/api/smoke/on', {method: 'POST'})
                .then(r => r.json())
                .then(data => { alert(data.message); updateStatus(); });
        }
        
        function smokeOff() { 
            fetch('/api/smoke/off', {method: 'POST'})
                .then(r => r.json())
                .then(data => { alert(data.message); updateStatus(); });
        }
        
        function smokePulse() {
            fetch('/api/pulse', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({duration: 3, intensity: 100})
            })
            .then(r => r.json())
            .then(data => { alert(data.message); updateStatus(); });
        }
        
        function customPulse() {
            const duration = document.getElementById('pulseSeconds').value;
            fetch('/api/pulse', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({duration: parseInt(duration), intensity: 100})
            })
            .then(r => r.json())
            .then(data => { alert(data.message); updateStatus(); });
        }
        
        // Update status every 2 seconds
        setInterval(updateStatus, 2000);
        updateStatus();
    </script>
</body>
</html>
  )";
  
  server.send(200, "text/html", html);
}

void turnSmokeOn(int duration) {
  digitalWrite(RELAY_PIN, HIGH);
  smokeActive = true;
  smokeStartTime = millis();
  
  if (duration > 0) {
    pulseMode = true;
    smokeDuration = duration;
  } else {
    pulseMode = false;
    smokeDuration = 0;
  }
  
  // Blink status LED when active
  digitalWrite(STATUS_LED, LOW);
}

void turnSmokeOff() {
  digitalWrite(RELAY_PIN, LOW);
  
  if (smokeActive) {
    unsigned long runTime = (millis() - smokeStartTime) / 1000;
    totalSmokeTime += runTime;
    Serial.printf("📊 Smoke ran for %lu seconds\n", runTime);
  }
  
  smokeActive = false;
  pulseMode = false;
  smokeDuration = 0;
  
  digitalWrite(STATUS_LED, HIGH);  // Solid on when ready
}

void saveStats() {
  preferences.putULong("operations", totalOperations);
  preferences.putULong("smoketime", totalSmokeTime);
}

void sendCORSHeaders() {
  server.sendHeader("Access-Control-Allow-Origin", "*");
  server.sendHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  server.sendHeader("Access-Control-Allow-Headers", "Content-Type");
}