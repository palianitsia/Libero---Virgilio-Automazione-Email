<h1>Libero / Virgilio / Tiscali — Creazione Automatizzata</h1>

<p>Creazione automatizzata delle email di <b>Libero</b>, <b>Virgilio</b> e <b>Tiscali</b>. Supporta <b>due metodi</b>:</p>

<ul>
  <li><b><code>browser</code></b> — navigazione tramite <b>CloakBrowser + Playwright</b> (metodo classico, v1.0)</li>
  <li><b><code>curl</code></b> — richieste HTTP dirette tramite <b>curl_cffi</b> + 2Captcha (nuovo in v1.1)</li>
</ul>

<p>OTP via <b>OnlineSim</b>, proxy <b>Webshare</b> opzionale, risoluzione captcha tramite <b>2Captcha</b> (in <code>curl</code> sempre, in <code>browser</code> opzionale).</p>

<blockquote>
  <p>⚠️ <b>Leggi <code>DISCLAIMER.md</code> prima di usare.</b> L'uso è a tuo rischio: la creazione automatizzata di account viola quasi certamente i Termini di Servizio dei provider.</p>
</blockquote>

<hr>

<h2>🆕 Novità v1.1 (Rev 4)</h2>

<p>La <b>Rev 4</b> introduce il controllo <code>USO_COOKIE_MANUALE</code>, che permette di scegliere tra due flussi di gestione cookie senza cambiare script:</p>

<ul>
  <li><b><code>USO_COOKIE_MANUALE = Si</code></b> → flusso classico (Rev 3): Playwright headless + <code>MANUAL_IOLCMP_VALUE</code> per il metodo <code>curl</code>, iniezione del cookie manuale per il metodo <code>browser</code>.</li>
  <li><b><code>USO_COOKIE_MANUALE = No</code></b> → flusso <b>no-cookie</b>: nessun Playwright, nessun <code>MANUAL_IOLCMP_VALUE</code>, solo <code>curl_cffi</code> puro. Utile quando il sito accetta la registrazione senza il consenso Iubenda esplicito.</li>
</ul>

<table>
  <thead>
    <tr><th>Funzione</th><th>v1.0</th><th>v1.1 (Base)</th><th>v1.1 (Rev 3)</th><th>v1.1 (Rev 4)</th></tr>
  </thead>
  <tbody>
    <tr><td>Provider supportati</td><td>Libero, Virgilio</td><td>Libero, Virgilio</td><td>Libero, Virgilio, Tiscali</td><td><b>Libero, Virgilio, Tiscali</b></td></tr>
    <tr><td>Metodo registrazione</td><td>solo browser</td><td><b>browser</b> oppure <b>curl</b></td><td>Invariato (Tiscali solo curl)</td><td>Invariato</td></tr>
    <tr><td>Captcha v2 in browser</td><td>manuale</td><td><b>opzionale 2Captcha</b></td><td>Invariato</td><td>Invariato</td></tr>
    <tr><td>Captcha v2/v3 in curl</td><td>non previsto</td><td><b>2Captcha automatico</b></td><td>Invariato</td><td>Invariato</td></tr>
    <tr><td>Check username</td><td>no</td><td><b>sì</b> (scarta/suggerito/errore)</td><td>Invariato</td><td>Invariato</td></tr>
    <tr><td>Fallback numero (curl)</td><td>no</td><td><b>sì</b> (numero fisso o solo fallback)</td><td>Invariato</td><td>Invariato</td></tr>
    <tr><td>Gestione Cookie Iubenda</td><td>Automatica</td><td>Playwright Headless</td><td><b>Manuale da config.txt</b> + Estensione Browser</td><td><b>Selezionabile: Manuale (Si) o No-Cookie (No)</b></td></tr>
  </tbody>
</table>

<h3>🍪 Gestione Cookie Selezionabile (Rev 4)</h3>
<p>A partire dalla <b>Rev 4</b> è possibile scegliere in <code>config.txt</code> come gestire il consenso Iubenda:</p>
<pre><code>USO_COOKIE_MANUALE = Si   # flusso classico (Playwright + MANUAL_IOLCMP_VALUE)
USO_COOKIE_MANUALE = No   # flusso no-cookie (curl puro, niente Playwright)</code></pre>
<ul>
  <li><b><code>Si</code></b>: comportamento identico alla Rev 3. Per <code>curl</code> viene avviato un browser headless che accetta il banner e inietta <code>MANUAL_IOLCMP_VALUE</code> nella sessione. Per <code>browser</code> il cookie manuale viene aggiunto al contesto.</li>
  <li><b><code>No</code></b>: nessun browser headless, nessun <code>MANUAL_IOLCMP_VALUE</code>. La sessione <code>curl_cffi</code> parte direttamente dalla pagina di registrazione. Se il server richiede il consenso, la registrazione può fallire: in quel caso torna a <code>Si</code>.</li>
