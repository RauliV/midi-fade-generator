# 🎭 MIDI Light Controller - Blender Add-on

## 📦 Asennus

### 1. Lataa lisäosa
- Tiedosto: `midi_light_controller.py`
- Sijainti: `/Users/raulivirtanen/Documents/valot/blender-integration/`

### 2. Asenna Blenderiin
1. **Avaa Blender**
2. **Edit** → **Preferences** (tai `Cmd+,` macOS:ssä)
3. **Add-ons** -välilehti
4. **Install...** -nappi
5. **Valitse** `midi_light_controller.py` tiedosto
6. **Install Add-on** 
7. **Rastita** "MIDI Light Controller" käyttöön

### 3. Löydä paneeli
- **3D Viewport** (pääikkuna)
- Paina **N** (tai View → Sidebar)
- Uusi välilehti: **"MIDI Lights"** 🎵

## 🎯 Käyttö

### Pääpaneeli
- **Status**: Näyttää onko `mido` asennettu
- **Install mido**: Asentaa puuttuvan kirjaston
- **Clear Animation**: Tyhjentää vanhat keyframet
- **Create Test Lights**: Luo värikkäitä testivaloja

### MIDI Import
```
📁 MIDI File: [polku MIDI-tiedostoon]
🎬 FPS: 24
⚡ Max Wattage: 300W
🌈 RGBW Groups: ☑️

[Import MIDI Animation] 🎵
```

### JSON Export  
```
📁 Output JSON: [vientitiedoston polku]
🎭 Scene Name: "BlenderScene"
⬆️ Fade In: 2.0s
⬇️ Fade Out: 3.0s  
📊 Steps: 20

[Export Blender Setup] 📤
```

## 🚀 Tyypillinen workflow

### 1. MIDI → Blender
1. **Clear Animation** (tyhjennä vanhat)
2. **Aseta MIDI-tiedoston polku**
3. **Import MIDI Animation**
4. **Paina SPACE** → Katso animaatio! 🎬

### 2. Blender → JSON → MIDI
1. **Säädä valot** Blenderissä (energia + värit)
2. **Export Blender Setup** 
3. **Terminaalissa**: `python3 midimaker5.py BlenderExport.json`
4. **Siirrä** .mid-tiedostot Multiplayhin! 🎮

### 3. Ongelmanratkaisu
- **Mustat valot**: **Create Test Lights** → vaihda Viewport tilaa
- **Vanhat animaatiot**: **Clear Animation** ennen uutta tuontia
- **mido puuttuu**: **Install mido** -nappi

## 🎨 Viewport-asetukset

Blenderin oikeassa yläkulmassa pallot:
- ⚫ **Solid** = ei värejä
- 🔘 **Material Preview** = ⭐ **PARAS** ⭐  
- 🌐 **Rendered** = hieno mutta hidas

## 💡 Vinkkejä

### Valojen nimeäminen
```
RGBW 13-16  → Scene Setter kanavat 13,14,15,16
RGBW 17-20  → Scene Setter kanavat 17,18,19,20
21          → Scene Setter kanava 21
35          → Scene Setter kanava 35
```

### MIDI-tiedostot
- **fade_in.mid** = valot syttyvät
- **fade_out.mid** = valot sammuvat  
- Löydät ne: `/Users/raulivirtanen/Documents/valot/generated_midi/`

### Multiplay-käyttö
1. **Windows-kone**: Lataa Multiplay
2. **Siirrä**: .mid-tiedostot USB:llä
3. **Yhdistä**: Scene Setter USB-porttiin
4. **Toista**: MIDI → valot syttyvät! 🌈

---

## 🔧 Kehittyneet ominaisuudet

### Custom-polut
Voit vaihtaa oletuspolkuja lisäosan asetuksista:
- MIDI input polku
- JSON output polku
- Scene-nimet

### RGBW vs. Single
- **RGBW Groups**: 4 kanavaa per valo (R,G,B,W)
- **Single**: 1 kanava per valo

### Batch-käsittely
1. **Export** useita kohtauksia samaan JSON:iin
2. **Käytä** `midimaker5.py` luomaan kaikki MIDI:t kerralla

---

✨ **Nyt sinulla on täydellinen Blender-integraatio MIDI-valojärjestelmään!** 🎉