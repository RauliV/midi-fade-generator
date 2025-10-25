# 🎵 MIDI Fade-in/out Generator

A beautiful, neon-themed web application for generating MIDI fade-in and fade-out files for lighting control systems.

![Neon Theme](nuotti.jpg)

## Features

- 🎭 **Scene Management**: Create and manage multiple lighting scenes
- 🎵 **MIDI Generation**: Generate fade-in and fade-out MIDI files
- 💾 **Preset System**: Save and load scene configurations
- 🌈 **Neon UI**: Beautiful purple neon-themed interface
- 📁 **Flexible Output**: Choose custom output directories
- 🔢 **Auto Numbering**: Automatic scene numbering system
- 🚫 **Duplicate Prevention**: Prevents duplicate preset names
- 📱 **Responsive Design**: Works on desktop and mobile

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/RauliV/midi-fade-generator.git
   cd midi-fade-generator
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install midiutil
   ```

## Usage

1. **Start the server:**
   ```bash
   python3 server.py
   ```

2. **Open in browser:**
   ```
   http://localhost:8000
   ```

3. **Create scenes:**
   - Add lighting scenes with channel values (0-127)
   - Set fade-in and fade-out durations
   - Configure MIDI generation steps

4. **Generate MIDI files:**
   - Choose output directory
   - Click "Generate MIDI files"
   - Files are saved as `scenename_fade_in.mid` and `scenename_fade_out.mid`

## File Structure

```
midi-fade-generator/
├── index.html              # Main web interface
├── server.py               # Web server
├── valot_python_backend.py  # MIDI generation backend
├── nuotti.jpg              # Neon music note image
├── scripts/
│   └── remove_duplicates.py # Utility for cleaning presets
├── docs/
└── README.md
```

## Configuration

### Output Directory Options

- **Relative path**: `generated_midi` → saves to project directory
- **Absolute path**: `/Users/name/Documents/MIDI` → saves to specific location
- **Home directory**: `~/Desktop/midifiles` → saves to desktop

### MIDI Parameters

- **Channels**: 1-512 (DMX standard)
- **Values**: 0-127 (MIDI standard)
- **Fade Steps**: 5-100 (smoothness of fade)
- **Duration**: Any positive number in seconds

## Development

### Server Features

- **HTTP Server**: Serves static files and handles API requests
- **Preset Management**: JSON-based storage with duplicate prevention
- **MIDI Generation**: Real-time MIDI file creation
- **Error Handling**: Comprehensive error messages and logging

### Frontend Features

- **Neon Theme**: Custom CSS with purple neon aesthetics
- **Modal System**: Beautiful feedback modals instead of alerts
- **Responsive Layout**: Optimized for various screen sizes
- **Auto-save**: Prevents data loss with confirmation dialogs

## Scripts

### Remove Duplicates
```bash
python3 scripts/remove_duplicates.py
```
Cleans up duplicate presets from the JSON storage file.

## Technical Details

- **Backend**: Python with midiutil library
- **Frontend**: HTML5, CSS3, JavaScript (no external dependencies)
- **Storage**: JSON files for presets
- **MIDI Standard**: Uses standard MIDI control change messages
- **Architecture**: Client-server with RESTful API

## Browser Compatibility

- ✅ Chrome/Chromium
- ✅ Firefox
- ✅ Safari
- ✅ Edge

## License

MIT License - feel free to use and modify!

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Support

For issues or questions, please open a GitHub issue.

---

Made with 💜 and lots of ✨ neon vibes!