</ul>

<h3>📧 Provider supportati (invariato dalla Rev 3)</h3>
<ul>
  <li><b>Libero</b> e <b>Virgilio</b>: metodo <code>browser</code> o <code>curl</code>.</li>
  <li><b>Tiscali</b>: solo metodo <code>curl</code>. La gestione dei cookie iniziali avviene automaticamente tramite browser headless all'avvio (indipendente da <code>USO_COOKIE_MANUALE</code>).</li>
  <li>Per Tiscali usa esclusivamente la <b>Provincia</b> (sigla di 2 lettere): <code>R</code> per una sigla casuale da <code>com_prov.json</code>, oppure specifica direttamente <code>RM</code>, <code>MI</code>, ecc.</li>
</ul>

<p>I file delle versioni precedenti (<code>v1.1._rev3.py</code>, <code>v1.1._rev3_bonus.py</code>, <code>v1.1._rev2.py</code>, <code>v1.0.py</code>) <b>restano nel repository</b> per chi vuole usare le versioni precedenti.</p>

<hr>

<h2>📋 Requisiti</h2>

<ul>
  <li>Python 3.9+</li>
  <li>Account OnlineSim con credito (per SMS)</li>
  <li>(Opzionale) Account Webshare per proxy</li>
  <li>(Opzionale) Account 2Captcha con credito — <b>obbligatorio</b> in <code>curl</code>, <b>opzionale</b> in <code>browser</code></li>
</ul>

<p><b>Nota per il metodo <code>curl</code>:</b> serve la libreria Python <code>curl_cffi</code>, che puoi installare con:</p>
<pre><code>pip install curl_cffi --upgrade</code></pre>
<p>Funziona su Linux, macOS e Windows senza configurazioni aggiuntive. Se usi solo <code>METODO = browser</code>, non è necessaria.</p>

<p><b>Nota Rev 4:</b> con <code>USO_COOKIE_MANUALE = No</code> non serve Playwright per il metodo <code>curl</code>. Lo script lo richiede solo con <code>USO_COOKIE_MANUALE = Si</code>.</p>

<hr>

<h2>🚀 Installazione</h2>

<h3>1. Installa Python</h3>
<p>Da <a href="https://www.python.org/downloads/">https://www.python.org/downloads/</a> — spunta <b>"Add Python to PATH"</b>.</p>

<h3>2. Scarica il progetto</h3>
<pre><code>git clone https://github.com/palianitsia/Libero---Virgilio-Automazione-Email.git
cd Libero---Virgilio-Automazione-Email</code></pre>
<p>Se non usi git: <b>Code → Download ZIP</b> e scompatta.</p>

<h3>3. Installa dipendenze</h3>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>4. Configura</h3>
<pre><code>copy config.example.txt config.txt    # Windows
cp config.example.txt config.txt      # Linux/macOS</code></pre>
<p>Apri <code>config.txt</code> e compila almeno:</p>
<pre><code>METODO = browser          # oppure curl
ONLINESIM_API_KEY = "la_tua_chiave"
PROVIDER = "libero"       # oppure virgilio, tiscali

# Rev 4: gestione cookie
USO_COOKIE_MANUALE = Si   # Si = Playwright + MANUAL_IOLCMP_VALUE, No = curl puro
MANUAL_IOLCMP_VALUE = "incolla_qui_il_tuo_cookie_iolcmp-exp"  # usato solo se USO_COOKIE_MANUALE = Si

# Solo se METODO = curl, oppure se vuoi il captcha automatico in browser
2CAPTCHA_API_KEY = "la_tua_chiave_2captcha"
Risolvi captcha con 2captcha (browser) = Si
</code></pre>

<h3>5. Aggiungi account</h3>
<p>Copia <code>dati_account.example.txt</code> in <code>dati_account.txt</code> e inserisci le righe nel formato:</p>
<pre><code>USERNAME-PASSWORD-NOME-COGNOME-DD/MM/AAAA-M|F-COMUNE</code></pre>
<p>Usa <code>R</code> come comune per sceglierne uno casuale da <code>com_prov.json</code>. Per Tiscali, il comune deve essere nel formato <code>Città (SIGLA)</code> oppure direttamente la sigla (<code>RM</code>, <code>MI</code>).</p>
<p>Esempio:</p>
<pre><code>mariorossi92-Password123!-Mario-Rossi-12/03/1992-M-R</code></pre>

