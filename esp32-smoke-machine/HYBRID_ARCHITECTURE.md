# 🎭 Paranneltu teatteri-arkkitehtuuri

## ⚠️ WiFi-konfliktien välttäminen

### Ongelma:
- Kaksi ESP32:ta samassa WiFi-verkossa → kaatumisia
- Multiplay + robotti-kaukolaukaisin konfliktoi

### 🚀 Ratkaisu: Hybrid-järjestelmä

## 🎪 Uusi arkkitehtuuri:

### 1. **Multiplay = Pääohjaus** (Ensisijainen)
```
Multiplay → WiFi → ESP32 Savupalvelin
    ↓
[Automaattinen show-ohjaus]
    ↓
HTTP POST /set-eye-state {"state": "smoke"}
```

### 2. **Robotti = Backup/Manual** (Toissijainen)
```
Robotti → Infrared/Radio → ESP32 Savupalvelin
    ↓
[Manuaalinen hätälaukaisu]  
    ↓
IR signal → smoke trigger
```

## 🔧 Tekniset ratkaisut:

### A) **IR-kommunikaatio** (Suositus):
```cpp
// Robotti lähettää IR-signaalia
IRsend irsend(IR_LED_PIN);
irsend.sendNEC(0x12345678, 32); // Smoke trigger code

// Savupalvelin vastaanottaa
IRrecv irrecv(IR_RECV_PIN);
if (irrecv.decode(&results)) {
    if (results.value == 0x12345678) {
        triggerSmoke();
    }
}
```

### B) **433MHz Radio** (Vaihtoehto):
```cpp
// Robotti: 433MHz lähettäjä
RCSwitch mySwitch = RCSwitch();
mySwitch.send("12345"); // Smoke code

// Savupalvelin: 433MHz vastaanotin  
if (mySwitch.available()) {
    if (mySwitch.getReceivedValue() == 12345) {
        triggerSmoke();
    }
}
```

### C) **Eri WiFi-kanavat** (Jos pysytään WiFi:ssä):
```cpp
// Savupalvelin: Kanava 1
WiFi.softAP(ssid, password, 1);

// Robotti: Yhdistää tavalliseen WiFi:hin (kanava 6+)
WiFi.begin(main_ssid, main_password);
```

## 🎭 Käytännön workflow:

### Normaali show:
1. **Multiplay** → HTTP → ESP32 → Savukone ✅
2. **Robotti OLED** → Näyttää show'n tilan
3. **Manuaalinen nappi** → Standby (ei käytössä)

### Hätätilanne:
1. **Multiplay kaatuu** → Robotti backup aktiiviseksi  
2. **Näyttelijä nostaa** robotin pään
3. **Painaa nappia** → IR/Radio → Savukone ✅

### Harjoitukset:
1. **Multiplay ei käytössä** → Robotti primary mode
2. **Jokainen napinpainallus** → suora laukaisu
3. **OLED feedback** → vahvistus toiminnasta

## 🔧 Koodimuutokset:

### savupalvelin2.ino:
```cpp
// Lisää IR/Radio vastaanotin
#include <IRremote.h>
IRrecv irrecv(14); // Pin 14 IR vastaanottimelle

void setup() {
    // ... WiFi setup ...
    irrecv.enableIRIn(); // IR-vastaanotin päälle
}

void loop() {
    server.handleClient();
    
    // Tarkista IR-komennot
    if (irrecv.decode(&results)) {
        if (results.value == SMOKE_IR_CODE) {
            triggerSmoke("IR_REMOTE");
        }
        irrecv.resume();
    }
}
```

### nappipuoli2.ino:
```cpp
// Lisää IR/Radio lähettäjä
#include <IRremote.h>
IRsend irsend(4); // Pin 4 IR LED

void sendSmokeCommand() {
    irsend.sendNEC(SMOKE_IR_CODE, 32);
    display.println("SMOKE SENT (IR)!");
    display.display();
}
```

## 🎯 Edut:

### 1. **Luotettavuus**:
- Multiplay = ensisijainen (vakaa)
- IR/Radio = backup (ei WiFi-konflikteja)

### 2. **Teatterikäytäntö**:
- Show-aikana: Automaattinen (Multiplay)
- Harjoituksissa: Manuaalinen (Robotti)
- Hätätilanteessa: Instant backup

### 3. **Tekninen**:
- Ei WiFi-kuormitusta
- Matala latenssi (IR/Radio)
- Itsenäiset järjestelmät

## 📋 Seuraavat askeleet:

1. **Valitse kommunikaatio**: IR vs 433MHz vs eri WiFi-kanavat
2. **Tilaa komponentit**: IR LED/Receiver tai 433MHz moduulit  
3. **Päivitä koodi**: Hybrid-tuki molempiin ESP32:iin
4. **Testaa luotettavuus**: Pitkäkestoiset ajot

Mikä ratkaisu tuntuu parhaalta sinun setupillesi? 🤔