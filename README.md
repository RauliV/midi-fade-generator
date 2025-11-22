# 🎭 Professional Theater Control System

**MIDI-based lighting and effects control for live theater production**

Built for Nokun Näyttämö's production of "Tankki Täyteen" - a comprehensive system combining MIDI lighting control, wireless smoke machines, and 3D-printed backup controllers.

## 🎯 What This Is

**Professional theater lighting system** with three main components:

1. **🎵 MIDI Light Control** - Generate complex lighting sequences using MIDI files
2. **💨 ESP32 Smoke Machines** - Wireless effects control with WiFi backup
3. **🤖 Bruno Robot** - 3D-printed physical backup controller for critical moments

## 🚀 Quick Start

```bash
# Generate MIDI lighting sequences
python midimaker.py

# Export to professional Multiplay software  
python multiplay_full_export.py

# Flash ESP32 smoke machine firmware
platformio run --target upload
```

## 🏗️ System Architecture

### Hardware Stack
- **Scene Setter 48** DMX controller → 22 theater lights (6 RGBW groups)
- **Multiplay software** → Professional show management
- **ESP32 modules** → Wireless smoke machine control
- **Bruno robot** → Physical backup controller (3D printed)

### Software Stack
- **Python MIDI generation** → Complex lighting sequences
- **Blender integration** → 3D visualization and export
- **ESP32 firmware** → Wireless control with HTTP APIs
- **Web interfaces** → Real-time system monitoring

## 📁 Key Projects

| Directory | Purpose | Technology |
|-----------|---------|------------|
| `esp32-smoke-machine/` | Wireless effects control | ESP32, WiFi, 433MHz |
| `3d-models/bruno-robot/` | Physical backup controller | 3D printing, electronics |
| `blender-integration/` | 3D visualization | Blender, Python |
| `multiplay_full_export.py` | Professional theater export | MIDI, HTTP APIs |

## 🎭 Live Theater Proven

**Successfully used in production** at Nokun Näyttämö:
- ✅ **22 synchronized lights** with complex sequences
- ✅ **Wireless smoke effects** with physical backup
- ✅ **Real-time MIDI generation** responsive to performance
- ✅ **Professional documentation** for theater technicians

## 🛠️ For Developers

**Skills demonstrated:**
- **Systems Integration:** Hardware + software + real-time performance
- **3D Design & Manufacturing:** CAD modeling, 3D printing, electronics
- **Professional Documentation:** Theater-ready specifications
- **Reliability Engineering:** Backup systems for live performance

---

*This system powers live theater lighting where failure is not an option.*

### 🎵 MIDI Generation (Electron App v1.1.6)
- Professional fade-in/fade-out generation  
- Scene Setter hardware compatibility (channels 1-40)
- Cross-platform desktop application (Windows/macOS)
- Real-time preview and debug logging

### 🎨 Blender Integration (NEW!)
- **RGBW Color Mixing**: Realistic 4-channel light simulation  
- **Visual Show Design**: Plan light shows in 3D environment
- **Bidirectional Workflow**: MIDI ↔ Blender ↔ JSON
- **Professional Add-on**: Full GUI in Blender's N-panel
- **Smart Light Detection**: Works with existing Blender setups

### 🎯 Advanced Features
- ✅ **Solved RGBW Problem**: Multiple MIDI channels per light fixture
- ✅ **Round-trip Support**: Perfect color preservation  
- ✅ **Intelligent Mapping**: "RGBW 33-36" format support
- ✅ **Realistic Physics**: Scene Setter intensity scaling

## 🚀 Quick Start

### 1. MIDI Generation
```bash
# Desktop app
open midi-fade-generator.app  # macOS
# or Windows: midi-fade-generator.exe

# Command line
cd midi-fade-generator && npm start
```

### 2. Blender Integration
```python
# Install add-on: blender-integration/midi_light_controller.py
# N-panel → MIDI Lights → Import MIDI Animation
```

### 3. Professional Workflow
```bash
python3 blender-integration/workflow_automation.py my_scenes.json
```

## 📁 Project Structure

```
├── 📱 midi-fade-generator/          # Electron app (v1.1.6)
├── 🎨 blender-integration/          # Blender system with RGBW
├── 🎵 Legacy Python/               # Original generators  
└── 📊 Testing/                     # Validation & examples
```

## 🎨 RGBW Breakthrough

**Problem Solved**: MIDI channel 35 (blue) now appears blue, not white!

**Technical Solution**: Mathematical color mixing algorithm that correctly handles 4-channel RGBW fixtures.

## 📚 Documentation

- 🎨 [RGBW Testing Guide](blender-integration/RGBW_TESTING_GUIDE.md)  
- 📖 [Add-on Installation](blender-integration/ADDON_INSTALLATION.md)
- 🔄 [Complete Workflow](blender-integration/MULTIPLAY_WORKFLOW.md)

---

## Legacy Build Instructions (Windows)

Alkuperäiset Windows-rakennusohjeet Python-sovellukselle:

```bash
pyinstaller --onefile --noconsole --icon=midi_lights.ico valot.py
```

- Kansioksi (onedir):

```bash
pyinstaller --onedir --noconsole --icon=midi_lights.ico valot.py
```

.spec‑tiedosto
- Projektissa on mukana myös `valot_with_uusiicon.spec` joka upottaa `uusi_ico.ico` tiedostona.
 Voit ajaa sen komennolla:

```bash
pyinstaller valot_with_uusiicon.spec
```

Tarvittaessa muokkaa `.spec`-tiedostoa (esim. `console=True` tai nimeä `name='valot'`).

Jos et pysty rakentamaan Windowsissa
- Korvaa icon jälkikäteen Windows‑koneella:
  - rcedit.exe: `rcedit.exe "C:\path\to\your.exe" --set-icon "C:\path\to\midi_lights.ico"`
  - Resource Hacker: avaa EXE ja korvaa icon manuaalisesti

Vahvistus
- Explorer saattaa välimuistittaa ikoneita. Jos et näe muutosta, käynnistä explorer uudelleen tai tyhjennä icon cache.

Lisätiedot
- Projektissa on mukana `build_windows.ps1` - PowerShell-skripti Windows-rakennusta varten.

PowerShell‑skripti (Windows) — esimerkki
```powershell
# Aja tämä PowerShellissa Windowsilla (avaa PowerShell projektikansiosta)
.
# Vaihda tarvittaessa polut ja asetukset
Set-StrictMode -Version Latest

param(
  [string]$SpecFile = 'valot_with_uusiicon.spec',
  [switch]$OneFile = $true
)

if ($OneFile) {
  pyinstaller --onefile --noconsole --clean $SpecFile
} else {
  pyinstaller --onedir --noconsole --clean $SpecFile
}

# Kopioi valmis exe talteen (esimerkki output-polku riippuen onedir/onefile)
if ($OneFile) {
  $exe = Join-Path -Path 'dist' -ChildPath 'valot.exe'
  Write-Host "Valmis: $exe"
} else {
  $outdir = Join-Path -Path 'dist' -ChildPath 'valot'
  Write-Host "Valmis kansio: $outdir"
}
```