<h3>6. Avvia</h3>
<p><b>v1.1 Rev 4 (Consigliata):</b></p>
<pre><code>python "Libero-Virglio-Tiscali-Creazione Automatizzata v1.1._rev4.py"</code></pre>

<p><b>v1.1 Rev 3 Bonus (Legacy - senza flag cookie):</b></p>
<pre><code>cd v1.1_rev3_bonus
python "Libero-Virglio Creazione Automatizzata v1.1._rev3_bonus.py"</code></pre>

<p><b>v1.1 Rev 3 Standard:</b></p>
<pre><code>python "Libero-Virglio Creazione Automatizzata v1.1._rev3.py"</code></pre>

<p><b>v1.1 Rev 2 (Legacy - Cookie Auto):</b></p>
<pre><code>python "Libero-Virglio Creazione Automatizzata v1.1._rev2.py"</code></pre>

<p><b>v1.0 (Legacy Browser):</b></p>
<pre><code>python "Libero-Virglio Creazione Automatizzata v1.0.py"</code></pre>

<hr>

<h2>🔄 Aggiornamento alla v1.1 Rev 4</h2>
<p>La Rev 4 unifica in un solo script tutte le funzionalità delle versioni precedenti, aggiungendo il flag <code>USO_COOKIE_MANUALE</code>.</p>
<ol>
  <li><b>Usa</b> lo script <code>Libero-Virglio-Tiscali-Creazione Automatizzata v1.1._rev4.py</code>.</li>
  <li><b>Configura</b> <code>PROVIDER</code> (<code>libero</code>, <code>virgilio</code>, <code>tiscali</code>).</li>
  <li><b>Scegli la modalità cookie</b>:
    <ul>
      <li><code>USO_COOKIE_MANUALE = Si</code> se hai un <code>iolcmp-exp</code> valido e vuoi il massimo della compatibilità.</li>
      <li><code>USO_COOKIE_MANUALE = No</code> se il sito accetta la registrazione senza consenso esplicito e vuoi evitare Playwright.</li>
    </ul>
  </li>
  <li><b>Avvia</b> lo script. Gestisce automaticamente Libero/Virgilio/Tiscali.</li>
</ol>
<p>Il <code>config.txt</code> viene aggiornato al primo avvio: le chiavi nuove (<code>USO_COOKIE_MANUALE</code>) vengono aggiunte, i valori esistenti e le chiavi custom preservati.</p>

<hr>

<h2>🔑 CloakBrowser — Come ottenere la licenza</h2>
<p>Necessario solo con <code>METODO = browser</code>. Lo script usa <b>CloakBrowser</b> per il browser. Si installa con <code>pip</code> ma il binario Chromium (scaricato al primo avvio) richiede una licenza.</p>

<h3>Installazione</h3>
<pre><code>pip install cloakbrowser</code></pre>
<p>Il binario viene scaricato automaticamente in <code>~/.cloakbrowser/</code> al primo utilizzo.</p>

<h3>Come ottenere la licenza</h3>
<p><b>Opzione A — Build gratuita v146 (nessuna chiave)</b> Non devi fare nulla. Se non configuri nulla, CloakBrowser usa la build v146 scaricata da GitHub Releases, <b>senza bisogno di chiave</b>.</p>
<p><b>Opzione B — Build recente gratuita (1 sessione)</b></p>
<ol>
  <li>Vai su <a href="https://cloakbrowser.dev/free">https://cloakbrowser.dev/free</a></li>
  <li>Fai login con GitHub</li>
  <li>Ottieni una chiave gratuita <code>cb_...</code></li>
  <li>Attivala in uno di questi modi:</li>
</ol>
<pre><code># Metodo 1: login da terminale
cloakbrowser login

# Metodo 2: variabile d'ambiente
export CLOAKBROWSER_LICENSE_KEY=cb_xxxxxxxx     # Linux/macOS
$env:CLOAKBROWSER_LICENSE_KEY="cb_xxxxxxxx"    # Windows PowerShell</code></pre>
<p>Questa modalità dà <b>1 sessione browser simultanea</b>.</p>
<p><b>Opzione C — Pro (a pagamento)</b> Sessioni multiple. Chiave da <a href="https://cloakbrowser.dev">https://cloakbrowser.dev</a>.</p>
<blockquote><p>Se usi solo <code>METODO = curl</code> con <code>USO_COOKIE_MANUALE = No</code>, CloakBrowser <b>e</b> Playwright non servono affatto.</p></blockquote>

