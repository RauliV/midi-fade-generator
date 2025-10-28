const { generateMidiFiles } = require('./node_midi_generator');
const fs = require('fs');

async function test() {
    console.log('=== Testing Node.js MIDI Generator ===');
    
    const testData = {
        scenes: [{
            name: 'node_test',
            channels: {'1': 127, '4': 80},
            fade_in_duration: 2,
            fade_out_duration: 2,
            steps: 15
        }],
        outputDir: '.'
    };
    
    try {
        const result = await generateMidiFiles(testData);
        console.log('Test result:', JSON.stringify(result, null, 2));
        
        // Tarkista että tiedostot luotiin
        const fadeInFile = 'node_test_fade_in.mid';
        const fadeOutFile = 'node_test_fade_out.mid';
        
        console.log(`Fade-in file exists: ${fs.existsSync(fadeInFile)}`);
        console.log(`Fade-out file exists: ${fs.existsSync(fadeOutFile)}`);
        
        if (fs.existsSync(fadeInFile)) {
            console.log(`Fade-in file size: ${fs.statSync(fadeInFile).size} bytes`);
        }
        if (fs.existsSync(fadeOutFile)) {
            console.log(`Fade-out file size: ${fs.statSync(fadeOutFile).size} bytes`);
        }
        
    } catch (error) {
        console.error('Test error:', error);
    }
    
    console.log('=== Test Complete ===');
}

test();