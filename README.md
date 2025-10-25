# 🎵 MIDI Fade Generator - Cross-Platform Desktop App

Beautiful Electron desktop application for generating MIDI fade-in and fade-out files for lighting control systems. Available for Windows 10/11 and macOS (Intel & Apple Silicon).

![MIDI Fade Generator](assets/icon.png)

## Features

🖥️ **Native Desktop App**: Standalone application for Windows and macOS  
📁 **Native File Dialogs**: Browse directories with system file explorer  
💾 **Local Data Storage**: Presets saved locally on your computer  
🎭 **Full Scene Management**: All web version features included  
⚡ **Offline Operation**: No internet connection required  
� **Cross-Platform**: Windows .exe and macOS .dmg installers  
🎯 **No Dependencies**: Everything included, no Python or external libraries needed  

## Download & Installation

### Ready-to-Use Installers
Download from the `/dist` folder or create a GitHub release:

**Windows 10/11:**
- `MIDI Fade Generator Setup 1.0.0.exe` (97 MB)
- Includes installer and automatic desktop shortcuts

**macOS:**
- `MIDI Fade Generator-1.0.0.dmg` (116 MB) - Intel Macs
- `MIDI Fade Generator-1.0.0-arm64.dmg` (111 MB) - Apple Silicon Macs
- Drag & drop installation to Applications folder

**Updated:** Kaikki versiot nyt korjatuilla ikoneilla!

### For End Users
1. Download the appropriate installer for your system
2. **Windows**: Run the `.exe` installer and follow prompts
3. **macOS**: Open the `.dmg` file and drag to Applications
4. Launch from Start Menu (Windows) or Applications folder (macOS)

### For Developers

## Setup & Requirements

