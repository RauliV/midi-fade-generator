const jsmidgen = require('jsmidgen');
const fs = require('fs').promises;
const path = require('path');

/**
 * Luo fade-in tai fade-out MIDI-tiedoston Node.js:llä
 */
function createFadeMidi(filename, notes, velocities, duration, isFadeIn, steps = 20) {
    const file = new jsmidgen.File();
    const track = new jsmidgen.Track();
    
    // Tempo: 120 BPM (sama kuin Python-versiossa)
    track.setTempo(120);
    
    // Käytä sopivaa resoluutiota jsmidgen:in kanssa
    const totalTicks = duration * 480; // 480 on jsmidgen:in oletus
    const ticksPerStep = Math.floor(totalTicks / steps);
    
    let currentTick = 0;
    
    if (isFadeIn) {
        // Fade-in: 1 -> target velocity
        for (let step = 1; step <= steps; step++) {
            const factor = step / steps;
            for (let i = 0; i < notes.length; i++) {
                const note = notes[i];
                const targetVel = velocities[i];
                const vel = Math.max(1, Math.floor(targetVel * factor));
                
                track.noteOn(0, note, currentTick, vel);
                track.noteOff(0, note, currentTick + ticksPerStep, 0);
            }
            currentTick += ticksPerStep;
        }
        
        // Hold target velocity lyhyesti  
        const holdTicks = Math.floor(0.4 * 480); // Käytä jsmidgen:in resoluutiota
        for (let i = 0; i < notes.length; i++) {
            const note = notes[i];
            const targetVel = velocities[i];
            track.noteOn(0, note, currentTick, targetVel);
            track.noteOff(0, note, currentTick + holdTicks, 0);
        }
        currentTick += holdTicks;
        
    } else {
        // Fade-out: target -> 0
        for (let step = 0; step <= steps; step++) {
            const factor = 1 - (step / steps);
            for (let i = 0; i < notes.length; i++) {
                const note = notes[i];
                const targetVel = velocities[i];
                const vel = Math.floor(targetVel * factor);
                
                track.noteOn(0, note, currentTick, vel);
                track.noteOff(0, note, currentTick + ticksPerStep, 0);
            }
            currentTick += ticksPerStep;
        }
    }
    
    file.addTrack(track);
    return file.toBytes();
}

/**
 * Pääfunktio MIDI-tiedostojen luomiseen
 */
async function generateMidiFiles(data) {
    try {
        console.log('Node.js MIDI Generator starting...');
        console.log('Input data:', JSON.stringify(data, null, 2));
        
        const results = [];
        const workingDir = data.outputDir || process.cwd();
        
        // Varmista että hakemisto on olemassa
        try {
            await fs.access(workingDir);
        } catch (err) {
            // Luo hakemisto jos ei ole olemassa
            await fs.mkdir(workingDir, { recursive: true });
        }
        
        for (const scene of data.scenes) {
            const sceneName = scene.name;
            const channels = scene.channels;
            const fadeInDuration = scene.fade_in_duration;
            const fadeOutDuration = scene.fade_out_duration;
            const steps = scene.steps || 20;
            
            console.log(`Processing scene: ${sceneName}`);
            
            // Muunna kanavat MIDI-nuoteiksi: nuotti = 69 + kanava
            const notes = Object.keys(channels).map(channel => 69 + parseInt(channel));
            const velocities = Object.values(channels);
            
            console.log(`Notes: ${notes}, Velocities: ${velocities}`);
            
            // Luo tiedostonimet
            const fadeInFilename = `${sceneName}_fade_in.mid`;
            const fadeOutFilename = `${sceneName}_fade_out.mid`;
            
            // Luo MIDI-tiedostot
            const fadeInBytes = createFadeMidi(fadeInFilename, notes, velocities, fadeInDuration, true, steps);
            const fadeOutBytes = createFadeMidi(fadeOutFilename, notes, velocities, fadeOutDuration, false, steps);
            
            // Kirjoita tiedostot
            const fadeInPath = path.join(workingDir, fadeInFilename);
            const fadeOutPath = path.join(workingDir, fadeOutFilename);
            
            await fs.writeFile(fadeInPath, Buffer.from(fadeInBytes));
            await fs.writeFile(fadeOutPath, Buffer.from(fadeOutBytes));
            
            console.log(`Created: ${fadeInPath} and ${fadeOutPath}`);
            
            results.push({
                scene: sceneName,
                fade_in_file: fadeInFilename,
                fade_out_file: fadeOutFilename,
                fade_in_path: fadeInPath,
                fade_out_path: fadeOutPath,
                channels_count: notes.length,
                steps: steps
            });
        }
        
        console.log('Node.js MIDI Generator completed successfully');
        return {
            success: true,
            results: results
        };
        
    } catch (error) {
        console.error('Node.js MIDI Generator error:', error);
        return {
            success: false,
            error: error.message
        };
    }
}

module.exports = { generateMidiFiles };

// Komentorivituki
if (require.main === module) {
    const readline = require('readline');
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    let inputData = '';
    
    rl.on('line', (line) => {
        inputData += line;
    });
    
    rl.on('close', async () => {
        try {
            const data = JSON.parse(inputData);
            console.log('Node.js MIDI Generator starting...');
            console.log('Input data:', JSON.stringify(data, null, 2));
            
            const result = await generateMidiFiles(data);
            console.log('Result:', JSON.stringify(result, null, 2));
            
            if (result.success) {
                process.exit(0);
            } else {
                process.exit(1);
            }
        } catch (error) {
            console.error('Error:', error.message);
            process.exit(1);
        }
    });
}