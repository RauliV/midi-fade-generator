# 🎭 Savukone-järjestelmä: Tuurajan opas

**Täydellinen käyttöohje jos Rauli ei ole paikalla**

## 🚨 HÄTÄ-YHTEENVETO (5 min lukuaika)

### Mikä tämä on?
- **Savukone** 15m päässä lavalla
- **Robotti-kaukolaukaisin** sinun kädessäsi
- **433MHz radio** = luotettavin yhteys
- **Multiplay** hoitaa automaattisesti, MUTTA...
- **Sinä olet backup** jos tekniikka pettää!

### Hätätilanteessa (Multiplay kaatuu):
1. **Ota robotti** käteen
2. **Nosta päätä** ylös → nappi paljastuu  
3. **Paina nappia** → savu lähtee HETI
4. **OLED näyttää** "SMOKE SENT!" 
5. **Savukone** pyörii 5 sekuntia

**SE ON SIINÄ!** 🎯

---

## 📋 TÄYDELLINEN OHJE

### 🎪 SHOW SETUP

#### Ennen esitystä (15 min):
1. **Tarkista virrat**:
   - [ ] Savukone: virtajohto kiinni
   - [ ] ESP32 #1: USB-virta (lava)  
   - [ ] ESP32 #2: Akku (robotti)

2. **Testaa yhteys**:
   - [ ] Robotti: OLED näyttää silmät
   - [ ] Nosta päätä → nappi näkyy
   - [ ] Paina nappia → "SMOKE SENT!"
   - [ ] Savukone: savu tulee 5 sek

3. **Multiplay-testi**:
   - [ ] Avaa Multiplay tietokoneella
   - [ ] Lataa cue-lista (*.json)
   - [ ] Testaa: Fire cue → savu lähtee
   - [ ] Jos ei toimi → **robotti on backup!**

#### Show'n aikana:
- **Tavallisesti**: Multiplay hoitaa automaattisesti
- **Jos Multiplay kaatuu**: Käytä robottia manuaalisesti
- **Timing**: Seuraa nuotteja/librettoa, laukaise oikeissa kohdissa

### 🤖 ROBOTTI-KAUKOLAUKAISIN

#### Fyysinen rakenne:
```
    [OLED-silmät]  ← Näyttö päässä
         |
    [Nostettava pää]  ← Nosta ylös
         |
    [Painonappi]  ← Piilossa pään alla
         |  
    [Vartalo/akku]  ← ESP32 + akku sisällä
```

#### OLED-näytön tilat:
- **Silmät keskellä** = Valmis
- **"WiFi: Connected"** = Yhteys OK
- **"SMOKE SENT!"** = Komento lähetetty
- **"Battery: 87%"** = Akun tila
- **Tyhjä näyttö** = Akku loppu → VAIHDA!

#### Akun vaihto (jos OLED sammuu):
1. **Käännä robotti** ympäri
2. **Avaa kansi** (ruuvit/kiinnikkeet)
3. **Vaihda USB-powerbank** / lataustikkujohto
4. **Sulje kansi** → OLED herää

### 📻 433MHz RADIO-TEKNOLOGIA

#### Miksi 433MHz?
- **Kantama**: 50-100m (riittää 15m)
- **Seinien läpi**: Toimii betoniseinienkin läpi
- **Ei WiFi-häiriöitä**: Oma taajuus
- **Instant**: Ei viivettä (< 100ms)
- **Luotettava**: Teollisuusstandardi

#### Toimintaperiaate:
```
Robotti [433MHz TX] ~~~> [433MHz RX] ESP32 → Rele → Savukone
   ^                                                    ^
Sinä painat nappia                           Savu tulee ulos
```

### 🎵 SHOW-KOORDINAATIO

#### Multiplay + Robotti yhteiskäytössä:

**Normaali (kaikki toimii):**
1. Multiplay lähettää automaattisesti
2. Robotti näyttää tilan OLED:ssa  
3. Sinä vain seuraat

**Backup (Multiplay kaatuu):**
1. OLED näyttää: "BACKUP MODE"
2. Seuraa nuotteja/librettoa
3. Laukaise itse oikeissa kohdissa