<hr>

<h2>⚙️ Come funziona (in breve)</h2>

<p><b>Metodo <code>browser</code></b> (v1.0 + v1.1 Rev 4):</p>
<ol>
  <li>Legge <code>config.txt</code> e <code>dati_account.txt</code>.</li>
  <li>Apre il browser (CloakBrowser) sulla pagina di registrazione.</li>
  <li>Se <code>USO_COOKIE_MANUALE = Si</code>, inietta <code>iolcmp-exp</code> dal config.</li>
  <li>Compila i 3 step: credenziali → dati anagrafici → numero di telefono.</li>
  <li>Se compare il captcha v2 e <code>Risolvi captcha con 2captcha (browser) = Si</code>, lo risolve con 2Captcha; altrimenti attende l'intervento manuale.</li>
  <li>Richiede un numero a OnlineSim, attende l'SMS, inserisce il PIN.</li>
  <li>Salva i cookie in <code>cookies/USERNAME.json</code> (se attivo).</li>
  <li>Sposta gli account creati in <code>account_creati.txt</code>.</li>
</ol>

<p><b>Metodo <code>curl</code></b> (v1.1 Rev 4):</p>
<ol>
  <li>Legge <code>config.txt</code> e <code>dati_account.txt</code>.</li>
  <li>Apre una sessione <code>curl_cffi</code> con fingerprint Chrome.</li>
  <li>Se <code>USO_COOKIE_MANUALE = Si</code>: avvia Playwright headless per accettare il banner e inietta <code>MANUAL_IOLCMP_VALUE</code> come <code>iolcmp-exp</code>.<br>
      Se <code>USO_COOKIE_MANUALE = No</code>: nessun Playwright, nessun cookie manuale, flusso HTTP puro.</li>
  <li>Pre-validazione reCAPTCHA v3 → se il server richiede il v2, lo risolve con 2Captcha.</li>
  <li>Check username opzionale (con <code>check_username.php</code> per Libero/Virgilio).</li>
  <li>Esegue le chiamate API specifiche per il provider scelto (Libero/Virgilio/Tiscali).</li>
  <li>Richiede il numero a OnlineSim (o fallback), invia le challenge, attende l'SMS, verifica il PIN.</li>
  <li>Salva i cookie in <code>cookies/USERNAME.json</code> (se attivo).</li>
  <li>Sposta gli account creati in <code>account_creati.txt</code>.</li>
</ol>

<hr>

<h2>🧩 File del progetto</h2>

<table>
  <thead><tr><th>File/Cartella</th><th>Descrizione</th></tr></thead>
  <tbody>
    <tr><td><code>Libero-Virglio-Tiscali-Creazione Automatizzata v1.1._rev4.py</code></td><td><b>Nuovo!</b> Script unificato Rev 4 con flag <code>USO_COOKIE_MANUALE</code> (Libero/Virgilio/Tiscali)</td></tr>
    <tr><td><code>v1.1_rev3_bonus/</code></td><td>Cartella con script Rev 3 Bonus (supporto Tiscali, senza flag cookie)</td></tr>
    <tr><td><code>Libero-Virglio Creazione Automatizzata v1.1._rev3.py</code></td><td>Script v1.1 Rev 3 (Libero/Virgilio - Cookie Manuale)</td></tr>
    <tr><td><code>Libero-Virglio Creazione Automatizzata v1.1._rev2.py</code></td><td>Script v1.1 Rev 2 (Cookie Auto via Playwright)</td></tr>
    <tr><td><code>Libero-Virglio Creazione Automatizzata v1.0.py</code></td><td>Script legacy v1.0 (solo browser)</td></tr>
    <tr><td><code>Login con cookie json per accesso istantaneo.py</code></td><td>Login rapido con i cookie salvati</td></tr>
    <tr><td><code>Estensione Browser Cookie Extractor</code></td><td>Estensione per estrarre <code>iolcmp-exp</code> facilmente</td></tr>
    <tr><td><code>config.txt</code></td><td>Configurazione (creato/aggiornato al primo avvio)</td></tr>
    <tr><td><code>config.example.txt</code></td><td>Esempio di configurazione</td></tr>
    <tr><td><code>dati_account.txt</code></td><td>Account da creare (creato al primo avvio)</td></tr>
    <tr><td><code>dati_account.example.txt</code></td><td>Esempio formato account</td></tr>
    <tr><td><code>account_creati.txt</code></td><td>Account creati con successo (creato al primo avvio)</td></tr>
    <tr><td><code>com_prov.json</code></td><td>Lista comuni/province per <code>R</code></td></tr>
    <tr><td><code>password_vietati.txt</code></td><td>Password comuni scartate dal sito</td></tr>
    <tr><td><code>cookies/</code></td><td>Cookie di sessione salvati (creato al primo avvio)</td></tr>
  </tbody>
