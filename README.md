# Libero / Virgilio — Creazione Automatizzata

Creazione automatizzata delle email di Libero e Virgilio. Navigazione tramite **CloakBrowser + Playwright**, con OTP via **OnlineSim** e supporto proxy **Webshare** opzionale.

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
```
Se non usi git: **Code → Download ZIP** e scompatta.

### 3. Installa dipendenze
```bash
pip install -r requirements.txt
```

### 4. Configura
```bash
copy config.example.txt config.txt    # Windows
cp config.example.txt config.txt      # Linux/macOS
```
Apri `config.txt` e incolla la tua **API key OnlineSim**.

### 5. Aggiungi account
Copia `dati_account.example.txt` in `dati_account.txt` e inserisci le righe nel formato:
```
USERNAME-PASSWORD-NOME-COGNOME-DD/MM/AAAA-M|F-COMUNE
```
Usa `R` come comune per sceglierne uno casuale da `com_prov.json`.

Esempio:
```
mariorossi92-Password123!-Mario-Rossi-12/03/1992-M-R
```

### 6. Avvia
```bash
python "Libero-Virglio Creazione Automatizzata v1.0.py"
```

---

## 🔑 CloakBrowser — Come ottenere la licenza

Lo script usa **CloakBrowser** per il browser. Si installa con `pip` ma il binario Chromium (scaricato al primo avvio) richiede una licenza.

### Installazione
```bash
pip install cloakbrowser
```
Il binario viene scaricato automaticamente in `~/.cloakbrowser/` al primo utilizzo.

### Come ottenere la licenza

**Opzione A — Build gratuita v146 (nessuna chiave)**
Non devi fare nulla. Se non configuri nulla, CloakBrowser usa la build v146 scaricata da GitHub Releases, **senza bisogno di chiave**.

**Opzione B — Build recente gratuita (1 sessione)**
1. Vai su <https://cloakbrowser.dev/free>
2. Fai login con GitHub
3. Ottieni una chiave gratuita `cb_...`
4. Attivala in uno di questi modi:

```bash
# Metodo 1: login da terminale
cloakbrowser login

# Metodo 2: variabile d'ambiente
export CLOAKBROWSER_LICENSE_KEY=cb_xxxxxxxx     # Linux/macOS
$env:CLOAKBROWSER_LICENSE_KEY="cb_xxxxxxxx"     # Windows PowerShell
```

Questa modalità dà **1 sessione browser simultanea**.

**Opzione C — Pro (a pagamento)**
Sessioni multiple. Chiave da <https://cloakbrowser.dev>.

---

## ⚙️ Come funziona (in breve)

1. Legge `config.txt` e `dati_account.txt`.
2. Apre il browser (CloakBrowser) sulla pagina di registrazione.
3. Compila i 3 step: credenziali → dati anagrafici → numero di telefono.
4. Richiede un numero a OnlineSim, attende l'SMS, inserisce il PIN.
5. Salva i cookie in `cookies/USERNAME.json` (se attivo).
6. Sposta gli account creati in `account_creati.txt`.

---

## 🧩 File del progetto

| File | Descrizione |
|------|-------------|
| `Libero-Virglio Creazione Automatizzata v1.0.py` | Script principale |
| `config.txt` | Configurazione (NON pubblicare) |
| `dati_account.txt` | Account da creare (NON pubblicare) |
| `account_creati.txt` | Account creati con successo |
| `com_prov.json` | Lista comuni/province per `R` |
| `cookies/` | Cookie di sessione salvati |

---

## ❓ FAQ

**Q: Devo pagare qualcosa?**
Lo script è MIT e gratuito. OnlineSim e Webshare sono a pagamento. CloakBrowser ha una build gratuita (v146 senza chiave, o free tier con login GitHub limitato a 1 sessione) e tier Pro opzionali.

**Q: Ho il CAPTCHA.**
Lo script non risolve reCAPTCHA: devi risolverlo tu manualmente nella finestra del browser.

**Q: È legale?**
Dipende dall'uso. Leggi `DISCLAIMER.md`. La creazione massiva di account quasi sempre viola i ToS di Libero/Virgilio.

**Q: Ho committato la API key per errore.**
Ruotala subito su onlinesim.io e rimuovila dalla cronologia con `git filter-repo` o BFG Repo-Cleaner.

---

## 📄 Licenza

Codice del progetto: **MIT** — vedi [LICENSE](LICENSE).
Binario CloakBrowser: licenza proprietaria CloakHQ — vedi [BINARY-LICENSE.md](https://github.com/CloakHQ/CloakBrowser/blob/main/BINARY-LICENSE.md).
