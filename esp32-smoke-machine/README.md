# � ESP32 Teatteri-savukone + Robotti-kaukolaukaisin

Ammattimainen teatteri-järjestelmä joka yhdistää:
- **WiFi-savukoneet** HTTP API:lla  
- **Robotti-kaukolaukaisin** OLED-silmillä
- **Multiplay-integraatio** show-ohjaukseen
- **Blender-simulaatio** koko setupille

## 🎪 Järjestelmän osat

### 1. Savupalvelin (ESP32 Access Point)
- **Tiedosto**: `savupalvelin2.ino`
- **Tehtävä**: WiFi AP + HTTP API + silmä-simulaatio  
- **IP**: 192.168.4.1
- **Releet**: Pin 27 (savukone)

### 2. Robotti-kaukolaukaisin (ESP32 Client)  
- **Tiedosto**: `nappipuoli2.ino`
- **Tehtävä**: OLED-silmät + manuaalinen nappi
- **Komponentit**: SSD1306 OLED + painonappi
- **Yhteys**: WiFi client → savupalvelimeen
```
ESP32 GPIO 2  → Relay IN
ESP32 GND     → Relay GND  
ESP32 3.3V    → Relay VCC
Relay COM     → Savukone +
Relay NO      → Power +
Power GND     → Savukone -
```

## 💻 Software

### API Endpoints:
```
POST /api/smoke/on           # Savukone päälle  
POST /api/smoke/off          # Savukone pois
POST /api/pulse/{seconds}    # N sekunnin pulssi
GET  /api/status             # Tila ja info
GET  /api/config             # Asetukset
POST /api/config             # Päivitä asetukset
```

### Käyttö Multiplaysta:
```json
{
  "type": "http_post",
  "url": "http://esp32-smoke.local/api/pulse/3",
  "payload": {
    "intensity": 100,
    "duration": 3
  }
}
```

## 🎬 Integration

### Blender-simulaatio:
- Savukoneet näkyvät Blender Smoke Simulationina
- MIDI-kanavat 41-45 = HTTP-komennot
- Visuaalinen suunnittelu + ohjausdatan generointi

### Multiplay Workflow:
1. **Suunnittele** Blenderissä (valot + savut)
2. **Export** täysi setup (MIDI + HTTP)  
3. **Import** Multiplayhin
4. **Aja show** - kaikki synkronoituna!

## 📁 Tiedostot

```
esp32-smoke-machine/
├── README.md                # Tämä tiedosto
├── smoke_controller.ino     # Arduino ESP32 koodi
├── web_interface.html       # HTTP API hallinta
├── config.json             # Asetukset
├── multiplay_integration.md # Multiplay setup-ohje
└── blender_simulation.py   # Blender-simulaatio
```

## 🚀 Quick Start

### 1. Hardware Setup
1. Kytke ESP32 + Relay + Savukone
2. Lataa `smoke_controller.ino` ESP32:een
3. Configuroi WiFi (Serial Monitor)

### 2. Network Setup  
1. ESP32 yhdistää WiFi:hin
2. Saat IP-osoitteen (esim. 192.168.1.100)
3. Testaa: `curl http://192.168.1.100/api/status`

### 3. Multiplay Integration
1. Vie Blender → `multiplay_full_export.py`
2. Päivitä ESP32 IP cue listiin
3. Import Multiplayhin
4. Testaa HTTP-kutsut
5. Aja show! 🎉

## 🎯 Features

### Ohjaus:
- ✅ HTTP REST API  
- ✅ WiFi connectivity
- ✅ Relay-kontrolli
- ✅ Pulse-timing
- ✅ Status monitoring

### Integraatio:
- ✅ Multiplay HTTP cues
- ✅ Blender simulaatio  
- ✅ MIDI-sinkronointi
- ✅ Show-automaatio

### Turvallisuus:
- ✅ Timeout protection
- ✅ Manual override
- ✅ Status feedback
- ✅ Error handling

## 🔗 Linkki kokonaisprojektiin

Tämä ESP32-savukone on osa isompaa **MIDI Fade Generator** projektia:
- **Valot**: Scene Setter MIDI-ohjaus
- **Blender**: RGBW-värinsekoitus + simulaatio  
- **Electron**: Desktop MIDI-generaattori
- **Savukoneet**: Tämä ESP32-järjestelmä

→ **Täydellinen ammattilaisnäytelmäohjaus!** 🎭✨

---

**Built for professional theater control** ⚡  
*ESP32 + WiFi + Relay = Simple but powerful* 🌫️