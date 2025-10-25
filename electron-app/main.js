const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs').promises;

// Kehitystila
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;
let presetsData = [];

// Luo pääikkuna
function createWindow() {
    // Määritä ikoni alustapohjaisen
    let iconPath;
    if (process.platform === 'darwin') {
        iconPath = path.join(__dirname, 'assets', 'icon.icns');
    } else {
        iconPath = path.join(__dirname, 'assets', 'icon.png');
    }
    
    mainWindow = new BrowserWindow({
        width: 1200,
        height: 900,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        icon: iconPath,
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
    // Määritä oletushakemisto (sama kuin web-versiossa)
    const defaultPath = '/Users/raulivirtanen/Documents/valot/generated_midi';
    
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        defaultPath: defaultPath
    });
    
    if (!result.canceled && result.filePaths.length > 0) {
        return result.filePaths[0];
    }
    return null; // Jos käyttäjä peruuttaa, palauta null
});

// Presets-tiedoston lataus
ipcMain.handle('load-presets', async () => {
    try {
        // Käytä käyttäjän kotihakemistoa macOS:ssä
        const os = require('os');
        const presetsPath = process.platform === 'darwin' 
            ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
            : path.join(__dirname, 'esitykset.json');
            
        // Varmista että hakemisto on olemassa
        if (process.platform === 'darwin') {
            const dir = path.dirname(presetsPath);
            await fs.mkdir(dir, { recursive: true });
        }
        
        console.log('Loading presets from:', presetsPath);
        const data = await fs.readFile(presetsPath, 'utf8');
        presetsData = JSON.parse(data);
        return presetsData;
    } catch (error) {
        console.log('No existing presets file, starting with empty array');
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
        
        // Tallenna tiedostoon - käytä käyttäjän kotihakemistoa macOS:ssä
        const os = require('os');
        const presetsPath = process.platform === 'darwin' 
            ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
            : path.join(__dirname, 'esitykset.json');
            
        // Varmista että hakemisto on olemassa
        if (process.platform === 'darwin') {
            const dir = path.dirname(presetsPath);
            await fs.mkdir(dir, { recursive: true });
        }
        
        console.log('Saving presets to:', presetsPath);
        await fs.writeFile(presetsPath, JSON.stringify(presetsData, null, 2));
        
        return { success: true, replaced: existingIndex >= 0 };
    } catch (error) {
        console.error('Virhe tallentaessa presettia:', error);
        return { success: false, error: error.message };
    }
});

// MIDI-tiedostojen generointi
ipcMain.handle('generate-midi', async (event, data) => {
    console.log('=== Python MIDI Generation (Electron) ===');
    console.log('Platform:', process.platform);
    console.log('Input data:', JSON.stringify(data, null, 2));
    
    try {
        // Käytä Python-generaattoria suoraan kuten web-versiossa
        const { spawn } = require('child_process');
        const os = require('os');
        
        // Määritä Python-polku alustapohjaisen
        let pythonPath;
        if (process.platform === 'darwin') {
            // macOS: kokeile Homebrew-polkua ensin, sitten järjestelmän
            pythonPath = '/opt/homebrew/bin/python3';
            if (!require('fs').existsSync(pythonPath)) {
                pythonPath = '/usr/bin/python3';
            }
        } else if (process.platform === 'win32') {
            pythonPath = 'python';
        } else {
            pythonPath = 'python3';
        }
        
        // Luo Python-skripti käyttäjän kotihakemistoon macOS:ssä
        let scriptPath;
        let workingDir;
        
        if (process.platform === 'darwin') {
            // macOS: käytä käyttäjän kotihakemistoa
            workingDir = path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator');
            await fs.mkdir(workingDir, { recursive: true });
            
            scriptPath = path.join(workingDir, 'valot_python_backend.py');
            
            // Kopioi Python-skripti jos ei ole vielä olemassa
            const bundledScriptPath = path.join(__dirname, 'valot_python_backend.py');
            try {
                await fs.access(scriptPath);
            } catch {
                // Tiedostoa ei ole, kopioi bundlesta
                const scriptContent = await fs.readFile(bundledScriptPath, 'utf8');
                await fs.writeFile(scriptPath, scriptContent);
            }
        } else {
            // Windows: käytä bundle-hakemistoa
            workingDir = __dirname;
            scriptPath = path.join(__dirname, 'valot_python_backend.py');
        }
        
        // Määritä MIDI-tiedostojen tallennushakemisto
        let outputDir;
        
        if (data.outputDir && data.outputDir !== 'generated_midi' && path.isAbsolute(data.outputDir)) {
            // Käyttäjä on valinnut erityisen hakemiston (absoluuttinen polku)
            outputDir = data.outputDir;
            console.log('Using user-selected directory:', outputDir);
        } else {
            // Käytä web-version kaltaista oletushakemistoa
            const originalProjectDir = '/Users/raulivirtanen/Documents/valot';
            outputDir = path.join(originalProjectDir, 'generated_midi');
            console.log('Using web-version compatible default directory:', outputDir);
        }
        
        await fs.mkdir(outputDir, { recursive: true });
        
        // Päivitä data käyttämään oikeaa output-hakemistoa (käytä absoluuttista polkua)
        const updatedData = { ...data, outputDir: path.resolve(outputDir) };
        
        console.log('Using Python path:', pythonPath);
        console.log('Script path:', scriptPath);
        console.log('Working directory:', workingDir);
        console.log('Output directory:', outputDir);
        
        return new Promise((resolve, reject) => {
            const python = spawn(pythonPath, [scriptPath], {
                cwd: workingDir,
                stdio: ['pipe', 'pipe', 'pipe'],
                env: { ...process.env, PYTHONUNBUFFERED: '1' }
            });
            
            let stdout = '';
            let stderr = '';
            
            python.stdout.on('data', (data) => {
                const output = data.toString();
                stdout += output;
                console.log('Python stdout:', output);
            });
            
            python.stderr.on('data', (data) => {
                const error = data.toString();
                stderr += error;
                console.error('Python stderr:', error);
            });
            
            python.on('error', (error) => {
                console.error('Python spawn error:', error);
                reject(new Error(`Failed to spawn Python: ${error.message}`));
            });
            
            python.on('close', (code) => {
                console.log('Python process closed with code:', code);
                console.log('Full stdout:', stdout);
                console.log('Full stderr:', stderr);
                
                if (code === 0) {
                    try {
                        const result = JSON.parse(stdout);
                        console.log('✅ Python MIDI generation result:', result);
                        resolve(result);
                    } catch (parseError) {
                        console.error('❌ Failed to parse Python output:', stdout);
                        reject(new Error('Failed to parse Python output'));
                    }
                } else {
                    console.error('❌ Python process failed:', stderr);
                    reject(new Error(`Python process failed: ${stderr}`));
                }
            });
            
            // Lähetä data Python-skriptille
            python.stdin.write(JSON.stringify(updatedData));
            python.stdin.end();
        });
        
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