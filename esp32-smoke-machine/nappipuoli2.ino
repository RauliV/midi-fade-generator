#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <WiFi.h>          // WiFi-tuki (olettaen ESP32 tai ESP8266)
#include <HTTPClient.h>    // HTTP-client

const char* ssid = "YourNetworkName";
const char* password = "YourPassword";
const int buttonPin = 27;
int buttonState = 0;

const String serverUrl = "http://192.168.4.1/get-eye-state";  
const String serverUrlPost = "http://192.168.4.1/set-eye-state"; 

long randNumber;

// Näytön mitat
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, -1);

// Silmien parametrit
int leftEyeX = SCREEN_WIDTH / 4;
int leftEyeY = SCREEN_HEIGHT / 2;
int rightEyeX = 3 * SCREEN_WIDTH / 4;
int rightEyeY = SCREEN_HEIGHT / 2;

int eyeRadius = 10;
int pupilRadius = 4;

int pupilOffsetX = 0;
int pupilOffsetY = 0;

// Nykyinen tila (aluksi center)
String currentState = "center";

const int smokePin = 27;
const int pollFrequency = 500;


void setup() {
  Serial.begin(115200);
  randomSeed(analogRead(0));
  
  //Näytön alustus
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    for (;;);
  }
  // Painikkeen pin, johon ohjataan virta, kun painiketta painetaan.
  pinMode(smokePin, INPUT);

  // Yhdistä WiFi:hen
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
    moveEyesUnconscious();
  }
  Serial.println("Connected to WiFi");

  display.clearDisplay();
  drawEyes();
  display.display();
}



void loop() {

  randNumber = random(1500);
  if (randNumber < 60) {
    if (randNumber < 10) moveEyesBlink();
    if ((randNumber > 10) && (randNumber < 20)) moveEyesRoll();
    if ((randNumber > 20) && (randNumber < 30)) moveEyesUp();
    if ((randNumber > 30) && (randNumber < 40)) moveEyesDown();
    if ((randNumber > 40) && (randNumber < 50)) moveEyesLeft();
    if ((randNumber > 50) && (randNumber < 60)) moveEyesRight();
    if ((randNumber > 60) && (randNumber < 70)) moveEyesUnconscious();
    if ((randNumber > 70) && (randNumber < 80)) moveEyesSleepy();
    


    delay(500);
    moveEyesCenter();
  }

  // Pollaa serveriä tilan saamiseksi 
  if (WiFi.status() == WL_CONNECTED) {
    buttonState = digitalRead(buttonPin);
    if (buttonState == HIGH) {
      Serial.println(postIt("smoke"));
      while (buttonState == HIGH) {
        buttonState = digitalRead(buttonPin);
        drawSmoke();
      }
    Serial.println(postIt("center"));

    }

    //Hae silmien tila palvelimelta
    HTTPClient http;
    http.begin(serverUrl.c_str());
    int httpCode = http.GET();

    if (httpCode > 0) {
      String payload = http.getString();
      int stateIndex = payload.indexOf("\"state\":\"") + 12;
      int endIndex = payload.indexOf("\"", stateIndex);
      String newState = payload.substring(stateIndex, endIndex);
      Serial.println(newState);

    if (newState != currentState) {
      currentState = newState;
      executeEyeState(newState);
      Serial.println(postIt(newState));
      if ((newState != "smoke") && (currentState != "smoke")) delay(1000);
      currentState = "center";
      executeEyeState(currentState);
      Serial.println(postIt("center"));
    }
    http.end();
  }
  delay(pollFrequency);  // Pollausväli
  }
}


//Apufunktioita

//Postaa palvelimelle tiedon tilasta, joka annettu parametrina
int postIt(String state){
  HTTPClient httpP;
  httpP.begin(serverUrlPost.c_str());
  httpP.addHeader("Content-Type", "application/json");
  httpP.addHeader("Accept",  "*/*");
  httpP.addHeader("Connection",  "keep-alive");
  int httpResponseCode = httpP.POST("{\"state\": \"" + state + "\"}");
  httpP.end();
  return (httpResponseCode);
}



// Funktio tilan suorittamiseen
void executeEyeState(String state) {
  if (state == "left") moveEyesLeft();
  else if (state == "right") moveEyesRight();
  else if (state == "up") moveEyesUp();
  else if (state == "down") moveEyesDown();
  else if (state == "center") moveEyesCenter();
  else if (state == "blink") moveEyesBlink();
  else if (state == "roll") moveEyesRoll();
  else if (state == "unconscious") moveEyesUnconscious(); 
  else if (state == "sleepy") moveEyesSleepy(); 
}

void drawEyes() {
  display.clearDisplay();
  
  display.drawCircle(leftEyeX, leftEyeY, eyeRadius, SSD1306_WHITE);
  display.fillCircle(leftEyeX + pupilOffsetX, leftEyeY + pupilOffsetY, pupilRadius, SSD1306_WHITE);
  
  display.drawCircle(rightEyeX, rightEyeY, eyeRadius, SSD1306_WHITE);
  display.fillCircle(rightEyeX + pupilOffsetX, rightEyeY + pupilOffsetY, pupilRadius, SSD1306_WHITE);
  
  display.display();
}

void moveEyesLeft() {
  pupilOffsetX = - (eyeRadius - pupilRadius - 2);
  pupilOffsetY = 0;
  drawEyes();
}

void moveEyesRight() {
  pupilOffsetX = (eyeRadius - pupilRadius - 2);
  pupilOffsetY = 0;
  drawEyes();
}

