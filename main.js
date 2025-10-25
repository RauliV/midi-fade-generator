const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs').promises;
const { generateMidiFiles } = require('./node_midi_generator');

// Kehitystila
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let presetsData = [];

// Luo pääikkuna
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 900,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: path.join(__dirname, 'assets', 'icon.png'), // Windows ikoni
        title: '🎵 MIDI Fade Generator'
    });

    // Lataa HTML-tiedosto
    mainWindow.loadFile('index.html');

    // Kehitystyökalut kehitystilassa
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }
}

// App ready
app.whenReady().then(createWindow);

// Sulje sovellus kun kaikki ikkunat suljettu (paitsi macOS)
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

// macOS: luo ikkuna jos ei ole ja app aktivoituu
app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
        createWindow();
    }
});

// Hakemistovalinta
ipcMain.handle('select-directory', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory']
    });
    
    if (!result.canceled && result.filePaths.length > 0) {
        return result.filePaths[0];
    }
    return null;
});

// Presets-tiedoston lataus
ipcMain.handle('load-presets', async () => {
    try {
        const presetsPath = path.join(__dirname, 'esitykset.json');
        const data = await fs.readFile(presetsPath, 'utf8');
        presetsData = JSON.parse(data);
        return presetsData;
    } catch (error) {
        // Jos tiedostoa ei ole, palautetaan tyhjä array
        presetsData = [];
        return presetsData;
    }
});

// Preset tallentaminen
ipcMain.handle('save-preset', async (event, presetData) => {
    try {
        // Tarkista duplikaatti
        const existingIndex = presetsData.findIndex(p => p.name === presetData.name);
        
        if (existingIndex >= 0) {
            // Korvaa olemassa oleva
            presetsData[existingIndex] = presetData;
        } else {
            // Lisää uusi
            presetsData.push(presetData);
        }
        
        // Tallenna tiedostoon
        const presetsPath = path.join(__dirname, 'esitykset.json');
        await fs.writeFile(presetsPath, JSON.stringify(presetsData, null, 2));
        
        return { success: true, replaced: existingIndex >= 0 };
    } catch (error) {
        console.error('Virhe tallentaessa presettia:', error);
        return { success: false, error: error.message };
    }
});

// MIDI-tiedostojen generointi
ipcMain.handle('generate-midi', async (event, data) => {
    console.log('=== Node.js MIDI Generation ===');
    console.log('Platform:', process.platform);
    console.log('Input data:', JSON.stringify(data, null, 2));
    
    try {
        // Käytä Node.js MIDI-generaattoria suoraan
        const result = await generateMidiFiles(data);
        console.log('✅ MIDI generation result:', result);
        return result;
        
    } catch (error) {
        console.error('❌ MIDI generation error:', error);
        return {
            success: false,
            error: error.message
        };
    }
});

// Versio info
ipcMain.handle('get-version', () => {
    return app.getVersion();
});