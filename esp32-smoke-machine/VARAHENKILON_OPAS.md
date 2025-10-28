# 🎭 Savukone-järjestelmä: Varahenkilön opas

**Täydellinen käyttöohje jos Rauli ei ole paikalla**

---

## 🚨 PIKAOHJEET (5 minuuttia lukuaikaa)

### Mikä tämä järjestelmä on?
- **Savukone** sijaitsee lavalla, 15 metrin päässä sinusta
- **Robotti-kaukolaukaisin** on sinun kädessäsi (näyttää silmiä)
- **433MHz radio** lähettää komennot luotettavasti
- **Multiplay-ohjelma** hoitaa normaalisti kaiken automaattisesti
- **MUTTA: Sinä olet varalla** jos tekniikka pettää!

### Hätätilanteessa kun Multiplay kaatuu:
1. **Ota robotti** käsiisi
2. **Nosta robotin päätä** ylöspäin → nappi paljastuu pään alta
3. **Paina nappia** lujaa → savu lähtee VÄLITTÖMÄSTI
4. **Näytössä lukee** "SMOKE SENT!" (vahvistus)
5. **Savukone** pyörii automaattisesti 5 sekuntia ja sammuu

**SE ON SIINÄ! Ei sen kummempaa!** 🎯

---

## 📋 VALMISTELUT ENNEN ESITYSTÄ

### 🔌 Tarkista virrat (15 minuuttia ennen):
- [ ] **Savukone**: Virtajohto pistorasiaan + ON-kytkin päällä
- [ ] **ESP32 laitteisto**: USB-virta kiinni (lavalla oleva pieni laatikko)
- [ ] **Robotti**: Akku latausjohto irti + päällä (jos näyttö näkyy = OK)

### 🧪 Testaa toiminta:
- [ ] **Robotti näyttö**: Näkyykö "silmät" ruudulla?
- [ ] **Nosta päätä**: Paljastuuko nappi pään alta?  
- [ ] **Testipainallus**: Paina nappia → pitäisi näkyä "SMOKE SENT!"
- [ ] **Savukone**: Tulikohan savua 5 sekunnin ajan?

### 💻 Multiplay-tarkistus:
- [ ] **Avaa Multiplay** tietokoneella
- [ ] **Lataa cue-lista**: Tiedosto nimeltä "*.json"
- [ ] **Testaa yksi cue**: Fire cue → lähtikö savu automaattisesti?
- [ ] **Jos ei toimi** → Robotti on varmistuskeino!

---

## 🎵 ESITYKSEN AIKANA

### Normaalitilanne (kaikki toimii):
- **Multiplay hoitaa** savukoneen automaattisesti
- **Sinä vain seuraat** esitystä ja nautit
- **Robotti näyttää** silmien liikkeillä että järjestelmä toimii

### Varatilanne (Multiplay kaatuu):
- **Robotti näyttö** vaihtuu: "BACKUP MODE"
- **Seuraa nuotteja** tai käsikirjoitusta
- **Laukaise savu** käsin oikeissa kohdissa
- **Ajoitus**: Yleensä 2-3 sekuntia ennen kuin halutaan savua näkyvälle

---

## 🤖 ROBOTTI-KAUKOLAUKAISIN

### Fyysinen rakenne:
```
[Näyttö päässä] ← OLED ruutu jossa "silmät"
      |
[Nostettava pää] ← Nosta tämä ylös käsin
      |  
[NAPPI PIILOSSA] ← Paljastuu kun nostat pään
      |
[Vartalo] ← Akku ja elektroniikka sisällä
```

### Näytön merkit:
- **Silmien liike** = Järjestelmä toimii normaalisti
- **"WiFi: Connected"** = Yhteys OK
- **"SMOKE SENT!"** = Savukomento lähetetty onnistuneesti  
- **"BACKUP MODE"** = Multiplay ei toimi, sinä ohjaat
- **"Battery: 67%"** = Akun tila prosentteina
- **Tyhjä ruutu** = Akku loppu → VAIHDA AKKU!

### Jos akku loppuu (ruutu sammuu):
1. **Käännä robotti** ympäri
2. **Etsi kansi** (ruuvit tai kiinnikkeet)
3. **Vaihda powerbank** tai kiinnitä lataustikku
4. **Sulje kansi** → ruudun pitäisi herätä

---

## 🎼 TYYPILLISET SAVUKOHDAT TEATTERISSA

### Milloin savua tarvitaan:
- **Jännittävät sisääntulot** (paha hahmo saapuu)
- **Taistelukohtaukset** ja räjähdykset  
- **Yliluonnolliset tapahtumat** (aaveet, taikuus)
- **Dramaattiset loppukohtaukset**

### Ajoitus (esimerkkejä):
- **3 sekuntia ENNEN** kun näyttelijä alkaa laulaa
- **Orkesterin fanfaarien** alkaessa
- **Kun näyttelijä nostaa käden** tms. sovittu merkki
- **Ennen kuin haluat savun näkyvän** (savu leviää hitaasti)

---

## 🔧 ONGELMATILANTEET JA RATKAISUT

### "Robotti ei reagoi napin painallukseen":
1. **Akku loppu?** → Näkyykö ruudulla mitään?
2. **Pään nosto?** → Kuuluuko "klik" kun nostat?  
3. **Nappi kunnossa?** → Tuntuu painuvan sisään?
4. **Odota hetki** → Yrità uudelleen 2-3 sekunnin kuluttua

