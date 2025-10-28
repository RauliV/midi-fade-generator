# 🎭 Blender MIDI Light Integration

Täydellinen integraatio MIDI-valoohjauksen ja Blenderin välillä. Mahdollistaa valoesitysten suunnittelun Blenderissä ja suoran viennin Multiplay-ohjelmaan Scene Setter -ohjausta varten.

## 🎯 Täydellinen Workflow

```
Blender → JSON → MIDI → Multiplay → Scene Setter → Valot
```

### ⭐ UUSI: Suora Multiplay-vienti
- **`blender_live_exporter.py`**: Vie Blender-setup suoraan Multiplayhin!
- Aseta valot Blenderissä → Saat valmiin MIDI:n → Siirrä Windowsiin → Valot syttyvät! 🌈
- Katso: [MULTIPLAY_WORKFLOW.md](MULTIPLAY_WORKFLOW.md)

### 1. JSON → MIDI (MIDI-generaattori)
- Lataa kohtaukset JSON-muodossa
- Luo fade-in/fade-out MIDI-tiedostot
- Scene Setter yhteensopiva (kanavat 1-40)

### 2. MIDI → Blender (`midi_to_blender.py`)
- Lukee MIDI-tiedoston
- Luo valoja automaattisesti
- Generoi keyframe-animaation
- Tukee RGBW-ryhmiä ja yksittäisiä spotteja

### 3. Blender → JSON (`blender_to_json.py`)
- Vie nykyisen valosetuppin JSON-muotoon
- Tunnistaa kanavat valojen nimistä
- Yhteensopiva MIDI-generaattorin kanssa

### 4. Blender → Multiplay (`blender_live_exporter.py`) ⭐ UUSI
- Vie Blender-setup suoraan käyttövalmiiksi MIDI:ksi
- Optimoitu Multiplay + Scene Setter -käyttöön
- Täydellinen RGBW-tuki

## 🛠️ Asennus

### Vaatimukset
- **Blender 3.0+**
- **Python 3.8+** 
- **mido-kirjasto**: `pip install mido`

### Blenderiin asennus
1. Avaa Blender
2. Window → Toggle System Console (Windows) tai Terminal (macOS)
3. Text Editor → New → Kopioi skripti
4. Muokkaa tiedostopolkuja tarpeen mukaan
5. Run Script

## 📋 Käyttöohje

### MIDI → Blender Tuonti

1. **Valmistele MIDI-tiedosto**
   - Luo kohtaus MIDI-generaattorilla
   - Tallenna fade-in.mid tai fade-out.mid

2. **Muokkaa asetuksia** (`midi_to_blender.py`):
   ```python
   MIDI_FILE_PATH = "/polku/tiedostoon.mid"
   FPS = 24
   MAX_WATTAGE = 300
   RGBW_GROUPS = True  # tai False yksittäisille spoteille
   ```

3. **Aja skripti Blenderissä**
   - Valot luodaan automaattisesti
   - Keyframet asetetaan velocity-arvojen mukaan
   - Animaatio valmis toistettavaksi!

### Blender → JSON Vienti

1. **Aseta valot haluamaasi tilaan**
   - Säädä energiat (0-300W)
   - Nimeä valot oikein (ks. nimeämiskäytännöt)

2. **Muokkaa asetuksia** (`blender_to_json.py`):
   ```python
   OUTPUT_PATH = "/polku/exported_scene.json"
   SCENE_NAME = "Oma_kohtaus"
   ```

3. **Aja skripti**
   - JSON-tiedosto luodaan
   - Voit ladata sen MIDI-generaattoriin

## 🏷️ Valojen Nimeämiskäytännöt

### RGBW-ryhmät (suositeltu)
```
RGBW_1_Red    → Kanava 1
RGBW_1_Green  → Kanava 2  
RGBW_1_Blue   → Kanava 3
RGBW_1_White  → Kanava 4
RGBW_2_Red    → Kanava 5
...
```

### Yksittäiset spotit
```
Spot_1   → Kanava 1
Spot_15  → Kanava 15
21       → Kanava 21
```

## ⚙️ Tekniset Yksityiskohdat

### MIDI-kanava Mappaus
- **MIDI-nuotti** = Kanava + 69
- **Kanava 1** = Nuotti 70
- **Kanava 40** = Nuotti 109

### Velocity ↔ Energia Muunnos
```python
# MIDI → Blender
energy_watts = (velocity / 127) * MAX_WATTAGE

# Blender → MIDI  
velocity = int((energy_watts / MAX_WATTAGE) * 127)
```

### RGBW-ryhmä Logiikka
- **4 kanavaa per ryhmä**: R, G, B, W
- **Ryhmä 1**: Kanavat 1-4
- **Ryhmä 2**: Kanavat 5-8
- **Ryhmä N**: Kanavat (N-1)*4+1 ... N*4

## 🎯 Esimerkkikäyttö

### 1. Luo kohtaus MIDI-generaattorilla
```json
{
  "name": "Tunnelma",
  "channels": {
    "1": 80,   // Red 63%
    "4": 40,   // White 31%
    "15": 127  // Spot 100%
  },
  "fade_in_duration": 3.0,
  "fade_out_duration": 2.0
}
```

### 2. Tuo Blenderiin
- Luo kolme valoa: `RGBW_1_Red`, `RGBW_1_White`, `Spot_15`
- Asettaa energiat: 189W, 95W, 300W
- Luo keyframe-animaation

### 3. Muokkaa Blenderissä
- Säädä värejä, sijainteja, kulmia
- Testaa eri valaistustiloja

### 4. Vie takaisin JSON:ksi
- Tallentaa nykyiset energia-arvot
- Voit luoda uusia MIDI-tiedostoja

## 🚀 Jatkokehitys

### Mahdollisia lisäominaisuuksia:
- **Reaaliaikainen ohjaus** Blenderistä Scene Setteriin
- **OSC-tuki** valonohjaussoftille
- **Värien vienti** (HSV → RGBW muunnos)
- **DMX512-tuki** ammattilaislaitteistolle
- **Äänireaktiivinen ohjaus**

## 📞 Tuki

Jos skriptit eivät toimi:

## 🎮 Multiplay-integraatio ⭐ UUSI

### Nopea käyttö
1. **Aseta valot Blenderissä** haluamaasi tilaan
2. **Aja** `blender_live_exporter.py` Blenderin Text Editorissa  
3. **Muunna MIDI:ksi**: `python3 midimaker5.py BlenderLive_Setup.json`
4. **Siirrä** .mid-tiedostot Multiplayhin Windowsissa
5. **Toista** → Valot syttyvät täsmälleen kuten Blenderissä! 🌈

### RGBW-tuki
- **Automaattinen värianalyysi**: RGB → RGBW-kanavat
- **Täysi Scene Setter -yhteensopivuus** (kanavat 1-40)
- **Helppo nimeäminen**: `RGBW 13-16`, `RGBW 17-20`, jne.

Katso: [MULTIPLAY_WORKFLOW.md](MULTIPLAY_WORKFLOW.md)

## 🔧 Vianetsintä

1. **Tarkista polut** - Käytä absoluuttisia polkuja
2. **Asenna mido** - `pip install mido`
3. **Blender-versio** - Vähintään 3.0
4. **Valotyypit** - Vain LIGHT-objektit tunnistetaan
5. **Kanava-alue** - Kanavat 1-40 tuettu
6. **Multiplay-ongelmat** - Varmista Scene Setter USB-yhteys

## 📄 Lisenssi

Sama lisenssi kuin MIDI-generaattorilla - käytä vapaasti!