# Libero---Virgilio-Automazione-Email
Creazione automatizzata delle email di libero e virgilio. Navigazione tramite cloackbrowser-playwright. 

# Libero / Virgilio — Creazione Automatizzata

Script Python per automatizzare la registrazione su Libero e Virgilio, con OTP via OnlineSim e supporto proxy Webshare opzionale.

> ⚠️ **Leggi [DISCLAIMER.md](DISCLAIMER.md) prima di usare.** L'uso è a tuo rischio: la creazione automatizzata di account viola quasi certamente i Termini di Servizio di Libero/Virgilio.

---

## 📋 Requisiti

- Python 3.9+
- Account [OnlineSim](https://onlinesim.io) con credito (per SMS)
- (Opzionale) Account [Webshare](https://webshare.io) per proxy

---

## 🚀 Installazione

### 1. Installa Python
Da <https://www.python.org/downloads/> — spunta **"Add Python to PATH"**.

### 2. Scarica il progetto
```bash
git clone https://github.com/palianitsia/Libero---Virgilio-Automazione-Email.git
cd Libero---Virgilio-Automazione-Email


Se non usi git: Code → Download ZIP e scompatta.

### 3. Installa dipendenze
bash
pip install -r requirements.txt

4. Configura
bash
copy config.example.txt config.txt    # Windows
cp config.example.txt config.txt      # Linux/macOS
Apri config.txt e incolla la tua API key OnlineSim.

5. Aggiungi account
Copia dati_account.example.txt in dati_account.txt e inserisci le righe nel formato:

text
USERNAME-PASSWORD-NOME-COGNOME-DD/MM/AAAA-M|F-COMUNE
Usa R come comune per sceglierne uno casuale da com_prov.json.

Esempio:

text
mariorossi92-Password123!-Mario-Rossi-12/03/1992-M-R

6. Avvia
bash
python "Libero-Virglio Creazione Automatizzata v1.0.py"
🔑 CloakBrowser — Come ottenere la licenza
Lo script usa CloakBrowser per il browser. Si installa con pip ma il binario Chromium (scaricato al primo avvio) richiede una licenza.

Installazione
bash
pip install cloakbrowser
Il binario viene scaricato automaticamente in ~/.cloakbrowser/ al primo utilizzo.

Come ottenere la licenza
Opzione A — Build gratuita v146 (nessuna chiave)
Non devi fare nulla. Se non configuri nulla, CloakBrowser usa la build v146 scaricata da GitHub Releases, senza bisogno di chiave.

Opzione B — Build recente gratuita (1 sessione)

Vai su https://cloakbrowser.dev/free

Fai login con GitHub

Ottieni una chiave gratuita cb_...

Attivala in uno di questi modi:

bash
# Metodo 1: login da terminale
cloakbrowser login

# Metodo 2: variabile d'ambiente
export CLOAKBROWSER_LICENSE_KEY=cb_xxxxxxxx     # Linux/macOS
$env:CLOAKBROWSER_LICENSE_KEY="cb_xxxxxxxx"     # Windows PowerShell
Questa modalità dà 1 sessione browser simultanea.

Opzione C — Pro (a pagamento)
Sessioni multiple. Chiave da https://cloakbrowser.dev.