**Hätä (kaikki kaatuu):**
1. Savukone voidaan käynnistää myös **manuaalisesti**
2. Kävele lavalle → paina savukoneen ON-nappia
3. Odota 5 sek → paina OFF

### 🎼 TYYPILLISET SAVUKOHDAT

#### Ooppera/Musikaali:
- **Dramaattiset sisääntulot** 
- **Taistelukohtaukset**
- **Yliluonnolliset ilmestykset**
- **Loppuräjähdykset**

#### Ajoitus (esimerkkejä):
- **3 sekuntia ENNEN** laulunsanoja
- **Fanfaarien alkaessa**  
- **Orkesterin crescendon huipussa**
- **Kun näyttelijä nostaa käden**

### 🔧 ONGELMATILANTEITA

#### "Robotti ei reagoi":
1. **Tarkista akku**: OLED näyttää jotain?
2. **Nosta päätä**: Kuuluuko klik?
3. **Paina nappia**: Tuntuu painuvan?
4. **OLED näyttää**: "SMOKE SENT!"?

#### "Savu ei tule":
1. **Robotti toimii** → Ongelma on savukoneessa
2. **Kävele lavalle** (jos turvallista)
3. **Tarkista savukone**: Virta päällä? Neste riittää?
4. **Manuaalinen käynnistys**: Savukoneen oma nappi

#### "Multiplay kaatuu":
1. **Älä paniikki** → Robotti hoitaa!
2. **Vaihda backup-moodiin**
3. **Seuraa nuotteja** → laukaise itse
4. **Showhan jatkuu** → yleisö ei huomaa

#### "Kaikki kaatuu":
1. **MacGyver-mode** → lavalle kävelemään
2. **Savukone**: Manuaalinen ON/OFF
3. **Improvisointi**: Käytä mitä on käytettävissä
4. **Show must go on!** 🎭

### 📱 YHTEYSTIEDOT

#### Hätätilanteessa soita/tekstaa:
- **Rauli**: [PUHELINNUMERO]
- **Teknikko #2**: [VARATIIMI]
- **Teatterinjohto**: [PÄÄTÖKSENTEKO]

#### WhatsApp-ryhmä: "Tekniikka LIVE"
- Rauli, sinä, muut teknikot
- Reaaliaikainen viestintä show'n aikana

### 📋 TARKISTUSLISTA ESITYKSEEN

#### 1 tunti ennen (Setup):
- [ ] Savukone: Virta + neste
- [ ] ESP32 #1: Käynnissä lavalla  
- [ ] Robotti: Akku täynnä
- [ ] Multiplay: Cue-lista ladattu
- [ ] Testaa: Yksi savupulssi end-to-end

#### 30 min ennen (Final check):
- [ ] 433MHz yhteys: Robotti → savukone
- [ ] OLED: Näyttää tilan normaalisti
- [ ] Backup-suunnitelma: Tiedät manuaaliset napit
- [ ] Ajoitus: Olet lukenut nuotit/libredot

#### Show aikana (Live):
- [ ] Robotti käteen, valmius
- [ ] Silmä nuotteihin/Multiplayhin
- [ ] Jos auto-savu EI tule → manuaali heti
- [ ] Dokumentoi ongelmat myöhempää varten

#### Show jälkeen (Cleanup):
- [ ] Sammuta savukone (turvallista)
- [ ] Robotti lataukseen
- [ ] Raportoi Raulille mitä tapahtui
- [ ] Varmuuskopioi Multiplay-logit

---

## 🎯 MUISTA!

### ✅ TÄRKEINTÄ:
1. **Show jatkuu** vaikka tekniikka pettää
2. **Turvallisuus ensin** - älä mene vaaraan
3. **Improvisaatio sallittu** - käytä maalaisjärkeä
4. **Robotti on backup** - luota siihen!

### ❌ ÄLÄ:
- Panikoi jos joku kaatuu
- Mene lavalle kesken kohtauksen (jos ei hätä)
- Unohda sammuttaa savukone lopuksi
- Jätä dokumentoimatta ongelmia

---

**Sinä pystyt tähän! Show must go on! 🎭✨**

*Rauli on vain puhelun päässä jos tarvitset apua.*