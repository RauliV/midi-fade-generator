/*
 * 🤖 Robotti-kaukolaukaisin v3.0 - 433MHz + OLED
 * 
 * Features:
 * - OLED silmä-animaatiot (SSD1306 128x32)
 * - 433MHz radio-lähettäjä (luotettava 15m+ kantama)
 * - Manuaalinen nappi (nostettava pää)
 * - Akun tilan valvonta
 * - Backup-mode kun Multiplay kaatuu
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <RCSwitch.h>  // 433MHz radio library

// OLED näytön mitat
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Hardware-pinnit
const int BUTTON_PIN = 27;          // Manuaalinen nappi (nostettava pää)
const int RADIO_TX_PIN = 4;         // 433MHz lähettäjä
const int STATUS_LED_PIN = 2;       // Built-in LED
const int BATTERY_PIN = A0;         // Akun jännite (jos käytössä)

// 433MHz Radio setup
RCSwitch mySwitch = RCSwitch();

// Napin tila
bool buttonState = false;
bool lastButtonState = false;
unsigned long lastButtonPress = 0;
const unsigned long DEBOUNCE_DELAY = 500; // 500ms debounce

// Silmien parametrit
int leftEyeX = SCREEN_WIDTH / 4;
int leftEyeY = SCREEN_HEIGHT / 2;
int rightEyeX = 3 * SCREEN_WIDTH / 4;
int rightEyeY = SCREEN_HEIGHT / 2;
int eyeRadius = 10;
int pupilRadius = 4;
int pupilOffsetX = 0;
int pupilOffsetY = 0;

// Animaatiot
String currentEyeState = "center";
unsigned long lastAnimationTime = 0;
unsigned long lastStatusUpdate = 0;

// 433MHz koodit (SAMAT kuin palvelimessa!)
const unsigned long SMOKE_ON_CODE = 12345;
const unsigned long SMOKE_OFF_CODE = 54321;
const unsigned long SMOKE_PULSE_CODE = 11111;

// Tilastot
unsigned long totalSmokeCommands = 0;
unsigned long bootTime = 0;

void setup() {
  Serial.begin(115200);
  Serial.println("🤖 Robotti-kaukolaukaisin v3.0 - 433MHz");
  
  // GPIO setup
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(STATUS_LED_PIN, OUTPUT);
  
  // 433MHz Radio setup
  mySwitch.enableTransmit(RADIO_TX_PIN);
  mySwitch.setRepeatTransmit(3); // Lähetä 3 kertaa varmuudeksi
  Serial.println("📻 433MHz lähettäjä päällä pin " + String(RADIO_TX_PIN));
  
  // OLED setup
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println("❌ OLED ei toimi!");
    while (1) {
      // Vilkuta LED jos OLED ei toimi
      digitalWrite(STATUS_LED_PIN, HIGH);
      delay(200);
      digitalWrite(STATUS_LED_PIN, LOW);
      delay(200);
    }
  }
  
  Serial.println("📺 OLED käynnistetty");
  
  // Alustus-animaatio
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  display.setCursor(0, 0);
  display.println("ROBOTTI v3.0");
  display.println("433MHz Ready!");
  display.display();
  delay(2000);
  
  bootTime = millis();
  drawEyes();
  
  Serial.println("🚀 Robotti valmis!");
  blinkLED(3); // 3 vilkutusta = valmis
}

void loop() {
  // Tarkista nappi
  checkButton();
  
  // Päivitä silmä-animaatiot
  updateEyeAnimations();
  
  // Päivitä status-info
  updateStatusDisplay();
  
  delay(50); // 20 FPS
}

void checkButton() {
  bool currentState = (digitalRead(BUTTON_PIN) == LOW); // Pull-up = LOW kun painettu
  
  // Debounce
  if (currentState != lastButtonState) {
    lastButtonState = currentState;
    
    if (currentState && (millis() - lastButtonPress > DEBOUNCE_DELAY)) {
      // Nappi painettu!
      onButtonPressed();
      lastButtonPress = millis();
    }
  }
}

void onButtonPressed() {
  Serial.println("🔴 Nappi painettu - lähetetään savukone-komento!");
  
  // Lähetä 433MHz signaali
  mySwitch.send(SMOKE_PULSE_CODE, 24); // 24-bit koodi
  
  totalSmokeCommands++;
  
  // OLED palaute
  showSmokeConfirmation();
  
  // LED palaute
  blinkLED(1);
  
  // Serial debug
  Serial.println("📻 433MHz lähetetty: " + String(SMOKE_PULSE_CODE));
}

void showSmokeConfirmation() {
  // Tallenna nykyinen tila
  String previousState = currentEyeState;
  
  // Näytä vahvistus
  display.clearDisplay();
  display.setTextSize(2);
  display.setTextColor(WHITE);
  
  // Keskitä teksti
  int16_t x1, y1;
  uint16_t w, h;
  display.getTextBounds("SMOKE", 0, 0, &x1, &y1, &w, &h);
  display.setCursor((SCREEN_WIDTH - w) / 2, 5);
  display.println("SMOKE");
  
  display.getTextBounds("SENT!", 0, 0, &x1, &y1, &w, &h);
  display.setCursor((SCREEN_WIDTH - w) / 2, 20);
  display.println("SENT!");
  
  display.display();
  
  // Näytä 2 sekuntia
  delay(2000);
  
  // Palaa takaisin silmiin
  currentEyeState = previousState;
  drawEyes();
}

void updateEyeAnimations() {
  // Automaattinen silmien liike jos ei manuaalista toimintaa
  if (millis() - lastAnimationTime > 5000) { // 5s välein
    // Satunnainen silmä-animaatio
    int randomAnim = random(0, 6);
    
    switch (randomAnim) {
      case 0: setEyeState("center"); break;
      case 1: setEyeState("left"); break;
      case 2: setEyeState("right"); break;
      case 3: setEyeState("up"); break;
      case 4: setEyeState("down"); break;
      case 5: setEyeState("blink"); break;
    }
    
    lastAnimationTime = millis();
  }
}

void updateStatusDisplay() {
  if (millis() - lastStatusUpdate > 10000) { // 10s välein näytä status
    showStatusInfo();
    lastStatusUpdate = millis();
  }
}

void showStatusInfo() {
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(WHITE);
  
  display.setCursor(0, 0);
  display.println("ROBOTTI STATUS:");
  
  display.setCursor(0, 10);
  display.println("Uptime: " + String((millis() - bootTime) / 1000) + "s");
  
  display.setCursor(0, 20);
  display.println("Smoke cmds: " + String(totalSmokeCommands));
  
  display.display();
  delay(3000); // Näytä 3s
  
  // Takaisin silmiin
  drawEyes();
}

void setEyeState(String state) {
  currentEyeState = state;
  
  if (state == "center") {
    pupilOffsetX = 0;
    pupilOffsetY = 0;
  } else if (state == "left") {
    pupilOffsetX = -(eyeRadius - pupilRadius - 2);
    pupilOffsetY = 0;
  } else if (state == "right") {
    pupilOffsetX = (eyeRadius - pupilRadius - 2);
    pupilOffsetY = 0;
  } else if (state == "up") {
    pupilOffsetX = 0;
    pupilOffsetY = -(eyeRadius - pupilRadius - 2);
  } else if (state == "down") {
    pupilOffsetX = 0;
    pupilOffsetY = (eyeRadius - pupilRadius - 2);
  } else if (state == "blink") {
    drawBlink();
    delay(200);
    return; // Ei päivitä drawEyes() heti
  }
  
  drawEyes();
}

void drawEyes() {
  display.clearDisplay();
  
  // Jos WiFi ei toimi, näytä X X silmät (kuten kuvassa!)
  if (WiFi.status() != WL_CONNECTED) {
    drawDisconnectedEyes();
    return;
  }
  
  // Vasen silmä (kehys)
  display.drawCircle(leftEyeX, leftEyeY, eyeRadius, WHITE);
  // Vasen pupilli
  display.fillCircle(leftEyeX + pupilOffsetX, leftEyeY + pupilOffsetY, pupilRadius, WHITE);
  
  // Oikea silmä (kehys)
  display.drawCircle(rightEyeX, rightEyeY, eyeRadius, WHITE);
  // Oikea pupilli
  display.fillCircle(rightEyeX + pupilOffsetX, rightEyeY + pupilOffsetY, pupilRadius, WHITE);
  
  display.display();
}

void drawDisconnectedEyes() {
  // X X silmät kun yhteys poikki (kuten kuvassa!)
  display.clearDisplay();
  
  // Vasen X
  display.drawLine(leftEyeX - 8, leftEyeY - 8, leftEyeX + 8, leftEyeY + 8, WHITE);
  display.drawLine(leftEyeX - 8, leftEyeY + 8, leftEyeX + 8, leftEyeY - 8, WHITE);
  
  // Oikea X  
  display.drawLine(rightEyeX - 8, rightEyeY - 8, rightEyeX + 8, rightEyeY + 8, WHITE);
  display.drawLine(rightEyeX - 8, rightEyeY + 8, rightEyeX + 8, rightEyeY - 8, WHITE);
  
  // Tekstiä alle
  display.setTextSize(1);
  display.setCursor(0, 24);
  display.setTextColor(WHITE);
  display.println("NO CONNECTION");
  
  display.display();
}

void drawBlink() {
  display.clearDisplay();
  
  // Piirretään vaakaviivat silmien tilalle
  display.drawLine(leftEyeX - eyeRadius, leftEyeY, leftEyeX + eyeRadius, leftEyeY, WHITE);
  display.drawLine(rightEyeX - eyeRadius, rightEyeY, rightEyeX + eyeRadius, rightEyeY, WHITE);
  
  display.display();
}

void blinkLED(int times) {
  for (int i = 0; i < times; i++) {
    digitalWrite(STATUS_LED_PIN, HIGH);
    delay(150);
    digitalWrite(STATUS_LED_PIN, LOW);
    delay(150);
  }
}

// Test-funktio 433MHz:ille (serial komentoja varten)
void serialCommands() {
  if (Serial.available()) {
    String command = Serial.readString();
    command.trim();
    
    if (command == "test_smoke") {
      onButtonPressed();
    } else if (command == "test_on") {
      mySwitch.send(SMOKE_ON_CODE, 24);
      Serial.println("📻 Lähetetty: SMOKE_ON");
    } else if (command == "test_off") {
      mySwitch.send(SMOKE_OFF_CODE, 24);
      Serial.println("📻 Lähetetty: SMOKE_OFF");
    } else if (command.startsWith("eye_")) {
      String state = command.substring(4);
      setEyeState(state);
      Serial.println("👁️ Silmät: " + state);
    } else {
      Serial.println("❓ Komennot: test_smoke, test_on, test_off, eye_center, eye_left, eye_right, eye_up, eye_down, eye_blink");
    }
  }
}