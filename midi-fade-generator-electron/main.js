const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs').promises;

// Kehitystila
const isDev = process.env.NODE_ENV === 'development';

let mainWindow;

// Turvallinen logging-funktio EPIPE-virheiden välttämiseksi
function safeLog(...args) {
    // Ei logita mitään tuotannossa EPIPE-virheiden välttämiseksi
    if (process.env.NODE_ENV === 'development') {
        try {
            console.log(...args);
        } catch (error) {
            // Sivuuta console-virheet hiljaa
        }
    }
}

// Global presets data
let presetsData = [];

// Apufunktio preset-polun löytämiseksi
async function findPresetsPath() {
    const os = require('os');
    let possiblePaths = [];
    
    if (process.platform === 'darwin') {
        possiblePaths = [
            path.join(os.homedir(), 'Documents', 'valot', 'esitykset.json'), // Nykyinen sijainti
            path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json') // Oletussijainti
        ];
    } else if (process.platform === 'win32') {
        possiblePaths = [
            path.join(os.homedir(), 'Documents', 'valot', 'esitykset.json'), // Nykyinen sijainti
            path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json') // Oletussijainti
        ];
    } else {
        // Linux: käytä projektin hakemistoa
        possiblePaths = [path.join(__dirname, '..', 'esitykset.json')];
    }
    
    // Etsi ensimmäinen olemassa oleva tiedosto
    for (const testPath of possiblePaths) {
        try {
            await fs.access(testPath);
            safeLog('Found existing presets at:', testPath);
            return testPath;
        } catch (e) {
            safeLog('Presets not found at:', testPath);
        }
    }
    
    // Jos mitään ei löytynyt, käytä uutta polkua
    const defaultPath = possiblePaths[possiblePaths.length - 1]; // Viimeinen = uusi polku
    safeLog('No existing presets found, using default path:', defaultPath);
    
    // Varmista että hakemisto on olemassa
    if (process.platform === 'darwin' || process.platform === 'win32') {
        const dir = path.dirname(defaultPath);
        await fs.mkdir(dir, { recursive: true });
    }
    
    return defaultPath;
}

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

    // Käsittele ikkunan sulkemisyritys
    mainWindow.on('close', async (event) => {
        // Estä sulkeminen aluksi
        event.preventDefault();
        
        try {
            // Tarkista onko tallentamattomia muutoksia
            const hasChanges = await mainWindow.webContents.executeJavaScript('typeof hasUnsavedChanges !== "undefined" ? hasUnsavedChanges : false');
            
            if (hasChanges) {
                // Käytä sovelluksen omaa dialogi-tyyliä
                const shouldClose = await mainWindow.webContents.executeJavaScript(`
                    showTripleConfirmDialog(
                        'Tallentamattomia muutoksia',
                        'Sinulla on tallentamattomia muutoksia. Mitä haluat tehdä?',
                        'Tallenna ja sulje',
                        'Sulje tallentamatta', 
                        'Peruuta'
                    ).then(choice => {
                        if (choice === 'save') {
                            return savePreset().then(() => 'close');
                        } else if (choice === 'discard') {
                            return 'close';
                        } else {
                            return 'cancel';
                        }
                    }).catch(() => 'cancel')
                `);

                if (shouldClose === 'close') {
                    mainWindow.destroy(); // Pakota sulkeminen
                }
                // Jos shouldClose !== 'close', ei tehdä mitään (sulkeminen estetty)
            } else {
                // Ei tallentamattomia muutoksia, sulje normaalisti
                mainWindow.destroy();
            }
        } catch (error) {
            safeLog('Error checking unsaved changes:', error);
            // Jos tarkistus epäonnistuu, sulje sovellus
            mainWindow.destroy();
        }
    });

    // Varmista että sovellus sammuu kun ikkuna suljetaan
    mainWindow.on('closed', () => {
        mainWindow = null;
        app.quit(); // Pakota sovellus sammumaan
    });

    // Kehitystyökalut kehitystilassa
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }
}

// App ready
app.whenReady().then(createWindow);

// Sulje sovellus kun kaikki ikkunat suljettu
app.on('window-all-closed', () => {
    // Sammuta aina, myös macOS:ssa
    app.quit();
});

