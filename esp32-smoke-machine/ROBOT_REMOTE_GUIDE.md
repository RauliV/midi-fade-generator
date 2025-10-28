# 🤖 Robotti-kaukolaukaisin käyttöohje

## Yleiskatsaus
Robotti-kaukolaukaisin on mekaaninen teatteri-efekti joka yhdistää:
- **Nostettavan pään** joka paljastaa napin
- **OLED-näytön** joka simuloi silmiä  
- **WiFi-yhteyden** savupalvelimeen
- **Manuaalisen laukaisun** savukoneille

## 🔧 Hardware Setup

### Komponentit:
- **ESP32** (nappipuoli2.ino)
- **OLED SSD1306** (128x32 pikseliä)
- **Painonappi** (pin 27)
- **3D-tulostettu kotelo** (robotti-muoto)
- **WiFi-yhteys** savupalvelimeen

### Kytkentä:
```
ESP32 Pin  | Komponentti
-----------|------------
21 (SDA)   | OLED SDA
22 (SCL)   | OLED SCL  
27         | Painonappi (+ 10kΩ pull-up)
3.3V       | OLED VCC
GND        | OLED GND + Nappi GND
```

## 📡 WiFi-verkko

### Savupalvelin (ESP32 Access Point):
- **SSID**: "Noku"
- **Salasana**: "savuk0nel4uk"  
- **IP**: 192.168.4.1

### Robotti yhdistää automaattisesti:
- Skannaa "Noku" verkkoa
- Yhdistää salasanalla
- Näyttää OLED:ssa yhteyden tilan

## 🎭 Teatteri-workflow

### 1. Multiplay-ohjaus:
```json
{
  "cue": "Robot_Smoke_01",
  "channel": 41,
  "action": "smoke",
  "duration": 5
}
```

### 2. Manuaalinen laukaisu:
1. **Nosta** robotin päätä ylös
2. **Paina** paljastunutta nappia
3. **OLED näyttää**: "SMOKE SENT!"
4. **Savukone** aktivoituu 5 sekunniksi

### 3. Silmä-animaatiot:
- **Center**: Silmät keskellä (lepotila)
- **Left/Right**: Silmät sivulle (seuraa toimintaa)  
- **Up/Down**: Silmät ylös/alas (reaktiot)
- **Blink**: Vilkkuminen (huomio)
- **Roll**: Pyörittely (hämmennys)
- **Smoke**: Erikoisefekti savun kanssa

## 🎮 OLED-käyttöliittymä

### Normaali tila:
```
┌──────────────────┐
│  ( ● )    ( ● )  │  <- Silmät keskellä
│                  │
└──────────────────┘
```

### Smoke-tila:
```
┌──────────────────┐
│  ( ● )    ( ● )  │  <- Silmät
│    ~~~  ~~~     │  <- Savu-animaatio
└──────────────────┘
```

### Yhteys-info:
```
┌──────────────────┐
│ WiFi: Connected  │
│ Server: Online   │  
└──────────────────┘
```

## 🎪 Blender-simulaatio

### Robotti-objektit:
- **Robot_Head**: Pää (nostettava)
- **Robot_Body**: Vartalo
- **Robot_Button**: Nappi (piilossa)
- **OLED_Display**: Näyttö (silmät)

### Valojen mapping:
- **Kanava 46**: Robot_Eyes_Center
- **Kanava 47**: Robot_Eyes_Left  
- **Kanava 48**: Robot_Eyes_Right
- **Kanava 49**: Robot_Eyes_Up
- **Kanava 50**: Robot_Eyes_Down
- **Kanava 51**: Robot_Eyes_Blink
- **Kanava 52**: Robot_Eyes_Roll

### Savukoneet:
- **Kanava 41-45**: Savukoneet (laukaisevat myös silmä-animaation)

## 🔧 Konfigurointi

### nappipuoli2.ino muokkaukset:
```cpp
// WiFi-asetukset
const char* ssid = "Noku";  
const char* password = "savuk0nel4uk";

// Palvelimen osoite
const String serverUrl = "http://192.168.4.1/get-eye-state";
const String serverUrlPost = "http://192.168.4.1/set-eye-state";

// Napin pin
const int buttonPin = 27;
```

### Multiplay HTTP-komennot:
```bash
# Savukone päälle + silmä-efekti
curl -X POST http://192.168.4.1/set-eye-state \
  -H "Content-Type: application/json" \
  -d '{"state": "smoke"}'

# Silmät vasemmalle  
curl -X POST http://192.168.4.1/set-eye-state \
  -H "Content-Type: application/json" \
  -d '{"state": "left"}'
```

## 🎭 Käyttötapaukset

### 1. Dramaattinen sisääntulo:
1. Robotti lavalle → silmät `center`
2. Katsoo yleisöä → silmät `down`  
3. Hämmästyy → silmät `roll`
4. Laukaisee savun → `smoke` (manuaalisesti)

### 2. Multiplay-synkronointi:
1. Musiikki alkaa → Multiplay lähettää `robot_eyes_left`
2. Efekti-kohta → Multiplay lähettää `smoke_center_stage`  
3. Lopetus → Multiplay lähettää `robot_eyes_center`

### 3. Hätälaukaisu:
1. Näyttelijä nostaa robotin pään
2. Painaa nappia (pin 27)
3. Instant-savu aktivoituu
4. OLED näyttää vahvistuksen

## 🚀 Troubleshooting

### WiFi-ongelmat:
- Tarkista että "Noku" verkko on käynnissä
- Reboot robotti (power cycle)
- Tarkista salasana koodista

### OLED ei toimi:
- Tarkista I2C-kytkennät (SDA/SCL)
- Kokeile eri I2C-osoitetta (0x3C/0x3D)
- Tarkista 3.3V syöttö

### Nappi ei reagoi:
- Tarkista pull-up vastus (10kΩ)
- Testaa nappi multimetrillä
- Varmista pin 27 konfiguraatio

### Savukone ei laukea:
- Tarkista WiFi-yhteys palvelimeen
- Testaa HTTP POST manuaalisesti
- Tarkista savupalvelin2.ino pin 27 output

## ✅ Testauslista

- [ ] WiFi yhdistää "Noku" verkkoon
- [ ] OLED näyttää silmät oikein  
- [ ] Nappi lähettää HTTP POST
- [ ] Savukone reagoi `smoke` komentoon
- [ ] Multiplay-integraatio toimii
- [ ] Blender simuloi oikein
- [ ] Manuaalinen + automaattinen laukaisu toimii

Robotti-kaukolaukaisin on nyt valmis ammattimaiseen teatterikäyttöön! 🎪🤖