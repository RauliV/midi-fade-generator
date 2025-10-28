const { contextBridge, ipcRenderer } = require('electron');

// Turvallinen API renderer-prosessille
contextBridge.exposeInMainWorld('electronAPI', {
    // Hakemistovalinta
    selectDirectory: () => ipcRenderer.invoke('select-directory'),
    getAppPath: () => ipcRenderer.invoke('get-app-path'),
    
    // Presets
    loadPresets: () => ipcRenderer.invoke('load-presets'),
    savePreset: (presetData) => ipcRenderer.invoke('save-preset', presetData),
    deletePreset: (presetName) => ipcRenderer.invoke('delete-preset', presetName),
    exportPresets: () => ipcRenderer.invoke('export-presets'),
    importPresets: () => ipcRenderer.invoke('import-presets'),
    exportSelectedPresets: (selectedPresets) => ipcRenderer.invoke('export-selected-presets', selectedPresets),
    previewImportPresets: () => ipcRenderer.invoke('preview-import-presets'),
    importSelectedPresets: (selectedPresets) => ipcRenderer.invoke('import-selected-presets', selectedPresets),
    
    // MIDI generointi
    generateMidi: (data) => ipcRenderer.invoke('generate-midi', data),
    
    // App info
    getVersion: () => ipcRenderer.invoke('get-version'),
    
    // Platform info
    platform: process.platform
});