// Estä sovellusta avautumasta uudestaan macOS:ssa
app.on('activate', () => {
    // macOS:ssa älä luo uutta ikkunaa automaattisesti
    // Käyttäjän on käynnistettävä sovellus uudestaan
});

// Hakemistovalinta
ipcMain.handle('select-directory', async () => {
    const os = require('os');
    
    // Käytä samaa logiikkaa kuin MIDI-generoinnissa
    let defaultPath;
    if (process.platform === 'darwin' || process.platform === 'win32') {
        // macOS ja Windows: käyttäjän Documents-hakemisto
        defaultPath = path.join(os.homedir(), 'Documents', 'valot', 'generated_midi');
    } else {
        // Linux: paikallinen hakemisto
        defaultPath = path.join(__dirname, 'generated_midi');
    }
    
    safeLog('Default directory path:', defaultPath);
    
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        defaultPath: defaultPath
    });
    
    if (!result.canceled && result.filePaths.length > 0) {
        const selectedPath = result.filePaths[0];
        safeLog('Selected directory:', selectedPath);
        return selectedPath;
    }
    return null; // Jos käyttäjä peruuttaa, palauta null
});

// Sovelluksen polun haku (suhteellisia polkuja varten)
ipcMain.handle('get-app-path', async () => {
    const os = require('os');
    
    // Käytä samaa logiikkaa kuin muualla
    if (process.platform === 'darwin' || process.platform === 'win32') {
        return path.join(os.homedir(), 'Documents', 'valot');
    } else {
        return __dirname;
    }
});

// Presets-tiedoston lataus
ipcMain.handle('load-presets', async () => {
    try {
        const presetsPath = await findPresetsPath();
        safeLog('Loading presets from:', presetsPath);
        const data = await fs.readFile(presetsPath, 'utf8');
        let rawData = JSON.parse(data);
        
        // Normalisoi vanha muoto uuteen muotoon
        presetsData = rawData.map(preset => {
            if (preset.channels && !preset.scenes) {
                // Vanha muoto: muunna uuteen muotoon
                return {
                    name: preset.name,
                    scenes: [{
                        name: preset.name || "Scene 1",
                        channels: preset.channels,
                        fade_in_duration: preset.fade_in_duration || 1,
                        fade_out_duration: preset.fade_out_duration || 1
                    }],
                    steps: preset.steps || 20,
                    saved_at: preset.saved_at || new Date().toISOString()
                };
            }
            // Uusi muoto: palauta sellaisenaan
            return preset;
        });
        
        return presetsData;
    } catch (error) {
        safeLog('No existing presets file, starting with empty array');
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
        const presetsPath = await findPresetsPath();
        safeLog('Saving presets to:', presetsPath);
        await fs.writeFile(presetsPath, JSON.stringify(presetsData, null, 2));
        
        return { success: true, replaced: existingIndex >= 0 };
    } catch (error) {
        safeLog('Virhe tallentaessa presettia:', error);
        return { success: false, error: error.message };
    }
});

// Preset poistaminen
ipcMain.handle('delete-preset', async (event, presetName) => {
    try {
        safeLog('Deleting preset:', presetName);
        
        // Etsi poistettava esitys
        const deleteIndex = presetsData.findIndex(p => p.name === presetName);
        
        if (deleteIndex === -1) {
            return { success: false, error: `Esitystä "${presetName}" ei löytynyt` };
        }
        
        // Poista esitys listasta
        presetsData.splice(deleteIndex, 1);
        
        // Tallenna päivitetty lista tiedostoon
        const presetsPath = await findPresetsPath();
        safeLog('Saving updated presets to:', presetsPath);
        await fs.writeFile(presetsPath, JSON.stringify(presetsData, null, 2));
        
        return { success: true };
    } catch (error) {
        safeLog('Virhe poistettaessa esitystä:', error);
        return { success: false, error: error.message };
    }
});

