const { contextBridge, ipcRenderer } = require('electron');

// Turvallinen API renderer-prosessille
contextBridge.exposeInMainWorld('electronAPI', {
    // Hakemistovalinta
    selectDirectory: () => ipcRenderer.invoke('select-directory'),
    
    // Presets
    loadPresets: () => ipcRenderer.invoke('load-presets'),
    savePreset: (presetData) => ipcRenderer.invoke('save-preset', presetData),
    
    // MIDI generointi
    generateMidi: (data) => ipcRenderer.invoke('generate-midi', data),
    
    // App info
    getVersion: () => ipcRenderer.invoke('get-version'),
    
    // Platform info
    platform: process.platform
});