</table>

<hr>

<h2>❓ FAQ</h2>

<p><b>Q: Devo pagare qualcosa?</b> Lo script è MIT e gratuito. OnlineSim e Webshare sono a pagamento. CloakBrowser ha una build gratuita (v146 senza chiave, o free tier con login GitHub limitato a 1 sessione) e tier Pro opzionali. 2Captcha è a pagamento (necessario solo per <code>curl</code> o per il captcha automatico in <code>browser</code>).</p>

<p><b>Q: Ho il CAPTCHA in <code>browser</code>.</b> Con <code>Risolvi captcha con 2captcha (browser) = Si</code> e <code>2CAPTCHA_API_KEY</code> valida, lo script lo risolve da solo. Con <code>No</code>, devi risolverlo tu manualmente nella finestra del browser (come nella v1.0).</p>

<p><b>Q: Ho il CAPTCHA in <code>curl</code>.</b> In <code>curl</code> 2Captcha è obbligatorio: lo script risolve v3 (pre-validazione) e v2 (se richiesto) automaticamente. Senza <code>2CAPTCHA_API_KEY</code> la registrazione si blocca.</p>

<p><b>Q: Come ottengo il cookie <code>iolcmp-exp</code>?</b> Usa l'<b>estensione browser</b> inclusa nel repository. Visita libero.it o virgilio.it, accetta i cookie se richiesto, e clicca sull'icona dell'estensione per copiare il valore. Incollalo in <code>MANUAL_IOLCMP_VALUE</code> in <code>config.txt</code> (necessario solo con <code>USO_COOKIE_MANUALE = Si</code>).</p>

<p><b>Q: Posso fare a meno del cookie manuale?</b> Sì, dalla Rev 4: imposta <code>USO_COOKIE_MANUALE = No</code>. La registrazione via <code>curl</code> partirà senza Playwright e senza <code>iolcmp-exp</code>. Se il server rifiuta per consenso mancante, torna a <code>Si</code> e fornisci il cookie.</p>

<p><b>Q: Posso usare le versioni precedenti insieme alla Rev 4?</b> Sì. Stessa cartella, stesso <code>config.txt</code> (la Rev 4 aggiunge le chiavi nuove preservando le tue), stessi <code>dati_account.txt</code> e <code>account_creati.txt</code>. Avvia lo script che preferisci.</p>

<p><b>Q: La Rev 4 modifica i miei file?</b> Solo <code>config.txt</code>, e solo per aggiungere le chiavi nuove mancanti (<code>USO_COOKIE_MANUALE</code>). I valori esistenti e le chiavi custom vengono preservati. <code>dati_account.txt</code> e <code>account_creati.txt</code> non vengono toccati se non per le righe degli account processati.</p>

<p><b>Q: Quale metodo scelgo?</b> <code>browser</code> è più semplice (nessuna chiave 2Captcha obbligatoria, CloakBrowser gestisce il fingerprint). <code>curl</code> è più veloce e leggero ma richiede 2Captcha e può essere bloccato più facilmente se il fingerprint non basta. Con <code>USO_COOKIE_MANUALE = No</code> il metodo <code>curl</code> è il più leggero in assoluto (nessun browser headless).</p>

<p><b>Q: Come registro su Tiscali?</b> Con la Rev 4 basta impostare <code>PROVIDER = "tiscali"</code> e <code>METODO = curl</code>. La gestione dei cookie Tiscali è automatica (Playwright headless) e indipendente da <code>USO_COOKIE_MANUALE</code>. Assicurati che il comune nel file accounts sia nel formato <code>Città (SIGLA)</code> o direttamente la sigla.</p>

<hr>

<h2>📄 Licenza</h2>
<p>Codice del progetto: <b>MIT</b> — vedi <code>LICENSE</code>. Binario CloakBrowser: licenza proprietaria CloakHQ — vedi <code>BINARY-LICENSE.md</code>.</p>