// Esitysten vienti tiedostoon
ipcMain.handle('export-presets', async (event) => {
    try {
        safeLog('Exporting presets...');
        
        // Näytä tallennusdialogi
        const { dialog } = require('electron');
        const result = await dialog.showSaveDialog(mainWindow, {
            title: 'Vie esitykset tiedostoon',
            defaultPath: `esitykset-backup-${new Date().toISOString().split('T')[0]}.json`,
            filters: [
                { name: 'JSON-tiedostot', extensions: ['json'] },
                { name: 'Kaikki tiedostot', extensions: ['*'] }
            ]
        });
        
        if (result.canceled) {
            return { success: false, error: 'Vienti peruutettu' };
        }
        
        // Tallenna esitykset valittuun tiedostoon
        const exportData = {
            exported: new Date().toISOString(),
            version: '1.0.0',
            presets: presetsData
        };
        
        await fs.writeFile(result.filePath, JSON.stringify(exportData, null, 2));
        
        return { 
            success: true, 
            filename: path.basename(result.filePath),
            count: presetsData.length
        };
    } catch (error) {
        safeLog('Virhe viennissä:', error);
        return { success: false, error: error.message };
    }
});

// Esitysten tuonti tiedostosta
ipcMain.handle('import-presets', async (event) => {
    try {
        safeLog('Importing presets...');
        
        // Näytä tiedostovalintadialogi
        const { dialog } = require('electron');
        const result = await dialog.showOpenDialog(mainWindow, {
            title: 'Tuo esitykset tiedostosta',
            filters: [
                { name: 'JSON-tiedostot', extensions: ['json'] },
                { name: 'Kaikki tiedostot', extensions: ['*'] }
            ],
            properties: ['openFile']
        });
        
        if (result.canceled || !result.filePaths.length) {
            return { success: false, error: 'Tuonti peruutettu' };
        }
        
        // Lue tuotava tiedosto
        const filePath = result.filePaths[0];
        const fileContent = await fs.readFile(filePath, 'utf8');
        const importData = JSON.parse(fileContent);
        
        // Tarkista tiedoston formaatti
        let importPresets = [];
        if (importData.presets && Array.isArray(importData.presets)) {
            // Uusi formaatti (viennin tulos)
            importPresets = importData.presets;
        } else if (Array.isArray(importData)) {
            // Vanha formaatti (suora array)
            importPresets = importData;
        } else {
            throw new Error('Tuntematon tiedostoformaatti');
        }
        
        let importedCount = 0;
        let existingCount = 0;
        let firstImported = null;
        
        // Yhdistä tuodut esitykset nykyisiin
        for (const importPreset of importPresets) {
            const existingIndex = presetsData.findIndex(p => p.name === importPreset.name);
            
            if (existingIndex >= 0) {
                // Päivitä olemassa oleva esitys
                presetsData[existingIndex] = { ...importPreset };
                existingCount++;
            } else {
                // Lisää uusi esitys
                presetsData.push({ ...importPreset });
                importedCount++;
                if (!firstImported) {
                    firstImported = importPreset.name;
                }
            }
        }
        
        // Tallenna päivitetyt esitykset
        const os = require('os');
        const presetsPath = process.platform === 'darwin' 
            ? path.join(os.homedir(), 'Documents', 'valot', 'esitykset.json')
            : process.platform === 'win32'
                ? path.join(os.homedir(), 'Documents', 'valot', 'esitykset.json')
                : path.join(__dirname, 'esitykset.json');
            
        // Varmista että hakemisto on olemassa
        if (process.platform === 'darwin' || process.platform === 'win32') {
            const dir = path.dirname(presetsPath);
            await fs.mkdir(dir, { recursive: true });
        }
        
        await fs.writeFile(presetsPath, JSON.stringify(presetsData, null, 2));
        
        return { 
            success: true, 
            filename: path.basename(filePath),
            imported: importedCount,
            existing: existingCount,
            firstImported: firstImported
        };
    } catch (error) {
        safeLog('Virhe tuonnissa:', error);
        return { success: false, error: error.message };
    }
});

// Valittujen esitysten vienti
ipcMain.handle('export-selected-presets', async (event, selectedPresets) => {
    try {
        safeLog('Exporting selected presets:', selectedPresets.length);
        
        // Näytä tallennusdialogi
        const { dialog } = require('electron');
        const result = await dialog.showSaveDialog(mainWindow, {
            title: 'Vie valitut esitykset tiedostoon',
            defaultPath: `esitykset-valitut-${new Date().toISOString().split('T')[0]}.json`,
            filters: [
                { name: 'JSON-tiedostot', extensions: ['json'] },
                { name: 'Kaikki tiedostot', extensions: ['*'] }
            ]
        });
        
        if (result.canceled) {
            return { success: false, error: 'Vienti peruutettu' };
        }
        
        // Tallenna valitut esitykset tiedostoon
        const exportData = {
            exported: new Date().toISOString(),
            version: '1.0.0',
            presets: selectedPresets
        };
        
        await fs.writeFile(result.filePath, JSON.stringify(exportData, null, 2));
        
        return { 
            success: true, 
            filename: path.basename(result.filePath),
            count: selectedPresets.length
        };
    } catch (error) {
        safeLog('Virhe viennissä:', error);
        return { success: false, error: error.message };
    }
});

