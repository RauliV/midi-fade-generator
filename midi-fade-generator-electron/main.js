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
            console.error('Error checking unsaved changes:', error);
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
        defaultPath = path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'generated_midi');
    } else {
        // Linux: paikallinen hakemisto
        defaultPath = path.join(__dirname, 'generated_midi');
    }
    
    console.log('Default directory path:', defaultPath);
    
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        defaultPath: defaultPath
    });
    
    if (!result.canceled && result.filePaths.length > 0) {
        const selectedPath = result.filePaths[0];
        console.log('Selected directory:', selectedPath);
        return selectedPath;
    }
    return null; // Jos käyttäjä peruuttaa, palauta null
});

// Sovelluksen polun haku (suhteellisia polkuja varten)
ipcMain.handle('get-app-path', async () => {
    const os = require('os');
    
    // Käytä samaa logiikkaa kuin muualla
    if (process.platform === 'darwin' || process.platform === 'win32') {
        return path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator');
    } else {
        return __dirname;
    }
});

// Presets-tiedoston lataus
ipcMain.handle('load-presets', async () => {
    try {
        // Käytä käyttäjän kotihakemistoa kaikilla alustoilla
        const os = require('os');
        const presetsPath = process.platform === 'darwin' 
            ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
            : process.platform === 'win32'
                ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')  
                : path.join(__dirname, 'esitykset.json');
            
        // Varmista että hakemisto on olemassa (Windows ja macOS)
        if (process.platform === 'darwin' || process.platform === 'win32') {
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
        
        // Tallenna tiedostoon - käytä käyttäjän kotihakemistoa kaikilla alustoilla
        const os = require('os');
        const presetsPath = process.platform === 'darwin' 
            ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
            : process.platform === 'win32'
                ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
                : path.join(__dirname, 'esitykset.json');
            
        // Varmista että hakemisto on olemassa (Windows ja macOS)
        if (process.platform === 'darwin' || process.platform === 'win32') {
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

// Preset poistaminen
ipcMain.handle('delete-preset', async (event, presetName) => {
    try {
        console.log('Deleting preset:', presetName);
        
        // Etsi poistettava esitys
        const deleteIndex = presetsData.findIndex(p => p.name === presetName);
        
        if (deleteIndex === -1) {
            return { success: false, error: `Esitystä "${presetName}" ei löytynyt` };
        }
        
        // Poista esitys listasta
        presetsData.splice(deleteIndex, 1);
        
        // Tallenna päivitetty lista tiedostoon
        const os = require('os');
        const presetsPath = process.platform === 'darwin' 
            ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
            : process.platform === 'win32'
                ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
                : path.join(__dirname, 'esitykset.json');
            
        // Varmista että hakemisto on olemassa
        if (process.platform === 'darwin' || process.platform === 'win32') {
            const dir = path.dirname(presetsPath);
            await fs.mkdir(dir, { recursive: true });
        }
        
        console.log('Saving updated presets to:', presetsPath);
        await fs.writeFile(presetsPath, JSON.stringify(presetsData, null, 2));
        
        return { success: true };
    } catch (error) {
        console.error('Virhe poistettaessa esitystä:', error);
        return { success: false, error: error.message };
    }
});

// Esitysten vienti tiedostoon
ipcMain.handle('export-presets', async (event) => {
    try {
        console.log('Exporting presets...');
        
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
        console.error('Virhe viennissä:', error);
        return { success: false, error: error.message };
    }
});

// Esitysten tuonti tiedostosta
ipcMain.handle('import-presets', async (event) => {
    try {
        console.log('Importing presets...');
        
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
            ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
            : process.platform === 'win32'
                ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
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
        console.error('Virhe tuonnissa:', error);
        return { success: false, error: error.message };
    }
});

// Valittujen esitysten vienti
ipcMain.handle('export-selected-presets', async (event, selectedPresets) => {
    try {
        console.log('Exporting selected presets:', selectedPresets.length);
        
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
        console.error('Virhe viennissä:', error);
        return { success: false, error: error.message };
    }
});

// Esikatsele tuotavat esitykset (ei tuo vielä)
ipcMain.handle('preview-import-presets', async (event) => {
    try {
        console.log('Previewing import presets...');
        
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
        console.error('Virhe esikatselussa:', error);
        return { success: false, error: error.message };
    }
});

// Tuo valitut esitykset
ipcMain.handle('import-selected-presets', async (event, selectedPresets) => {
    try {
        console.log('Importing selected presets:', selectedPresets.length);
        
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
        const os = require('os');
        const presetsPath = process.platform === 'darwin' 
            ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
            : process.platform === 'win32'
                ? path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator', 'esitykset.json')
                : path.join(__dirname, 'esitykset.json');
            
        // Varmista että hakemisto on olemassa
        if (process.platform === 'darwin' || process.platform === 'win32') {
            const dir = path.dirname(presetsPath);
            await fs.mkdir(dir, { recursive: true });
        }
        
        await fs.writeFile(presetsPath, JSON.stringify(presetsData, null, 2));
        
        return { 
            success: true, 
            imported: importedCount,
            existing: existingCount,
            firstImported: firstImported
        };
    } catch (error) {
        console.error('Virhe tuonnissa:', error);
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
                    console.log('Windows - Found Python at:', pythonPath);
                    break;
                } catch (e) {
                    // Jatka seuraavaan
                }
            }
            
            console.log('Windows detected, using Python command:', pythonPath);
        } else {
            pythonPath = 'python3';
        }
        
        // Luo Python-skripti käyttäjän kotihakemistoon kaikilla alustoilla
        let scriptPath;
        let workingDir;
        
        if (process.platform === 'darwin' || process.platform === 'win32') {
            // macOS ja Windows: käytä käyttäjän Documents-hakemistoa
            workingDir = path.join(os.homedir(), 'Documents', 'MIDI-Fade-Generator');
            await fs.mkdir(workingDir, { recursive: true });
            
            scriptPath = path.join(workingDir, 'valot_python_backend.py');
            
            console.log(`${process.platform.toUpperCase()} - Working directory:`, workingDir);
            console.log(`${process.platform.toUpperCase()} - Script path:`, scriptPath);
            
            // Kopioi Python-skripti jos ei ole vielä olemassa
            const bundledScriptPath = path.join(__dirname, 'valot_python_backend.py');
            console.log(`${process.platform.toUpperCase()} - Bundled script path:`, bundledScriptPath);
            
            try {
                await fs.access(scriptPath);
                console.log(`${process.platform.toUpperCase()} - Script already exists at target location`);
            } catch {
                // Tiedostoa ei ole, kopioi bundlesta
                console.log(`${process.platform.toUpperCase()} - Copying script from bundle to user directory`);
                const scriptContent = await fs.readFile(bundledScriptPath, 'utf8');
                await fs.writeFile(scriptPath, scriptContent);
                console.log(`${process.platform.toUpperCase()} - Script copied successfully`);
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
                console.log('Using user-selected absolute directory:', outputDir);
            } else {
                // Käyttäjä on kirjoittanut suhteellisen polun - liitä working diriin
                outputDir = path.join(workingDir, data.outputDir);
                console.log('Using user-selected relative directory:', data.outputDir, '-> absolute:', outputDir);
            }
        } else {
            // Käytä johdonmukaista hakemistorakennetta kaikilla alustoilla
            outputDir = path.join(workingDir, 'generated_midi');
            console.log('Using platform-specific default directory:', outputDir);
        }
        
        await fs.mkdir(outputDir, { recursive: true });
        
        // Päivitä data käyttämään oikeaa output-hakemistoa (käytä absoluuttista polkua)
        const updatedData = { ...data, outputDir: path.resolve(outputDir) };
        
        console.log('🔧 DEBUG: Alkuperäinen data.outputDir:', data.outputDir);
        console.log('🔧 DEBUG: Laskettu outputDir:', outputDir);
        console.log('🔧 DEBUG: Lopullinen updatedData.outputDir:', updatedData.outputDir);
        
        console.log('Using Python path:', pythonPath);
        console.log('Script path:', scriptPath);
        console.log('Working directory:', workingDir);
        console.log('Output directory:', outputDir);
        
        // Windows-debugging
        if (process.platform === 'win32') {
            console.log('Windows - About to spawn Python process...');
            console.log('Windows - Python command:', pythonPath);
            console.log('Windows - Script exists?', require('fs').existsSync(scriptPath));
        }
        
        return new Promise((resolve, reject) => {
            console.log('Spawning Python process with:', { pythonPath, args: [scriptPath], cwd: workingDir });
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
                if (process.platform === 'win32' && error.code === 'ENOENT') {
                    reject(new Error(`Python 3.6+ ei löytynyt Windowsista.\n\nRatkaise ongelma:\n1. Lataa Python 3.6+ osoitteesta https://python.org\n2. Asennuksen aikana valitse "Add Python to PATH"\n3. Asenna midiutil: avaa Command Prompt ja aja "pip install midiutil"\n4. Käynnistä sovellus uudestaan\n\nVirhe: ${error.message}`));
                } else {
                    reject(new Error(`Failed to spawn Python: ${error.message}`));
                }
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
                    
                    // Tarkista onko kyse puuttuvasta midiutil-moduulista
                    if (stderr.includes('No module named') && stderr.includes('midiutil')) {
                        reject(new Error(`Python-moduuli 'midiutil' puuttuu.\n\nRatkaise ongelma:\n1. Avaa Command Prompt tai Terminal järjestelmänvalvojana\n2. Aja komento: pip install midiutil\n3. Käynnistä sovellus uudestaan\n\nJos pip ei toimi:\n- Windows: asenna Python uudestaan osoitteesta https://python.org (valitse "Add Python to PATH")\n- macOS: asenna Homebrew ja aja: brew install python\n\nVirheen tiedot: ${stderr}`));
                    } else {
                        reject(new Error(`Python process failed: ${stderr}`));
                    }
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