void moveEyesUp() {
  pupilOffsetX = 0;
  pupilOffsetY = - (eyeRadius - pupilRadius - 2);
  drawEyes();
}

void moveEyesDown() {
  pupilOffsetX = 0;
  pupilOffsetY = (eyeRadius - pupilRadius - 2);
  drawEyes();
}

void moveEyesCenter() {
  pupilOffsetX = 0;
  pupilOffsetY = 0;
  drawEyes();
}

void moveEyesBlink() {
  display.clearDisplay();
  
  display.drawLine(leftEyeX - eyeRadius, leftEyeY, leftEyeX + eyeRadius, leftEyeY, SSD1306_WHITE);
  display.drawLine(rightEyeX - eyeRadius, rightEyeY, rightEyeX + eyeRadius, rightEyeY, SSD1306_WHITE);
  
  display.display();
  delay(200);
  drawEyes();
}

void moveEyesRoll() {
  int rollRadius = eyeRadius - pupilRadius - 2;
  int steps = 8;
  
  for (int i = 0; i < steps; i++) {
    float angle = 2 * PI * i / steps;
    pupilOffsetX = rollRadius * cos(angle);
    pupilOffsetY = rollRadius * sin(angle);
    drawEyes();
    delay(150);
  } 
  moveEyesCenter();
}

void moveEyesUnconscious() {
  display.clearDisplay();
  
  // Piirrä 'X' vasemmalle silmälle
  display.drawLine(leftEyeX - eyeRadius, leftEyeY - eyeRadius, leftEyeX + eyeRadius, leftEyeY + eyeRadius, SSD1306_WHITE);
  display.drawLine(leftEyeX + eyeRadius, leftEyeY - eyeRadius, leftEyeX - eyeRadius, leftEyeY + eyeRadius, SSD1306_WHITE);
  
  // Piirrä 'X' oikealle silmälle
  display.drawLine(rightEyeX - eyeRadius, rightEyeY - eyeRadius, rightEyeX + eyeRadius, rightEyeY + eyeRadius, SSD1306_WHITE);
  display.drawLine(rightEyeX + eyeRadius, rightEyeY - eyeRadius, rightEyeX - eyeRadius, rightEyeY + eyeRadius, SSD1306_WHITE);
  
  display.display();
  delay(500);
  moveEyesCenter();

}

// Funktio puolinukuksissa oloon: Luomet lerpallaan (puoliavoimet luomet, yläluomi puoliksi alas)
void moveEyesSleepy() {
  display.clearDisplay();
  
  // Piirrä silmät normaalisti, mutta ilman pupilleja 
  display.drawCircle(leftEyeX, leftEyeY, eyeRadius, SSD1306_WHITE);  // Silmämuna vasen
  display.drawCircle(rightEyeX, rightEyeY, eyeRadius, SSD1306_WHITE);  // Silmämuna oikea
    
  // Yläluomi vasen: kaareva viiva approx linjoilla 
  display.drawLine(leftEyeX - eyeRadius, leftEyeY - (eyeRadius / 2), leftEyeX, leftEyeY - (eyeRadius / 2) - 2, SSD1306_WHITE);
  display.drawLine(leftEyeX, leftEyeY - (eyeRadius / 2) - 2, leftEyeX + eyeRadius, leftEyeY - (eyeRadius / 2), SSD1306_WHITE);
  
  // Yläluomi oikea
  display.drawLine(rightEyeX - eyeRadius, rightEyeY - (eyeRadius / 2), rightEyeX, rightEyeY - (eyeRadius / 2) - 2, SSD1306_WHITE);
  display.drawLine(rightEyeX, rightEyeY - (eyeRadius / 2) - 2, rightEyeX + eyeRadius, rightEyeY - (eyeRadius / 2), SSD1306_WHITE);
  
  // Pienehköt pupillit alempana (kuvaamaan uneliaisuutta)
  display.fillCircle(leftEyeX + pupilOffsetX, leftEyeY + (eyeRadius / 2), pupilRadius / 2, SSD1306_WHITE);  // Pieni pupilli alempana vasen
  display.fillCircle(rightEyeX + pupilOffsetX, rightEyeY + (eyeRadius / 2), pupilRadius / 2, SSD1306_WHITE);  // Pieni pupilli alempana oikea
  
  display.display();
  delay(500);
  moveEyesCenter();
}


void drawSmoke() {
  display.clearDisplay();
  drawEyes();
  
  // Lisää savu (yksinkertainen viivojen animaatio nousevasta savusta pään yläpuolella)
  for (int frame = 0; frame < 5; frame++) {  // Yksinkertainen loop animaatiolle
    display.clearDisplay();
    drawEyes();  // Pidä silmät näkyvissä
    
    // Savu-viivat (nousevat käyrät keskeltä ylös)
    int smokeX = SCREEN_WIDTH / 2;
    int smokeY = SCREEN_HEIGHT / 4;  // Aloita yläosasta
    display.drawLine(smokeX - 5, smokeY, smokeX - 10, smokeY - 10 + frame * 2, SSD1306_WHITE);
    display.drawLine(smokeX, smokeY, smokeX + 5, smokeY - 15 + frame * 2, SSD1306_WHITE);
    display.drawLine(smokeX + 5, smokeY, smokeX + 10, smokeY - 10 + frame * 2, SSD1306_WHITE);
    
    display.display();
   // delay(200);  // Animaation nopeus
  }
  display.clearDisplay();
  drawEyes();  // Pidä silmät näkyvissä
  display.display();
}