### Windows 10/11 Users
1. **Install Python**: Download Python 3.6+ from https://python.org (check "Add Python to PATH")
2. **Install MIDI library**: Run `pip install midiutil` in Command Prompt
3. **Download & Install**: Get the `.exe` installer from [Releases](https://github.com/RauliV/midi-fade-generator-electron/releases)
4. **Launch**: Find "MIDI Fade Generator" in Start Menu

### macOS Users  
1. **Download App**: Get the `.dmg` from [Releases](https://github.com/RauliV/midi-fade-generator-electron/releases)
2. **Launch**: Open from Applications folder
   - ✅ **Python Included**: macOS version has Python automatically handled

### Developer Setup
Prerequisites:
- **Node.js** (v16 or later)
- **Python 3.6+** with midiutil (`pip install midiutil`)
- **Git**

**Note**: Desktop applications use Python with midiutil for Logic Pro compatible MIDI generation.

```bash
git clone https://github.com/RauliV/midi-fade-generator.git
cd midi-fade-generator
npm install
```

## Building Desktop Applications

### Windows Build
```bash
npm run build-win
```
Creates: `dist/MIDI Fade Generator Setup 1.0.0.exe`

### macOS Build  
```bash
npm run build-mac
```
Creates: 
- `dist/MIDI Fade Generator-1.0.0.dmg` (Intel)
- `dist/MIDI Fade Generator-1.0.0-arm64.dmg` (Apple Silicon)

### Development Mode
```bash
npm start
```

## Creating GitHub Release

1. **Ensure builds are complete**:
   ```bash
   npm run build-win
   npm run build-mac
   ```

2. **Create release on GitHub**:
   - Go to repository → Releases → "Create a new release"
   - Tag: `v1.0.0`
   - Title: `MIDI Fade Generator v1.0.0 - Cross-Platform Desktop App`
   - Upload files from `dist/` folder:
     - `MIDI Fade Generator Setup 1.0.0.exe`
     - `MIDI Fade Generator-1.0.0.dmg`
     - `MIDI Fade Generator-1.0.0-arm64.dmg`

## Technical Details

### Architecture
- **Frontend**: HTML5/CSS3/JavaScript with neon purple theme
- **Backend**: Node.js with Electron framework
- **MIDI Generation**: Python midiutil library (Logic Pro compatible)
- **File System**: Native file dialogs and local storage
- **Packaging**: `electron-builder` for cross-platform builds

### Project Structure
```
midi-fade-generator/
├── index.html              # Web version
├── valot_server.py         # Web server
├── valot_python_backend.py # MIDI generation
├── electron-app/           # Desktop application
│   ├── main.js             # Electron main process
│   ├── preload.js          # Secure IPC bridge
│   ├── index.html          # Desktop UI
│   ├── package.json        # Build configuration
│   ├── valot_python_backend.py # MIDI backend
│   └── assets/             # Icons and resources
│       ├── icon.png
│       ├── icon.icns       # macOS
│       └── icon.ico        # Windows
└── generated_midi/         # Output folder
```

Development commands:
```bash
# Run in development mode
npm run dev

# Start application
npm start

# Build Windows installer
npm run build-win
```

## Features Comparison

| Feature | Web Version | Electron Version |
|---------|-------------|------------------|
| MIDI Generation | ✅ | ✅ |
| Scene Management | ✅ | ✅ |
| Preset System | ✅ | ✅ |
| Neon Theme | ✅ | ✅ |
| Directory Selection | Manual typing | **Native dialog** |
| Installation | Server setup | **One-click installer** |
| Desktop Integration | ❌ | **✅ Start Menu, Desktop** |
| Offline Use | ✅ | ✅ |
| File Association | ❌ | **✅ Future feature** |

## How It Works

1. **Python Backend**: Uses the same reliable Python MIDI generation
2. **Electron Frontend**: Native desktop wrapper around the web interface
3. **IPC Communication**: Secure communication between web UI and system
4. **File System Access**: Direct access to Windows file system

## Technical Architecture

```
┌─────────────────┐
│   HTML/CSS/JS   │  ← Beautiful neon UI
│   (Renderer)    │
└─────────┬───────┘
          │ IPC
┌─────────▼───────┐
│   Main Process  │  ← Electron main thread
│   (Node.js)     │
└─────────┬───────┘
          │ spawn
┌─────────▼───────┐
│ Python Backend  │  ← MIDI generation
│   (midiutil)    │
└─────────────────┘
```

## Development Notes

### File Structure
```
midi-fade-generator-electron/
├── main.js              # Electron main process
├── preload.js           # Security context bridge
├── index.html           # Web interface (modified)
├── valot_python_backend.py  # MIDI generation
├── package.json         # Dependencies & build config
├── assets/
│   └── icon.png         # Application icon
└── dist/                # Built applications
```

### Building Process
1. **Development**: Electron runs locally with hot reload
2. **Packaging**: electron-builder creates Windows installer
3. **Distribution**: NSIS installer with Start Menu integration

### Security Features
- **Context Isolation**: Web content isolated from Node.js
- **Preload Scripts**: Secure API exposure to renderer
- **No Node Integration**: Prevents direct Node.js access from web

## Troubleshooting

### ❌ "MIDI Generation Failed" Error  
**Symptoms**: App starts but MIDI files aren't created

**Solutions**:
1. **Check output directory**: Ensure you have write permissions
2. **Check console**: Open Developer Tools (F12) for error details
3. **Restart app**: Close and reopen the application

### ❌ "No suitable Python" Error (Legacy)
**Note**: This error should not occur in v2.0+ as Python is no longer required!

**If you see this error**:
1. **Update App**: Download the latest version
2. **Clear Cache**: Delete app data and reinstall

### ❌ Windows Defender / Antivirus Warning
**Symptoms**: "Unrecognized app" or antivirus blocks installation

**Solutions**:
1. **Windows Defender**: Click "More info" → "Run anyway"
2. **Add Exception**: Add the application folder to antivirus exclusions
3. **Alternative**: Download source code and build locally

### ❌ App Won't Start
**Symptoms**: Nothing happens when launching

**Solutions**:
1. **Check System Requirements**: Windows 10/11, 4GB+ RAM
2. **Install Visual C++**: Download Microsoft Visual C++ Redistributable
3. **Run as Administrator**: Right-click app → "Run as administrator"
4. **Clear App Data**: Delete `%APPDATA%/midi-fade-generator-electron`

### ❌ Build Issues (Developers)
**Symptoms**: `npm run build-win` fails

**Solutions**:
1. **Node.js Version**: Ensure Node.js v16+
2. **Clear Cache**: Run:
   ```bash
   npm cache clean --force
   rm -rf node_modules
   npm install
   ```
3. **Windows Build Tools**: Install with:
   ```bash
   npm install --global windows-build-tools
   ```

### 💡 Getting Help
- 🐛 **Report Issues**: [GitHub Issues](https://github.com/RauliV/midi-fade-generator-electron/issues)
- 📖 **Documentation**: Check this README
- 🔧 **Debug Mode**: Run with `npm run dev` for detailed logs

## Future Enhancements

- 📁 **File Association**: Open .preset files directly
- 🔄 **Auto-updates**: Automatic application updates
- 🎵 **MIDI Preview**: Play generated files directly
- 📊 **Advanced Analytics**: Scene statistics and optimization
- 🌐 **Multi-language**: Localization support

## License

MIT License - See [LICENSE](LICENSE) file

## Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/RauliV/midi-fade-generator-electron/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/RauliV/midi-fade-generator-electron/discussions)
- 📧 **Email**: Direct contact for enterprise support

---

Built with 💜 using Electron and lots of ✨ neon magic!