// Esikatsele tuotavat esitykset (ei tuo vielä)
ipcMain.handle('preview-import-presets', async (event) => {
    try {
        safeLog('Previewing import presets...');
        
        // Näytä tiedostovalintadialogi
        const { dialog } = require('electron');
        const result = await dialog.showOpenDialog(mainWindow, {
            title: 'Valitse tuotava esitystiedosto',
            filters: [
                { name: 'JSON-tiedostot', extensions: ['json'] },
                { name: 'Kaikki tiedostot', extensions: ['*'] }
            ],
            properties: ['openFile']
        });
        
        if (result.canceled || !result.filePaths.length) {
            return { success: false, error: 'Tuonti peruutettu' };
        }
        
        // Lue ja esikatsele tiedosto
        const filePath = result.filePaths[0];
        const fileContent = await fs.readFile(filePath, 'utf8');
        const importData = JSON.parse(fileContent);
        
        // Tarkista tiedoston formaatti
        let importPresets = [];
        if (importData.presets && Array.isArray(importData.presets)) {
            // Uusi formaatti (viennin tulos)
            importPresets = importData.presets;
        } else if (Array.isArray(importData)) {
            // Vanha formaatti (suora array)
            importPresets = importData;
        } else {
            throw new Error('Tuntematon tiedostoformaatti');
        }
        
        return { 
            success: true, 
            filename: path.basename(filePath),
            presets: importPresets,
            fullPath: filePath
        };
    } catch (error) {
        safeLog('Virhe esikatselussa:', error);
        return { success: false, error: error.message };
    }
});

// Tuo valitut esitykset
ipcMain.handle('import-selected-presets', async (event, selectedPresets) => {
    try {
        safeLog('Importing selected presets:', selectedPresets.length);
        
        let importedCount = 0;
        let existingCount = 0;
        let firstImported = null;
        
        // Yhdistä valitut esitykset nykyisiin
        for (const importPreset of selectedPresets) {
            const existingIndex = presetsData.findIndex(p => p.name === importPreset.name);
            
            if (existingIndex >= 0) {
                // Päivitä olemassa oleva esitys
                presetsData[existingIndex] = { ...importPreset };
                existingCount++;
            } else {
                // Lisää uusi esitys
                presetsData.push({ ...importPreset });
                importedCount++;
                if (!firstImported) {
                    firstImported = importPreset.name;
                }
            }
        }
        
        // Tallenna päivitetyt esitykset
        const presetsPath = await findPresetsPath();
        await fs.writeFile(presetsPath, JSON.stringify(presetsData, null, 2));
        
        return { 
            success: true, 
            imported: importedCount,
            existing: existingCount,
            firstImported: firstImported
        };
    } catch (error) {
        safeLog('Virhe tuonnissa:', error);
        return { success: false, error: error.message };
    }
});

