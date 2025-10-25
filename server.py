#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.server
import socketserver
import json
import subprocess
import os
import urllib.parse
import tempfile
import mimetypes
from pathlib import Path
import datetime

PORT = 8000
SCRIPT_DIR = Path(__file__).parent
MIDI_OUTPUT_DIR = SCRIPT_DIR / "generated_midi"
PRESETS_FILE = SCRIPT_DIR / "esitykset.json"

# Varmista että kansiot ovat olemassa
MIDI_OUTPUT_DIR.mkdir(exist_ok=True)

class MIDIHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Käsittele GET-pyynnöt"""
        if self.path == '/':
            self.path = '/valot3.html'
        
        if self.path.startswith('/download/'):
            # MIDI-tiedoston lataus
            filename = self.path[10:]  # Poista '/download/' alusta
            file_path = MIDI_OUTPUT_DIR / filename
            
            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                self.send_header('Content-type', 'audio/midi')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                    
                print(f"📥 Lähetetty tiedosto: {filename}")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'File not found')
                print(f"❌ Tiedostoa ei löytynyt: {filename}")
                
        elif self.path == '/presets':
            # Palauta tallennetut esitykset
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if PRESETS_FILE.exists():
                with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(json.dumps([]).encode('utf-8'))
                
        else:
            # Staattinen tiedosto
            try:
                if self.path.startswith('/'):
                    file_path = SCRIPT_DIR / self.path[1:]
                else:
                    file_path = SCRIPT_DIR / self.path
                    
                if file_path.exists() and file_path.is_file():
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    if mime_type is None:
                        mime_type = 'text/plain'
                        
                    self.send_response(200)
                    self.send_header('Content-type', mime_type)
                    self.end_headers()
                    
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.send_response(404)
                    self.end_headers()
            except Exception as e:
                print(f"Virhe tiedoston käsittelyssä: {e}")
                self.send_response(500)
                self.end_headers()

    def do_POST(self):
        """Käsittele POST-pyynnöt"""
        if self.path == '/generate-midi':
            # MIDI-generaatio
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                print(f"🎵 Saatiin pyyntö {len(data['scenes'])} kohtaukselle")
                
                # Määritä tallennushakemisto
                output_dir = data.get('output_directory', 'generated_midi')
                if not os.path.isabs(output_dir):
                    # Jos suhteellinen polku, liitä script-hakemistoon
                    output_dir = SCRIPT_DIR / output_dir
                else:
                    output_dir = Path(output_dir)
                
                # Luo hakemisto jos ei ole olemassa
                output_dir.mkdir(parents=True, exist_ok=True)
                print(f"📁 Tallennushakemisto: {output_dir}")
                
                # Vaihda työhakemisto määriteltyyn tallennushakemistoon
                original_cwd = os.getcwd()
                os.chdir(output_dir)
                
                try:
                    # Kutsu Python-skriptiä samassa ympäristössä
                    backend_script = SCRIPT_DIR / 'valot_python_backend.py'
                    
                    # Käytä virtual environmentin Python-tulkkia
                    import sys
                    venv_python = SCRIPT_DIR / '.venv' / 'bin' / 'python'
                    if venv_python.exists():
                        python_executable = str(venv_python)
                    else:
                        python_executable = sys.executable
                    
                    print(f"🐍 Käytetään Python-tulkkia: {python_executable}")
                    
                    result = subprocess.run(
                        [python_executable, str(backend_script)],
                        input=json.dumps(data),
                        text=True,
                        capture_output=True,
                        check=True
                    )
                    
                    response_data = json.loads(result.stdout)
                    
                    # Lisää tallennushakemisto vastaukseen
                    response_data['output_directory'] = str(output_dir)
                    
                    # Lähetä vastaus
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                    
                    print(f"✅ Onnistuneesti luotu MIDI-tiedostot {len(response_data.get('results', []))} kohtaukselle hakemistoon {output_dir}")
                    
                finally:
                    os.chdir(original_cwd)
                    
            except subprocess.CalledProcessError as e:
                print(f"❌ Python-skripti epäonnistui: {e}")
                print(f"stderr: {e.stderr}")
                error_response = {
                    'success': False,
                    'error': f'Python-skripti epäonnistui: {e.stderr}'
                }
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                
            except Exception as e:
                print(f"❌ Odottamaton virhe: {e}")
                error_response = {
                    'success': False,
                    'error': str(e)
                }
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
                
        elif self.path == '/save-preset':
            # Tallenna esitys
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # Lataa olemassa olevat esitykset
                presets = []
                if PRESETS_FILE.exists():
                    with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
                        presets = json.load(f)
                
                # Lisää aikaleima
                data['saved_at'] = datetime.datetime.now().isoformat()
                
                # Etsi olemassa oleva esitys samalla nimellä
                preset_name = data.get('name', '')
                existing_index = -1
                for i, preset in enumerate(presets):
                    if preset.get('name', '') == preset_name:
                        existing_index = i
                        break
                
                if existing_index >= 0:
                    # Korvaa olemassa oleva esitys
                    presets[existing_index] = data
                    print(f"🔄 Korvattu olemassa oleva esitys: {preset_name}")
                else:
                    # Lisää uusi esitys
                    presets.append(data)
                    print(f"➕ Lisätty uusi esitys: {preset_name}")
                
                # Tallenna takaisin
                with open(PRESETS_FILE, 'w', encoding='utf-8') as f:
                    json.dump(presets, f, indent=2, ensure_ascii=False)
                
                response = {'success': True, 'message': 'Esitys tallennettu'}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
                # Tulosta sopiva viesti riippuen siitä, oliko korvaus vai uusi
                
            except Exception as e:
                print(f"❌ Virhe esityksen tallennuksessa: {e}")
                error_response = {'success': False, 'error': str(e)}
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        """Käsittele GET-pyynnöt"""
        if self.path == '/':
            self.path = '/valot3.html'
        
        if self.path.startswith('/download/'):
            # MIDI-tiedoston lataus
            filename = self.path[10:]  # Poista '/download/' alusta
            file_path = MIDI_OUTPUT_DIR / filename
            
            if file_path.exists() and file_path.is_file():
                self.send_response(200)
                self.send_header('Content-type', 'audio/midi')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                    
                print(f"📥 Lähetetty tiedosto: {filename}")
            else:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'File not found')
                print(f"❌ Tiedostoa ei löytynyt: {filename}")
                
        elif self.path == '/presets':
            # Palauta tallennetut esitykset
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if PRESETS_FILE.exists():
                with open(PRESETS_FILE, 'r', encoding='utf-8') as f:
                    self.wfile.write(f.read().encode('utf-8'))
            else:
                self.wfile.write(json.dumps([]).encode('utf-8'))
                
        else:
            # Staattinen tiedosto
            try:
                if self.path.startswith('/'):
                    file_path = SCRIPT_DIR / self.path[1:]
                else:
                    file_path = SCRIPT_DIR / self.path
                    
                if file_path.exists() and file_path.is_file():
                    mime_type, _ = mimetypes.guess_type(str(file_path))
                    if mime_type is None:
                        mime_type = 'text/plain'
                        
                    self.send_response(200)
                    self.send_header('Content-type', mime_type)
                    self.end_headers()
                    
                    with open(file_path, 'rb') as f:
                        self.wfile.write(f.read())
                else:
                    self.send_response(404)
                    self.end_headers()
            except Exception as e:
                print(f"Virhe tiedoston käsittelyssä: {e}")
                self.send_response(500)
                self.end_headers()

    def do_OPTIONS(self):
        """Käsittele CORS preflight-pyynnöt"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    """Käynnistä HTTP-palvelin"""
    print(f"🚀 Käynnistetään MIDI-generaattori palvelin...")
    print(f"📁 Työskentelyhakemisto: {SCRIPT_DIR}")
    print(f"📁 MIDI-tiedostot tallennetaan: {MIDI_OUTPUT_DIR}")
    print(f"🌐 Palvelin käynnistyy portissa {PORT}")
    print(f"🔗 Avaa selaimessa: http://localhost:{PORT}/valot3.html")
    print(f"⏹️  Lopeta palvelin: Ctrl+C")
    print("-" * 50)

    with socketserver.TCPServer(("", PORT), MIDIHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Palvelin lopetettu")

if __name__ == "__main__":
    main()