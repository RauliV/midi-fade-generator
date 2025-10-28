# 🎭 Blender → Multiplay → Full Show Control

## Täysi näytelmäintegraatio: Valot + Savukoneet + Äänet

### 🎬 Sinun setup (ammattilaisjärjestelmä):
- **Multiplay** - Päämittaus: musiikki, äänet, HTTP-komennot, MIDI-sync  
- **Scene Setter** - Valot MIDI:llä (kanavat 1-40)
- **ESP32 Savukone** - WiFi HTTP API (kanavat 41-45)
- **Blender** - Visuaalinen simulaatio (valot + savut)

### 🌟 Käyttöohje: Yhtenäinen workflow

## 1. Suunnittele Blenderissä 🎨

**RGBW-ryhmät:**
- `RGBW 13-16` → Scene Setter kanavat 13,14,15,16 (R,G,B,W)
- `RGBW 17-20` → Scene Setter kanavat 17,18,19,20 (R,G,B,W)
- `RGBW 25-28` → Scene Setter kanavat 25,26,27,28 (R,G,B,W)

**Yksittäiset valot:**
- `21` → Scene Setter kanava 21
- `35` → Scene Setter kanava 35

**🌫️ Savukoneet (Blender-simulaatio):**
- `Smoke_Front_Left` → ESP32 HTTP (simuloi kanava 41)
- `Smoke_Front_Right` → ESP32 HTTP (simuloi kanava 42)  
- `Smoke_Back_Left` → ESP32 HTTP (simuloi kanava 43)
- `Smoke_Back_Right` → ESP32 HTTP (simuloi kanava 44)
- `Smoke_Center_Stage` → ESP32 HTTP (simuloi kanava 45)

## 2. Vie Mixed Export 🚀

Uusi exporter luo **molemmat**:
- **MIDI-tiedostot** valoille (Scene Setter)
- **HTTP-skriptit** savukoneille (ESP32)  
- **Multiplay Cue List** - Synkronoitu ohjaus

```bash
cd /Users/raulivirtanen/Documents/valot/blender-integration
python3 multiplay_full_export.py
```

## 3. Multiplay Setup 🎮

**Cue struktuuri:**
```
Cue 1.0: Fade In Lights (MIDI)
  ↳ Scene Setter: fade_in.mid
  
Cue 1.5: Start Smoke (HTTP) 
  ↳ HTTP: POST http://esp32-smoke.local/api/smoke/on
  
Cue 2.0: Audio + Sync
  ↳ Sound: musik.wav
  ↳ MIDI: light_sequence.mid
  ↳ HTTP: POST http://esp32-smoke.local/api/pulse/3
  
Cue 3.0: Fade Out All
  ↳ MIDI: fade_out.mid  
  ↳ HTTP: POST http://esp32-smoke.local/api/smoke/off
```

## 4. ESP32 Savukone-projekti 🌫️

### Hardware:
- ESP32 Dev Board
- Relay Module (savukone ohjaus)  
- WiFi network connectivity
- Power supply

### Software API:
```
POST /api/smoke/on       # Savukone päälle
POST /api/smoke/off      # Savukone pois  
POST /api/pulse/N        # N sekunnin pulssi
GET  /api/status         # Tila-check
```

### Integration:
- **IP-osoite**: `esp32-smoke.local` tai `192.168.1.XXX`
- **Multiplay HTTP Cues** - Suora ohjaus
- **Blender simulaatio** - Näyttää savun visuaalisesti

### 2. Aja Exporter-skripti 🚀

#### Tapa A: Blenderin sisällä
1. Avaa Blender
2. Vaihda Scripting-työalueeseen
3. Text Editor → Open → `blender_live_exporter.py`
4. Paina **Run Script**
5. Katso Console-tulosteet

#### Tapa B: Komentoriviltä (edistyneet)
```bash
cd /Users/raulivirtanen/Documents/valot/blender-integration
python3 blender_to_multiplay.py
```

### 3. Luo MIDI-tiedostot 🎵

Exporter luo JSON-tiedoston. Muunna se MIDI:ksi:

```bash
cd /Users/raulivirtanen/Documents/valot
python3 midimaker5.py BlenderLive_Setup.json
```

Saat tiedostot:
- `BlenderLive_fade_in.mid`
- `BlenderLive_fade_out.mid`

### 4. Siirrä Multiplayhin 🎮

1. Kopioi `.mid`-tiedostot Windows-koneeseen
2. Avaa Multiplay
3. Yhdistä Scene Setter USB:iin
4. Lataa fade_in.mid Multiplayhin
5. Paina Play → valot syttyvät täsmälleen kuten Blenderissä! 🌈

## Esimerkkitilanne 💡

**Blenderissä:**
- `RGBW 13-16`: energia 150W, väri (1.0, 0.5, 0.2) = oranssi
- `21`: energia 200W, väri (0.0, 0.0, 1.0) = sininen

**Tulos:**
- Kanavat 13,14,15,16 saavat RGBW-jaon oranssista väristä
- Kanava 21 saa täyden sinisen intensiteetin

**Multiplayssa:**
- Scene Setter sytyttää valot täsmälleen samassa intensiteetissä!

## Vinkit 💡

- **Energia 0** = valo sammuksissa (ei mukaan MIDI:iin)
- **Värit**: RGB-analyysistä päätellään RGBW-jakautuma
- **Max energia**: 300W (muokkaa koodista tarvittaessa)
- **Fade-ajat**: 2s in / 3s out (muokattavissa)

## Vianetsintä 🔧

**"Ei tunnistettu kanavaa"** → Tarkista valon nimi
**"Ei valoja löytynyt"** → Aseta energy > 0 Blenderissä  
**JSON ok, mutta ei MIDI** → Aja midimaker5.py erikseen
**MIDI ok, mutta valot ei syty** → Tarkista Scene Setter yhteys

---

✨ **Nyt sinulla on täydellinen putki: Blender → JSON → MIDI → Multiplay → Scene Setter → Valot!** 🎉