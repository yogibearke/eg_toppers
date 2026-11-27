# 📈 EG_toppers Stock Dashboard

Een snel, interactief aandelendashboard en screener voor **2.089 aandelen** uit de **EasyGrowth Cloud**, volledig gebouwd als statische webapplicatie (HTML, CSS en JavaScript) — direct geschikt voor **GitHub Pages** én lokaal gebruik.

**Live Dashboard:** [https://yogibearke.github.io/eg_toppers/](https://yogibearke.github.io/eg_toppers/)

---

## ✨ Belangrijkste Functionaliteiten

* **Kant-en-klare & eigen beleggingsprofielen** *(automatisch bewaard in `localStorage`)*:
  * 🐢 **Rustige Groeiers (10j & 5j):** Bedrijven die over 10 of 5 jaar met minstens **+15% per jaar** groeiden met een uitzonderlijk strakke log-lineaire trend (**TK / $R^2 \ge 95\%$**), exclusief cyclische sectoren.
  * 🏛️ **Compounders (10j):** Structurele kapitaalallocators en kwaliteitsbedrijven/holdings met $\ge 15\%$ koersgroei/jr en $R^2 \ge 85\%$ over 10 jaar.
  * 💎 **Echte Kwaliteitsgroeiers (5j):** Fundamentele toppers met hoge rentabiliteit ($\text{ROIC} \ge 18\%$), sterke prijszettingskracht ($\text{Nettomarge} \ge 15\%$) en dubbelcijferige omzet- en winstgroei.
  * 🚀 **De Top van het Moment (1j):** Actuele koplopers met sterke 1-jaarstrend en winstversnelling.
  * ⚡ **Dubbele Turbo:** Gelijktijdige omzet- én winstgroei van minstens $+20\%$ met $\text{ROIC} \ge 15\%$.
* **Flexibele Screener met `Any`-knoppen:** Stel per parameter zelf drempelwaarden in of schakel individuele criteria uit, wissel tussen tijdframes (**1J, 3J, 5J, 10J**) en beheer of bewaar eigen profielen.
* **Geïntegreerd Zijvenster & 2e Scherm Synchronisatie:**
  * **EasyGrowth Grafiek:** Bekijk direct de officiële EasyGrowth-pagina van het geselecteerde aandeel in het zijpaneel of koppel een extern venster op een tweede beeldscherm.
  * **Profiel & Factoren:** Duidelijke toelichting bij de filosofie van het gekozen profiel, een directe check per criterium voor het geselecteerde aandeel en visuele meters voor **ROIC**, **Nettomarge**, **Winstgroei** en **TK ($R^2$)**.
* **1-Klik CSV Kopiëren:** Kopieer alle gefilterde tickers direct als kommagescheiden lijst naar het klembord.

---

## 📐 Gebruikte Indicatoren

| Indicator | Betekenis |
| :--- | :--- |
| **ROIC (5j)** | *Return on Invested Capital* — het 5-jaars gemiddeld rendement op geïnvesteerd kapitaal (%). |
| **Omzetgroei** | Meerjarige groei van de bedrijfsomzet (%). |
| **Winstgroei (EPS)** | Groei van de winst per aandeel / WPA (%). |
| **Nettomarge** | Nettowinst als percentage van de omzet — maatstaf voor *pricing power* en economische slotgracht (%). |
| **Koersgroei / jr** | Geannualiseerd koersrendement (CAGR) over het gekozen tijdframe (1J, 3J, 5J of 10J). |
| **TK / $R^2$** | **Trendkwaliteit ($R^2 \times 100$)** van de log-lineaire regressielijn over het gekozen tijdframe (`0 – 100`). Hoe dichter bij `100`, hoe rechter en rustiger de koers langs een exponentiële groeilijn stijgt zonder diepe zaagtanden. |

---

## 📁 Bestandsstructuur

Het project is bewust minimaal en overzichtelijk gehouden:

```text
Eg_toppers/
├── index.html            # De volledige webapplicatie (Desktop + GSM UI & PWA-ondersteuning)
├── eg_live_universe.js   # Gecachte dataset van 2.089 aandelen incl. voorberekende 1J/3J/5J/10J metrics
├── manifest.json         # Web App Manifest (voor installatie als standalone app op GSM & pc)
├── sw.js                 # Service Worker voor snelle laadtijden & offline fallback
├── icon.svg              # Scherp vector app-icoon voor het startscherm
├── update_universe.py    # Optioneel Python-script om eg_live_universe.js lokaal te verversen
├── .gitignore            # Git-uitsluitingen voor tijdelijke systeembestanden
└── README.md             # Documentatie
```

---

## 📱 Installeren als Webapp op je GSM (iPhone & Android)

**EG_toppers** is een volwaardige **Progressive Web App (PWA)** met een aangepaste mobiele interface:
* **Android (Chrome):** Open [yogibearke.github.io/eg_toppers](https://yogibearke.github.io/eg_toppers/) en tik bovenaan op **Installeer App** (of kies via het menu `⋮` → *Toevoegen aan startscherm / App installeren*).
* **iPhone / iPad (Safari):** Open de link in Safari, tik onderaan op het **Deel-icoon** (`⬆️`) en kies **Zet op beginscherm**.
* **Slimme EasyGrowth-koppeling op GSM:** Op mobiel klapt het zijpaneel niet ongewenst over de lijst heen en zijn gedetailleerde filters netjes inklapbaar. Tik je op een aandeel, dan zie je direct de **Profiel & Factoren**-analyse én een grote knop om het aandeel rechtstreeks op volledig scherm te openen in de **EasyGrowth webapp / browser** (met behoud van je eigen EasyGrowth-login).

---

## 🚀 Publiceren op GitHub Pages

Omdat de applicatie 100% statisch is, kun je hem gratis en zonder server hosten op **GitHub Pages**:

1. Maak een nieuwe (of gebruik een bestaande) repository op GitHub.
2. Upload of push `index.html`, `eg_live_universe.js`, `update_universe.py`, `.gitignore` en `README.md` naar de `main`-branch:
   ```bash
   git init
   git add .
   git commit -m "Initial release EG_toppers Stock Dashboard"
   git branch -M main
   git remote add origin https://github.com/yogibearke/eg_toppers.git
   git push -u origin main
   ```
3. Ga op GitHub naar **Settings → Pages**.
4. Kies bij **Build and deployment**:
   * **Source:** `Deploy from a branch`
   * **Branch:** `main` en map `/ (root)` → klik op **Save**.
5. Na ongeveer 1 minuut staat je dashboard live op:
   [https://yogibearke.github.io/eg_toppers/](https://yogibearke.github.io/eg_toppers/)

---

## 🔄 Automatische Data-Update (Elke Weekdag om Middernacht)

De dataset (`eg_live_universe.js`) wordt **volledig automatisch** ververst via **GitHub Actions** ([.github/workflows/update-universe.yml](.github/workflows/update-universe.yml)):
* **Schema:** Elke weekdag om **middernacht** (`00:00 CET` / `23:00 UTC`), na het sluiten van zowel de Europese beurzen als Wall Street.
* **Handmatig starten:** Je kunt ook op elk gewenst moment op GitHub onder het tabblad **Actions → Update EasyGrowth Dataset → Run workflow** met één klik direct een verversing starten.
* **Lokaal testen:** Start een simpele lokale webserver met `python -m http.server 8080` en open `http://localhost:8080`. Wil je lokaal zelf de data verversen, voer dan `python update_universe.py` uit.