### "Savu ei tule vaikka robotti sanoo SENT":
1. **Robotti toimii oikein** → Vika on savukoneessa
2. **Kävele lavalle** (jos turvallista kesken kohtauksen)
3. **Tarkista savukone**: 
   - Virta päällä? (ON-nappi)
   - Savuneste riittää? (säiliö)
   - Kuuma tarpeeksi? (odota 2-3 min)
4. **Hätälaukaisu**: Paina savukoneen omaa nappia

### "Multiplay-ohjelma kaatuu":
1. **Älä paniikki!** → Robotti hoitaa tilanteen
2. **Vaihda varatilanmoodiin** mielessäsi
3. **Seuraa nuotteja** tai librettoa  
4. **Laukaise savu** itse sopivissa kohdissa
5. **Esitys jatkuu** → yleisö ei huomaa teknisiä ongelmia

### "Kaikki kaatuu (worst case)":
1. **MacGyver-tila** → Kävele lavalle jos mahdollista
2. **Savukoneen oma nappi**: ON → odota 5 sek → OFF
3. **Improvisoi**: Käytä kaikkea käytettävissä olevaa
4. **Muista**: Show must go on! 🎭

---

## 📱 YHTEYSTIEDOT HÄTÄÄN

### Soita/tekstaa jos iso ongelma:

**Rauli (päävastaava):**
- Puhelin: ___________________
- WhatsApp: ___________________

**Tavarainen teknikko:**  
- Puhelin: ___________________

**Teatterinjohto (päätökset):**
- Puhelin: ___________________

### WhatsApp-ryhmä: "Tekniikka LIVE"
- Mukana: Rauli, sinä, muut teknikot
- Käytä esityksen aikana pikakommunikointiin

---

## 🌐 VERKKOTIEDOT (täytä käsin)

### WiFi-verkko (jos tarvitaan):
- **Verkko**: ___________________
- **Salasana**: ___________________

### Multiplay-tietokone:
- **IP-osoite**: ___________________  
- **Käyttäjä**: ___________________
- **Salasana**: ___________________

### Savupalvelin (ESP32):
- **IP-osoite**: ___________________
- **Web-osoite**: http://___________________

---

## ✅ TARKISTUSLISTA ESITYKSEEN

### 1 tunti ennen esitystä:
- [ ] Savukone: Virta + savuneste riittää
- [ ] ESP32: Käynnissä ja yhdistetty
- [ ] Robotti: Akku täynnä + näyttö toimii  
- [ ] Multiplay: Ohjelma auki + cue-lista ladattu
- [ ] **Testaa**: Yksi savupulssi päästä päähän

### 30 minuuttia ennen esitystä:
- [ ] Radio-yhteys: Robotti → savukone toimii
- [ ] Näyttö: Robotti näyttää tilan normaalisti
- [ ] Backup-suunnitelma: Tiedät manuaaliset napit
- [ ] Ajoitus: Olet tutustunut nuotteihin/käsikirjoitukseen

### Esityksen aikana:
- [ ] Robotti käteen + valmius-asento
- [ ] Seuraa Multiplayta ja nuotteja
- [ ] Jos automaattinen savu EI tule → manuaali välittömästi  
- [ ] Kirjaa ylös kaikki ongelmat myöhempää korjausta varten

### Esityksen jälkeen:
- [ ] Sammuta savukone turvallisesti (OFF + irti seinästä)
- [ ] Laita robotti lataukseen
- [ ] Raportoi Raulille mitä tapahtui (toimiko/ei toiminut)
- [ ] Tallenna Multiplay-logit varmuuden vuoksi

---

## 🎯 MUISTA NÄMÄ TÄRKEIMMÄT ASIAT!

### ✅ TÄRKEIN:
1. **Esitys jatkuu** vaikka tekniikka pettää
2. **Turvallisuus ensin** - älä mene vaarallisiin paikkoihin
3. **Maalaisjärki sallittu** - käytä kaikkea apua  
4. **Robotti on luotettava** - luota siihen hätätilanteessa!

### ❌ ÄLÄ KOSKAAN:
- Paniikoi jos joku laite kaatuu
- Mene lavalle kesken kohtauksen (paitsi hätä)
- Unohda sammuttaa savukone esityksen lopuksi
- Jätä raportoimatta ongelmia Raulille

---

## 🎭 LOPUKSI

**Sinä pystyt tähän!** Järjestelmä on suunniteltu niin, että kuka tahansa osaa käyttää sitä. Robotti-kaukolaukaisin on idioottivarmasti toimiva - nosta pää, paina nappi, savu tulee. 

**Esitys on tärkeintä** - tekniikan on tarkoitus palvella taidetta, ei päinvastoin. Jos joku menee pieleen, improvisointi on sallittua ja jopa suotavaa.

**Rauli on aina puhelun päässä** jos tarvitset apua. Mutta luultavasti et tarvitse - olet täysin kykenevä hoitamaan tämän!

---

**Show must go on! 🎪✨**

*Tämä opas on tulostettu ___/___/2025*  
*Päivitetty versio aina saatavilla: github.com/RauliV/midi-fade-generator*