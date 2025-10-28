#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// WiFi-asetukset (korvaa omillasi)
const char *ssid = "YourNetworkName";
const char *password = "YourPassword";


// Web-palvelin portissa 80
WebServer server(80);

// Nykyinen silmien tila (oletuksena "center")
String eyeState = "center";
const int smokePin = 27;

// HTML-sivu (upotettu Arduinoon)
const char index_html[] PROGMEM = R"rawliteral(
<!DOCTYPE html>
<html lang="fi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Silmien Simulaatio</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-color: #f0f0f0;
        }
        canvas {
            border: 1px solid #000;
            background-color: #000; /* Musta tausta kuten OLED */
            image-rendering: pixelated; /* Säilytä pikselimäinen ulkoasu */
        }
        .controls {
            margin-top: 20px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>Silmien Simulaatio</h1>
    <canvas id="eyeCanvas" width="128" height="32"></canvas>
    <div class="controls">
        <button onclick="setEyeState('center')">Keskelle</button>
        <button onclick="setEyeState('left')">Vasemmalle</button>
        <button onclick="setEyeState('right')">Oikealle</button>
        <button onclick="setEyeState('up')">Ylös</button>
        <button onclick="setEyeState('down')">Alas</button>
        <button onclick="setEyeState('blink')">Vilkkuminen</button>
        <button onclick="setEyeState('roll')">Pyörittely</button>
        <button onclick="setEyeState('smoke')">Smoke</button> <!-- Lisätty smoke-nappi teemaan -->
    </div>

    <script>
        const canvas = document.getElementById('eyeCanvas');
        const ctx = canvas.getContext('2d');

        // Silmien parametrit
        const screenWidth = 128;
        const screenHeight = 32;
        const leftEyeX = screenWidth / 4;
        const leftEyeY = screenHeight / 2;
        const rightEyeX = 3 * screenWidth / 4;
        const rightEyeY = screenHeight / 2;
        const eyeRadius = 10;
        const pupilRadius = 4;

        let pupilOffsetX = 0;
        let pupilOffsetY = 0;

        // Funktio silmien piirtämiseen
        function drawEyes() {
            ctx.clearRect(0, 0, screenWidth, screenHeight);

            ctx.beginPath();
            ctx.arc(leftEyeX, leftEyeY, eyeRadius, 0, 2 * Math.PI);
            ctx.strokeStyle = '#fff';
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(leftEyeX + pupilOffsetX, leftEyeY + pupilOffsetY, pupilRadius, 0, 2 * Math.PI);
            ctx.fillStyle = '#fff';
            ctx.fill();

            ctx.beginPath();
            ctx.arc(rightEyeX, rightEyeY, eyeRadius, 0, 2 * Math.PI);
            ctx.stroke();

            ctx.beginPath();
            ctx.arc(rightEyeX + pupilOffsetX, rightEyeY + pupilOffsetY, pupilRadius, 0, 2 * Math.PI);
            ctx.fill();
        }

        // Funktio tilan asettamiseen (lähetä POST Arduino-palvelimelle)
        async function setEyeState(state) {
            try {
                const response = await fetch('/set-eye-state', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state })
                });
                if (response.ok) {
                    // Päivitä paikallinen simulaatio
                    switch (state) {
                        case 'left': moveEyesLeft(); break;
                        case 'right': moveEyesRight(); break;
                        case 'up': moveEyesUp(); break;
                        case 'down': moveEyesDown(); break;
                        case 'center': moveEyesCenter(); break;
                        case 'blink': moveEyesBlink(); break;
                        case 'roll': moveEyesRoll(); break;
                        case 'smoke': moveEyesSmoke(); break; // Lisätty smoke paikalliseen simulaatioon
                    }
                }
            } catch (error) {
                console.error('Error setting state:', error);
            }
        }

        // Muut moveEyes-funktiot (paikallinen simulaatio)
        function moveEyesLeft() {
            pupilOffsetX = - (eyeRadius - pupilRadius - 2);
            pupilOffsetY = 0;
            drawEyes();
        }

        function moveEyesRight() {
            pupilOffsetX = (eyeRadius - pupilRadius - 2);
            pupilOffsetY = 0;
            drawEyes();
        }

        function moveEyesUp() {
            pupilOffsetX = 0;
            pupilOffsetY = - (eyeRadius - pupilRadius - 2);
            drawEyes();
        }

        function moveEyesDown() {
            pupilOffsetX = 0;
            pupilOffsetY = (eyeRadius - pupilRadius - 2);
            drawEyes();
        }

        function moveEyesCenter() {
            pupilOffsetX = 0;
            pupilOffsetY = 0;
            drawEyes();
        }

        function moveEyesBlink() {
            ctx.clearRect(0, 0, screenWidth, screenHeight);

            ctx.beginPath();
            ctx.moveTo(leftEyeX - eyeRadius, leftEyeY);
            ctx.lineTo(leftEyeX + eyeRadius, leftEyeY);
            ctx.stroke();

            ctx.beginPath();
            ctx.moveTo(rightEyeX - eyeRadius, rightEyeY);
            ctx.lineTo(rightEyeX + eyeRadius, rightEyeY);
            ctx.stroke();

            setTimeout(drawEyes, 200);
        }

        function moveEyesRoll() {
            const rollRadius = eyeRadius - pupilRadius - 2;
            const steps = 8;
            let i = 0;

            function animate() {
                if (i >= steps) {
                    moveEyesCenter();
                    return;
                }
                const angle = 2 * Math.PI * i / steps;
                pupilOffsetX = rollRadius * Math.cos(angle);
                pupilOffsetY = rollRadius * Math.sin(angle);
                drawEyes();
                i++;
                setTimeout(animate, 100);
            }

            animate();
        }

        function moveEyesSmoke() {
            ctx.clearRect(0, 0, screenWidth, screenHeight);
            // Yksinkertainen savu-efekti webissä (esim. piirrä viivoja)
            for (let frame = 0; frame < 5; frame++) {
                setTimeout(() => {
                    ctx.clearRect(0, 0, screenWidth, screenHeight);
                    drawEyes(); // Tausta
                    // Savu-viivat
                    ctx.beginPath();
                    ctx.moveTo(leftEyeX, leftEyeY - eyeRadius - frame * 2);
                    ctx.lineTo(leftEyeX - 5, leftEyeY - eyeRadius - 10 - frame * 2);
                    ctx.stroke();
                    ctx.beginPath();
                    ctx.moveTo(rightEyeX, rightEyeY - eyeRadius - frame * 2);
                    ctx.lineTo(rightEyeX + 5, rightEyeY - eyeRadius - 10 - frame * 2);
                    ctx.stroke();
                }, frame * 200);
            }
        }

        // Alusta
       // moveEyesCenter();
    </script>