// MIDI-tiedostojen generointi
ipcMain.handle('generate-midi', async (event, data) => {
    safeLog('=== Python MIDI Generation (Electron) ===');
    safeLog('Platform:', process.platform);
    safeLog('Input data:', JSON.stringify(data, null, 2));
    
    try {
        // Normalisoi presetit scenes-muotoon Python-skriptiä varten
        let scenesToProcess = [];
        
        if (data.presets && Array.isArray(data.presets)) {
            for (const preset of data.presets) {
                safeLog('🔧 DEBUG: Processing preset:', preset.name);
                
                if (preset.channels && !preset.scenes) {
                    // Vanha muoto: muunna scenes-muotoon
                    safeLog('🔧 DEBUG: Converting old format preset to new format');
                    scenesToProcess.push({
                        name: preset.name,
                        channels: preset.channels,
                        fade_in_duration: preset.fade_in_duration || 1.0,
                        fade_out_duration: preset.fade_out_duration || 1.0,
                        steps: preset.steps || 20
                    });
                } else if (preset.scenes) {
                    // Uusi muoto: lisää scenes-lista
                    safeLog('🔧 DEBUG: Using new format preset with', preset.scenes.length, 'scenes');
                    for (const scene of preset.scenes) {
                        scenesToProcess.push({
                            name: scene.name,
                            channels: scene.channels,
                            fade_in_duration: scene.fade_in_duration || 1.0,
                            fade_out_duration: scene.fade_out_duration || 1.0,
                            steps: scene.steps || preset.steps || 20
                        });
                    }
                } else {
                    console.warn('🔧 WARNING: Unknown preset format:', preset);
                }
            }
        } else if (data.scenes && Array.isArray(data.scenes)) {
            // Data on jo scenes-muodossa
            safeLog('🔧 DEBUG: Data already in scenes format');
            scenesToProcess = data.scenes;
        } else {
            throw new Error('Invalid data format: no presets or scenes found');
        }
        
        safeLog('🔧 DEBUG: Total scenes to process:', scenesToProcess.length);
        
        // Päivitä data scenes-muotoon
        const processedData = {
            ...data,
            scenes: scenesToProcess
        };
        delete processedData.presets; // Poista vanhat presetit
        
        safeLog('🔧 DEBUG: Processed data for Python:', JSON.stringify(processedData, null, 2));
        
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
            // Windows: kokeile eri Python-polkuja järjestyksessä
            const possiblePaths = [
                'python',     // Python Launcher (suositeltu)
                'python3',    // Jos asennettu erikseen
                'py',         // Python Launcher vaihtoehto
                'C:\\Python39\\python.exe',
                'C:\\Python310\\python.exe',
                'C:\\Python311\\python.exe',
                'C:\\Python312\\python.exe'
            ];
            
            pythonPath = 'python'; // oletusarvo
            
            // Kokeile löytää Python
            for (const testPath of possiblePaths) {
                try {
                    const { execSync } = require('child_process');
                    execSync(`${testPath} --version`, { stdio: 'ignore', timeout: 5000 });
                    pythonPath = testPath;
                    safeLog('Windows - Found Python at:', pythonPath);
                    break;
                } catch (e) {
                    // Jatka seuraavaan
                }
            }
            
            safeLog('Windows detected, using Python command:', pythonPath);
        } else {
            pythonPath = 'python3';
        }
        
        // Luo Python-skripti käyttäjän kotihakemistoon kaikilla alustoilla
        let scriptPath;
        let workingDir;
        
        if (process.platform === 'darwin' || process.platform === 'win32') {
            // macOS ja Windows: käytä käyttäjän Documents-hakemistoa
            workingDir = path.join(os.homedir(), 'Documents', 'valot');
            await fs.mkdir(workingDir, { recursive: true });
            
            scriptPath = path.join(workingDir, 'valot_python_backend.py');
            
            safeLog(`${process.platform.toUpperCase()} - Working directory:`, workingDir);
            safeLog(`${process.platform.toUpperCase()} - Script path:`, scriptPath);
            
            // Kopioi Python-skripti jos ei ole vielä olemassa
            const bundledScriptPath = path.join(__dirname, 'valot_python_backend.py');
            safeLog(`${process.platform.toUpperCase()} - Bundled script path:`, bundledScriptPath);
            
            try {
                await fs.access(scriptPath);
                safeLog(`${process.platform.toUpperCase()} - Script already exists at target location`);
            } catch {
                // Tiedostoa ei ole, kopioi bundlesta
                safeLog(`${process.platform.toUpperCase()} - Copying script from bundle to user directory`);
                const scriptContent = await fs.readFile(bundledScriptPath, 'utf8');
                await fs.writeFile(scriptPath, scriptContent);
                safeLog(`${process.platform.toUpperCase()} - Script copied successfully`);
            }
        } else {
            // Linux: käytä bundle-hakemistoa
            workingDir = __dirname;
            scriptPath = path.join(__dirname, 'valot_python_backend.py');
        }
        
        // Määritä MIDI-tiedostojen tallennushakemisto
        let outputDir;
        
        if (data.outputDir && data.outputDir !== 'generated_midi') {
            if (path.isAbsolute(data.outputDir)) {
                // Käyttäjä on valinnut absoluuttisen polun
                outputDir = data.outputDir;
                safeLog('Using user-selected absolute directory:', outputDir);
            } else {
                // Käyttäjä on kirjoittanut suhteellisen polun - liitä working diriin
                outputDir = path.join(workingDir, data.outputDir);
                safeLog('Using user-selected relative directory:', data.outputDir, '-> absolute:', outputDir);
            }
        } else {
            // Käytä johdonmukaista hakemistorakennetta kaikilla alustoilla
            outputDir = path.join(workingDir, 'generated_midi');
            safeLog('Using platform-specific default directory:', outputDir);
        }
        
        await fs.mkdir(outputDir, { recursive: true });
        
        // Päivitä data käyttämään oikeaa output-hakemistoa ja prosessoitua scenes-dataa
        const updatedData = { ...processedData, outputDir: path.resolve(outputDir) };
        
        safeLog('🔧 DEBUG: Alkuperäinen data.outputDir:', data.outputDir);
        safeLog('🔧 DEBUG: Laskettu outputDir:', outputDir);
        safeLog('🔧 DEBUG: Lopullinen updatedData.outputDir:', updatedData.outputDir);
        
        safeLog('Using Python path:', pythonPath);
        safeLog('Script path:', scriptPath);
        safeLog('Working directory:', workingDir);
        safeLog('Output directory:', outputDir);
        
        // Windows-debugging
        if (process.platform === 'win32') {
            safeLog('Windows - About to spawn Python process...');
            safeLog('Windows - Python command:', pythonPath);
            safeLog('Windows - Script exists?', require('fs').existsSync(scriptPath));
        }
        
        return new Promise((resolve, reject) => {
            safeLog('Spawning Python process with:', { pythonPath, args: [scriptPath], cwd: workingDir });
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
                safeLog('Python stdout:', output);
            });
            
            python.stderr.on('data', (data) => {
                const error = data.toString();
                stderr += error;
                safeLog('Python stderr:', error);
            });
            
            python.on('error', (error) => {
                safeLog('Python spawn error:', error);
                if (process.platform === 'win32' && error.code === 'ENOENT') {
                    reject(new Error(`Python 3.6+ ei löytynyt Windowsista.\n\nRatkaise ongelma:\n1. Lataa Python 3.6+ osoitteesta https://python.org\n2. Asennuksen aikana valitse "Add Python to PATH"\n3. Asenna midiutil: avaa Command Prompt ja aja "pip install midiutil"\n4. Käynnistä sovellus uudestaan\n\nVirhe: ${error.message}`));
                } else {
                    reject(new Error(`Failed to spawn Python: ${error.message}`));
                }
            });
            
            python.on('close', (code) => {
                safeLog('Python process closed with code:', code);
                safeLog('Full stdout:', stdout);
                safeLog('Full stderr:', stderr);
                
                if (code === 0) {
                    try {
                        const result = JSON.parse(stdout);
                        safeLog('✅ Python MIDI generation result:', result);
                        resolve(result);
                    } catch (parseError) {
                        safeLog('❌ Failed to parse Python output:', stdout);
                        reject(new Error('Failed to parse Python output'));
                    }
                } else {
                    safeLog('❌ Python process failed:', stderr);
                    
                    // Tarkista onko kyse puuttuvasta midiutil-moduulista
                    if (stderr.includes('No module named') && stderr.includes('midiutil')) {
                        reject(new Error(`Python-moduuli 'midiutil' puuttuu.\n\nRatkaise ongelma:\n1. Avaa Command Prompt tai Terminal järjestelmänvalvojana\n2. Aja komento: pip install midiutil\n3. Käynnistä sovellus uudestaan\n\nJos pip ei toimi:\n- Windows: asenna Python uudestaan osoitteesta https://python.org (valitse "Add Python to PATH")\n- macOS: asenna Homebrew ja aja: brew install python\n\nVirheen tiedot: ${stderr}`));
                    } else {
                        reject(new Error(`Python process failed: ${stderr}`));
                    }
                }
            });
            
            // Lähetä data Python-skriptille
            const jsonData = JSON.stringify(updatedData, null, 2);
            safeLog('🔧 DEBUG: Sending JSON data to Python:', jsonData);
            
            python.stdin.write(jsonData);
            python.stdin.end();
        });
        
    } catch (error) {
        safeLog('❌ MIDI generation error:', error);
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