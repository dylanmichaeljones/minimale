# 5x5 Mini-Male (Mini-Chess)

Täielikult toimiv ja lihvitud 5x5 mini-male mäng Python 3 ja Pygame graafilise liidesega, mida saab mängida arvuti vastu. Arvuti käikude arvutamiseks on kasutusel **Minimax algoritm koos Alpha-Beta kärpimise (pruning)**, vaigistusotsingu (quiescence search) ja positsiooniliste hindamistabelitega (Piece-Square Tables).

---

## Sisukord
- [Algne lauaseis ja koordinaadid](#algne-lauaseis-ja-koordinaadid)
- [Mängureeglid](#mängureeglid)
- [Arvutivastane (Minimax AI)](#arvutivastane-minimax-ai)
- [Graafiline liides ja juhtimine](#graafiline-liides-ja-juhtimine)
- [Paigaldamine ja käivitamine](#paigaldamine-ja-käivitamine)
- [Koodistruktuur](#koodistruktuur)

---

## Algne lauaseis ja koordinaadid

Mängulaud on mõõtmetega **5x5 ruutu**:
* **Veerud (failid):** `A`, `B`, `C`, `D`, `E` (vasakult paremale)
* **Read:** `1`, `2`, `3`, `4`, `5` (valge poolt vaadates alt üles)

Vastavalt nõudele asuvad etturid mõlemal poolel teisel real:
* **Valge etturid** asuvad real **2** (`A2` kuni `E2`).
* **Musta etturid** asuvad real **4** (`A4` kuni `E4` - musta poolt teine rida).
* **Rida 3** on alguses tühi puhvertsoon.

Algne paigutus põhineb klassikalisel **Gardneri 5x5 mini-malesüsteemil (Martin Gardner, 1969)**, kus tagarea vanger, ratsu, oda, lipp ja kuningas on paigutatud järgmiselt:

```text
       A     B     C     D     E
    +-----+-----+-----+-----+-----+
 5  |  V  |  R  |  O  |  L  |  K  |   (Must tagarida: vanger, ratsu, oda, lipp, kuningas)
    +-----+-----+-----+-----+-----+
 4  |  E  |  E  |  E  |  E  |  E  |   (Musta etturid - teine rida musta poolt)
    +-----+-----+-----+-----+-----+
 3  |  .  |  .  |  .  |  .  |  .  |   (Tühi rida)
    +-----+-----+-----+-----+-----+
 2  |  E  |  E  |  E  |  E  |  E  |   (Valge etturid - teine rida valge poolt)
    +-----+-----+-----+-----+-----+
 1  |  V  |  R  |  O  |  L  |  K  |   (Valge tagarida: vanger, ratsu, oda, lipp, kuningas)
    +-----+-----+-----+-----+-----+
       A     B     C     D     E
```

Eesti malenotatsiooni tähised:
* **K** – Kuningas (King)
* **L** – Lipp (Queen)
* **V** – Vanker (Rook)
* **O** – Oda (Bishop)
* **R** – Ratsu (Knight)
* **E** – Ettur (Pawn)

---

## Mängureeglid

1. **Vigurite liikumine:**
   * **Kuningas (K):** Liigub 1 ruudu mistahes suunas (horisontaalselt, vertikaalselt või diagonaalselt). Ei tohi astuda tule alla.
   * **Lipp (L):** Liigub suvalise arvu vabu ruute sirgjooneliselt või diagonaalselt.
   * **Vanker (V):** Liigub suvalise arvu vabu ruute vertikaalselt või horisontaalselt.
   * **Oda (O):** Liigub suvalise arvu vabu ruute diagonaalselt.
   * **Ratsu (R):** Liigub L-kujuliselt (2 sammu ühes ja 1 risti teises suunas), hüpates üle teiste vigurite.
   * **Ettur (E):**
     * Liigub **1 ruut otse ette** vabale ruudule.
     * Lööb **1 ruut diagonaalselt ette** vastase vigurit.
     * 5x5 minilaudadel puudub etturi topeltsamm ja en-passant (kuna laud on 5 rida pikk, viiks 2 sammu etturi koheselt vastase teisele reale).
2. **Etturi lipustumine (Promotion):**
   * Kui valge ettur jõuab 5. reale või must ettur 1. reale, asendatakse see mängija valikul lipu, vankri, oda või ratsuga. Kasutajale avaneb mugav graafiline valikuaken.
3. **Mängu lõpp:**
   * **Matt (Checkmate):** Kuningas on tule all ja seaduslikke käike tule vältimiseks pole – vastane võidab.
   * **Patt (Stalemate):** Mängijal pole seaduslikke käike, kuid kuningas ei ole tule all – viik.
   * **Kolmekordne kordus:** Kui sama lauapositsioon kordub kolm korda – viik.
   * **Ebapiisav materjal:** K vs K, K+O vs K, K+R vs K – viik.
   * **50 käigu reegel:** 50 poolkäiku ilma etturi liikumise või löömiseta – viik.

---

## Arvutivastane (Minimax AI)

Arvuti kasutab edasiarendatud **Minimax algoritmi koos Alpha-Beta kärpimisega**:
* **Alpha-Beta Pruning:** Vähendab läbivaadatavate harude arvu üle 85%, tagades välkkiire mõtlemisaja (< 0.2s).
* **Käikude järjestamine (Move Ordering):**
  1. Parim käik transponeerimistabelist.
  2. Löömised järjestatuna **MVV-LVA** meetodil (Most Valuable Victim – Least Valuable Aggressor, nt etturiga lipu löömine on kõrgeima prioriteediga).
  3. Etturi lipustamised.
  4. Šahhid ja positsioonilised etturid.
* **Vaigistusotsing (Quiescence Search):** Otsib lehtedes edasi löömiskäike, et vältida "horisondi efekti" (kus arvuti ei märkaks kohest vastulööki).
* **Positsioonilised hindamistabelid (PST):** Igal viguril on kohandatud 5x5 väärtustabel:
  * Ratsu ja oda eelistavad tsentrit (ruut C3 ja siserõngas).
  * Etturid saavad kõrgema hinde mida lähemal nad on 5. reale lipustumisele.
  * Kuningas püsib avangus ja keskmängus turvaliselt nurgas, lõppmängus liigub tsentrisse.
* **Transponeerimistabel:** Salvestab juba arvutatud lauaseisude hinnangud.
* **Raskusastmed:**
  * **Lihtne (Easy):** Sügavus 2, valib vahel teise parima käigu (sobib algajale).
  * **Keskmine (Medium):** Sügavus 3, kindel ja taktikaliselt täpne malemängija.
  * **Raske (Hard):** Sügavus 4 + vaigistusotsing, meistritasemel 5x5 malemootor.
* **Asünkroonne taustalõim:** Arvuti arvutab oma käiku taustalõimes (`threading.Thread`), mistõttu kasutajaliides ei kiilu kunagi kinni ja jääb sujuvaks.

---

## Graafiline liides ja juhtimine

* **Käikude tegemine:**
  * **Klõpsamine:** Klõpsa oma viguril ja seejärel sihtruudul.
  * **Lohistamine (Drag & Drop):** Hoia hiire vasakut nuppu all ja lohista vigur sihtruudule.
* **Visuaalsed vihjed:**
  * Rohelised täpid näitavad võimalikke vabu sihtruute.
  * Punased rõngad näitavad vastase vigurite löömise võimalusi.
  * Valitud ruut on valgustatud helerohelisega.
  * Viimane käik on esile tõstetud pehme kuldse tooniga.
  * Tule all (šahhis) olev kuningas helendab punaselt.
* **Küljepaneel:**
  * Seisumärgis (kelle käik, šahh, matt teade).
  * Äravõetud vigurid mõlemale poolele koos punktiedu näidikuga (`+3`, `+5`).
  * Käikude ametlik ajalugu eesti algebrailises notatsioonis (nt `1. c2-c3 b4xc3`, `Ld1xd5+`).
  * **Uus mäng:** Alustab uut mängu.
  * **Võta tagasi:** Tühistab arvuti ja mängija viimase käigu (saab proovida teist strateegiat).
  * **Mängija Valge/Must:** Võimalus mängida nii valgete kui ka mustadega.
  * **Pööra laud:** Pöörab vaadet lauale.
  * **Raskusaste:** Lülitab raskusastet (Lihtne / Keskmine / Raske).
* **Kiirklahvid:**
  * `U` või `Ctrl+Z`: Võta käik tagasi
  * `N`: Uus mäng
  * `F`: Pööra laud ümber
  * `Esc`: Tühista valik

---

## Paigaldamine ja käivitamine

### 1. Nõuded
* Python 3.10+ (toetatud ka Python 3.14+)
* `pygame-ce` või `pygame`

### 2. Paigaldamine
```bash
pip install -r requirements.txt
```
*(Märkus: Python 3.14 puhul on soovitatav `pygame-ce`, mille paigaldab `requirements.txt` automaatselt).*

### 3. Käivitamine
```bash
python main.py
```

### 4. Testide käivitamine
```bash
python test_board.py
python test_ai.py
python test_gameplay.py
```

---

## Koodistruktuur

* `main.py` – Mängu käivitusfail ja tervituskonsool.
* `gui.py` – Pygame graafiline liides, sündmuste haldus, nupud, animatsioonid ja modaalid.
* `board.py` – Laua loogika, vigurite reeglid, käikude genereerimine, šahh ja matt.
* `ai.py` – Minimax algoritm, Alpha-Beta kärpimine, vaigistusotsing, hindamisfunktsioon.
* `pieces_svg.py` – Standardsed skaleeritavad SVG vektorgraafika vigurid Pygame pindadele.
* `constants.py` – Konstandid, värvid, geomeetria, eesti malenotatsioon ja algseis.
* `requirements.txt` – Projekti sõltuvused.