</body>
</html>
)rawliteral";


void setup() {
  Serial.begin(115200);

  pinMode(smokePin, OUTPUT);
  digitalWrite(smokePin, LOW);  // Aluksi LOW

  if (!WiFi.softAP(ssid, password)) {
    log_e("Soft AP creation failed.");
    while (1);
  }

  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  //server.begin();

  Serial.println("Server started");
/*
  // Yhdistä WiFi:hen
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
*/
  // Endpointit
  server.on("/", HTTP_GET, []() {
    server.send_P(200, "text/html", index_html);  // Palvele HTML-sivu
  });

  server.on("/set-eye-state", HTTP_POST, []() {
    if (server.hasArg("plain")) {
      StaticJsonDocument<200> doc;
      deserializeJson(doc, server.arg("plain"));
      String state = doc["state"];
      if (state == "center" || state == "left" || 
          state == "right" || state == "up" || 
          state == "down" || state == "blink" || 
          state == "roll" || state == "smoke" ||
          state == "unconscious" || state == "sleepy") {
        eyeState = state;
        if (state == "smoke") {
          digitalWrite(smokePin, HIGH);  // Lähetä HIGH pin 27:aan smoke-tilassa (jos käytät)
          return;
        } else {
          digitalWrite(smokePin, LOW);  // Muissa tiloissa LOW
        }
      
       // Päivitä paikallinen näyttö heti tilan muutoksessa
        server.send(200, "application/json", "{\"success\": true}");
      } else {
        server.send(400, "application/json", "{\"error\": \"Invalid state\"}");
      }
    } else {
      server.send(400, "application/json", "{\"error\": \"No body\"}");
    }
  });

  server.on("/get-eye-state", HTTP_GET, []() {
    server.send(200, "application/json", "{\"state\": \"" + eyeState + "\"}");
  });

  server.begin();
}

void loop() {
  server.handleClient();
}
