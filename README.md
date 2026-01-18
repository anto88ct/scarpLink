# 🕵️‍♂️ LinkedIn Dorker & Scraper

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

**Uno strumento OSINT avanzato per l'estrazione automatizzata di profili LinkedIn.**

Il software prende in input il **nome di un'azienda** e scansiona i dipendenti, esportando i dati (Nome, Ruolo, Località, Link) in file Excel ordinati. Il progetto è progettato per emulare il comportamento umano e minimizzare il rischio di blocchi.

## ✨ Funzionalità

| Funzionalità | Descrizione |
| :--- | :--- |
| 🍪 **Sessione Persistente** | Mantiene il login attivo tra le sessioni salvando i cookie localmente in `chrome_data`. |
| 🤖 **Deep Scan** | Scansione approfondita simulando scroll, click e attese casuali (Human-like behavior). |
| 🔍 **Google Dorking** | Modalità "Stealth" che usa operatori di ricerca Google per trovare profili senza navigare su LinkedIn. |
| 📊 **Export Excel** | Salvataggio automatico e formattato dei risultati nella cartella `exports/`. |
| 🖥️ **Multi-Interfaccia** | Disponibile via GUI (Interfaccia Web), CLI (Terminale) e Script Dorking. |

---

## 🛠️ Installazione

### Prerequisiti
* Python 3.8 o superiore.
* Google Chrome installato sul sistema.

### 1. Clona la repository
```bash
git clone https://github.com/tuo-username/linkedin-dorker.git
cd linkedin-dorker
```

### 2. Configura l'ambiente virtuale (Consigliato)
È buona norma isolare le dipendenze del progetto per evitare conflitti.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Installa le dipendenze
```bash
pip install -r requirements.txt
```

## ⚙️ Configurazione e Primo Accesso (IMPORTANTE)
Il sistema utilizza una cartella locale chiamata **chrome_data** per salvare la sessione del browser. Non devi scrivere la password nel codice.

La cartella `chrome_data` viene creata automaticamente dallo script se non esiste. Ecco come procedere la prima volta:

1. Esegui lo script principale:
   ```bash
   python main.py
   ```
2. Si aprirà una finestra di Google Chrome controllata dal software.
3. Effettua il login manuale su LinkedIn inserendo email e password direttamente nel browser aperto.
4. Una volta entrato nella Home di LinkedIn (feed notizie), lo script rileverà l'accesso.
5. Puoi chiudere lo script.

✅ **Fatto!** Da questo momento in poi, non dovrai più fare il login. Il software userà i cookie salvati in `chrome_data` per accedere automaticamente.

## 🚀 Utilizzo
Il tool offre tre modalità di utilizzo a seconda delle tue esigenze.

### Modalità 1: Interfaccia Grafica (Consigliata)
Una dashboard web pulita e interattiva.

```bash
streamlit run ui.py
```

* Inserisci il nome dell'azienda nella barra laterale (es. "Microsoft", "Ferrari").
* Clicca su **Avvia**.
* Attendi la scansione e scarica il file Excel direttamente dalla pagina.

### Modalità 2: Linea di Comando (Deep Scan)
Per l'uso da terminale con log dettagliati delle operazioni in tempo reale.

```bash
python main.py
```

* Il sistema ti chiederà: `Azienda:`.
* Digita il nome e premi Invio.

### Modalità 3: Google Dorking
Cerca profili usando Google. Questa modalità è meno invasiva e non richiede necessariamente il login a LinkedIn (utile per ricerche preliminari).

```bash
python googleDorking.py
```

## 🛡️ Sicurezza e .gitignore
⚠️ **Attenzione:** La cartella `chrome_data` contiene i tuoi cookie di sessione (che equivalgono alla tua password). **Non caricarla mai online** (GitHub, GitLab, ecc.).

Assicurati che il tuo file `.gitignore` contenga le seguenti righe:

```text
venv/
__pycache__/
chrome_data/
exports/
.env
```

## ⚠️ Disclaimer
**LEGGERE ATTENTAMENTE**

Questo software è stato sviluppato esclusivamente a scopo educativo e di ricerca (OSINT).

* L'estrazione automatizzata di dati (scraping) da LinkedIn potrebbe violare i loro Termini di Servizio.
* L'autore non si assume alcuna responsabilità per l'uso improprio di questo strumento.
* L'autore non è responsabile per eventuali violazioni della privacy o per restrizioni (ban/sospensioni) applicate al tuo account LinkedIn.

**Si consiglia vivamente di utilizzare il tool con moderazione.**