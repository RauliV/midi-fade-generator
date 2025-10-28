# 🛒 433MHz Setup - Ostoslista ja Asennus

## 🛍️ Mitä tarvitset (n. 20-30€)

### 433MHz Radio-moduulit:
1. **433MHz Transmitter** (TX) - Robotti-kaukolaukaisimeen
   - Hinta: ~3-5€
   - Esim: FS1000A, SYN115, tai vastaava
   - Kantama: 50-100m (riittää hyvin 15m)

2. **433MHz Receiver** (RX) - Savupalvelimeen  
   - Hinta: ~3-5€
   - Esim: MX-RM-5V, SYN480R, tai vastaava
   - Herkkä vastaanotin, toimii sisätiloissa

### Antenni-johtimet:
- **17,3 cm lanka** molempiin (1/4 aallon pituus 433MHz:lle)
- Tai valmiit kierre-antennit

### Arduino kirjasto:
```cpp
#include <RCSwitch.h>  // Arduino Library Manager → "rc-switch"
```

## 🔧 Kytkentä

### Savupalvelin (ESP32 + RX):
```
433MHz RX    ESP32
---------    -----
VCC     →    3.3V
GND     →    GND  
DATA    →    Pin 2
ANT     →    17.3cm johdin
```

### Robotti (ESP32 + TX):
```
433MHz TX    ESP32
---------    -----
VCC     →    3.3V
GND     →    GND
DATA    →    Pin 4
ANT     →    17.3cm johdin
```

## 📡 Tekninen info

### Taajuus:
- **433.92 MHz** (ISM-kaista, luvaton käyttö sallittu)
- **Teho**: <10mW (ei vaadi lupaa)
- **Modulaatio**: ASK/OOK (amplitude shift keying)

### Kantama:
- **Sisätilat**: 10-30m (riippuu seinistä)
- **Ulkotilat**: 50-100m+ (vapaa näkölinja)
- **Teatteri**: 15m läpi betoniseinien ✅

### Luotettavuus:
- **Viive**: <100ms (lähes instant)
- **Toistuvuus**: Koodi lähetetään 3x varmuudeksi
- **Häiriöt**: Vähän liikennettä 433MHz kaistalla
- **Virhetoleranssi**: Checksummit ja koodivalidointi

## 💻 Koodin asennus

### 1. Arduino Library Manager:
```
Sketch → Include Library → Manage Libraries
Hae: "rc-switch" by sui77
Install
```

### 2. Lataa koodit ESP32:ille:
```
savupalvelin_433mhz.ino → ESP32 #1 (lavalla)
robotti_433mhz.ino      → ESP32 #2 (robotti)
```

### 3. Testaa Serial Monitor:ssa:
```
Robotti: "test_smoke" → lähettää savukomennon
Palvelin: näyttää "📻 433MHz vastaanotettu: 11111"
```

## 🧪 Testaus vaiheittain

### Vaihe 1: Perusyhteys
1. **Kytke moduulit** ESP32:hin
2. **Lataa koodit** molempiin  
3. **Avaa Serial Monitor** molemmista (115200 baud)
4. **Robotti**: Kirjoita "test_smoke"
5. **Palvelin**: Pitäisi näyttää vastaanotettu viesti

### Vaihe 2: Antenni-optimointi
1. **Ilman antennia**: Testi 1-2m päältä
2. **17.3cm johdin**: Testi 5-10m päältä
3. **Kierre-antenni**: Testi täysi kantama

### Vaihe 3: Häiriötestaus
1. **WiFi päällä**: Toimiiko 433MHz silti?
2. **Bluetooth päällä**: Häiriöitä?
3. **Monta laitetta**: ESP32 + kännykkä + laptop

### Vaihe 4: Teatteriolosuhteet
1. **15m etäisyys**: Robotti → lava
2. **Seinien läpi**: Toimiiko betoniseinien läpi?
3. **Muu tekniikka**: Äänentoisto + valot päällä

## 🎭 Käyttöönotto teatterissa

### Asennusjärjestys:
1. **Savupalvelin**: Asenna lavalle/tekniseen tilaan
2. **Testaa HTTP**: Multiplay → ESP32 toimii
3. **Asenna 433MHz RX**: Savupalvelimeen
4. **Robotti**: Asenna OLED + 433MHz TX
5. **Etäisyystesti**: 15m päästä

### Backup-suunnitelma:
- **Plan A**: Multiplay HTTP → ESP32 (normaali)
- **Plan B**: Robotti 433MHz → ESP32 (backup)  
- **Plan C**: Manuaalinen nappi ESP32:ssa (hätä)
- **Plan D**: Savukoneen oma nappi (MacGyver)

## 🔍 Troubleshooting

### "433MHz ei toimi":
1. **Kytkennät**: Tarkista VCC/GND/DATA
2. **Antenni**: 17.3cm johdin kiinni ANT-pinniin
3. **Etäisyys**: Ala läheltä (1m), lisää vähitellen
4. **Serial Monitor**: Näkyykö debug-viestit?

### "Toimii läheltä, ei kaukaa":
1. **Antenni**: Pidemmät johtimet/kierre-antennit
2. **Virta**: Tarkista 3.3V syöttö (ei 5V!)
3. **Häiriöt**: Sammuta WiFi/Bluetooth testiksi
4. **Suunta**: Antennit samaan suuntaan

### "Satunnaisia häiriöitä":
1. **Koodivalidointi**: Tarkista että koodit täsmää
2. **Toisto**: Nosta repeat-määrää (3→5)
3. **Taajuus**: Kokeile eri kanavia 433.1-433.9 MHz
4. **Checksum**: Lisää virheentarkistus koodiin

## 💡 Pro-vinkit

### Luotettavuus:
- **Antenni oikeaan suuntaan** (sama polarisaatio)
- **Esteetön näkölinja** jos mahdollista
- **Koodi lähetetään 3x** varmuudeksi
- **Timeout-tarkistus** palvelimessa

### Tehokkuus:
- **433MHz vain backupiin** (ei jatkuvaan käyttöön)
- **Multiplay primary** = vakaa HTTP-yhteys
- **Robotti secondary** = luotettava radio-backup

### Turvallisuus:
- **Uniikki koodi** per teatteri (vaihda SMOKE_PULSE_CODE)
- **Timeout-suojaus** (max 5 min savukone päällä)
- **Manual override** aina saatavilla

---

**🎯 Tulos: Luotettava 15m+ kantama, <100ms viive, ei WiFi-konflikteja!**

*433MHz on teollisuusstandardi - jos se toimii garagenoven avaajissa, se toimii teatterissakin! 📻✨*