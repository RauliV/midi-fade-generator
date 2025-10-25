# 🎵 MIDI Fade Generator - Electron Desktop App

Beautiful Electron desktop application for generating MIDI fade-in and fade-out files for lighting control systems. Optimized for Windows 10 with native file dialogs and desktop integration.

![MIDI Fade Generator](nuotti.jpg)

## Features

🖥️ **Native Desktop App**: Standalone Windows application, no browser needed  
📁 **Native File Dialogs**: Browse directories with Windows file explorer  
💾 **Local Data Storage**: Presets saved locally on your computer  
🎭 **Full Scene Management**: All web version features included  
⚡ **Offline Operation**: No internet connection required  
🎯 **Windows 10 Optimized**: Built specifically for Windows desktop use  

## Download & Installation

### For End Users
Download the latest release from GitHub:
1. Go to [Releases](https://github.com/RauliV/midi-fade-generator-electron/releases)
2. Download `MIDI-Fade-Generator-Setup-1.0.0.exe`
3. Run the installer
4. Launch from Start Menu or Desktop

### For Developers

## Setup & Requirements

### Windows 10/11 Users
1. **Download & Install**: Get the `.exe` installer from [Releases](https://github.com/RauliV/midi-fade-generator-electron/releases)
2. **Launch**: Find "MIDI Fade Generator" in Start Menu
   - ✅ **No Python Required**: MIDI generation now uses Node.js internally!

### macOS Users  
1. **Download App**: Get the `.dmg` from [Releases](https://github.com/RauliV/midi-fade-generator-electron/releases)
2. **Launch**: Open from Applications folder
   - ✅ **No Dependencies**: Everything included in the app!

### Developer Setup
Prerequisites:
- **Node.js** (v16 or later)
- **Python 3.8+** with midiutil library
- **Git**

```bash
git clone https://github.com/RauliV/midi-fade-generator-electron.git
cd midi-fade-generator-electron
npm install
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