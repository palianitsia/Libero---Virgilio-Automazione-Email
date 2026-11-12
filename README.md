<h1>Libero / Virgilio — Creazione Automatizzata</h1>

<p>Creazione automatizzata delle email di Libero e Virgilio. Supporta <b>due metodi</b>:</p>

<ul>
  <li><b><code>browser</code></b> — navigazione tramite <b>CloakBrowser + Playwright</b> (metodo classico, v1.0)</li>
  <li><b><code>curl</code></b> — richieste HTTP dirette tramite <b>curl_cffi</b> + 2Captcha (nuovo in v1.1)</li>
</ul>

<p>OTP via <b>OnlineSim</b>, proxy <b>Webshare</b> opzionale, risoluzione captcha tramite <b>2Captcha</b> (in <code>curl</code> sempre, in <code>browser</code> opzionale).</p>

<blockquote>
  <p>⚠️ <b>Leggi <code>DISCLAIMER.md</code> prima di usare.</b> L'uso è a tuo rischio: la creazione automatizzata di account viola quasi certamente i Termini di Servizio di Libero/Virgilio.</p>
</blockquote>

<hr>

<h2>🆕 Novità v1.1</h2>

<table>
  <thead>
    <tr><th>Funzione</th><th>v1.0</th><th>v1.1</th></tr>
  </thead>
  <tbody>
    <tr><td>Metodo registrazione</td><td>solo browser</td><td><b>browser</b> oppure <b>curl</b></td></tr>
    <tr><td>Captcha v2 in browser</td><td>manuale</td><td><b>opzionale 2Captcha</b> (config)</td></tr>
    <tr><td>Captcha v2/v3 in curl</td><td>non previsto</td><td><b>2Captcha automatico</b></td></tr>
    <tr><td>Check username prima registrazione</td><td>no</td><td><b>sì</b> (scarta/suggerito/errore)</td></tr>
    <tr><td>Fallback numero (curl)</td><td>no</td><td><b>sì</b> (numero fisso o solo fallback)</td></tr>
    <tr><td>Config auto-aggiornata</td><td>no</td><td><b>sì</b> (chiavi nuove aggiunte in automatico)</td></tr>
  </tbody>
</table>

<p>Il file <code>Libero-Virglio Creazione Automatizzata v1.0.py</code> <b>resta nel repository</b> per chi vuole usare la versione precedente.</p>

<hr>

<h2>📋 Requisiti</h2>

<ul>
  <li>Python 3.9+</li>
  <li>Account OnlineSim con credito (per SMS)</li>
  <li>(Opzionale) Account Webshare per proxy</li>
  <li>(Opzionale) Account 2Captcha con credito — <b>obbligatorio</b> in <code>curl</code>, <b>opzionale</b> in <code>browser</code></li>
</ul>

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
PROVIDER = "libero"       # oppure virgilio

# Solo se METODO = curl, oppure se vuoi il captcha automatico in browser
2CAPTCHA_API_KEY = "la_tua_chiave_2captcha"
Risolvi captcha con 2captcha (browser) = Si</code></pre>
<p>Se usi <code>METODO = curl</code> e non hai 2Captcha, la registrazione si blocca al primo captcha: 2Captcha è obbligatorio in <code>curl</code>.</p>

<h3>5. Aggiungi account</h3>
<p>Copia <code>dati_account.example.txt</code> in <code>dati_account.txt</code> e inserisci le righe nel formato:</p>
<pre><code>USERNAME-PASSWORD-NOME-COGNOME-DD/MM/AAAA-M|F-COMUNE</code></pre>
<p>Usa <code>R</code> come comune per sceglierne uno casuale da <code>com_prov.json</code>.</p>
<p>Esempio:</p>
<pre><code>mariorossi92-Password123!-Mario-Rossi-12/03/1992-M-R</code></pre>

<h3>6. Avvia</h3>
<p><b>v1.1 (consigliata):</b></p>
<pre><code>python "Libero-Virglio Creazione Automatizzata v1.1._rev2"</code></pre>
<p><b>v1.0 (legacy):</b></p>
<pre><code>python "Libero-Virglio Creazione Automatizzata v1.0.py"</code></pre>

<hr>

<h2>🔄 Aggiornamento dalla v1.0 alla v1.1</h2>
<p>La v1.1 è <b>retrocompatibile</b>: puoi tenerla nella stessa cartella della v1.0 senza toccare i file esistenti.</p>
<ol>
  <li><b>Mantieni</b> <code>config.txt</code>, <code>dati_account.txt</code>, <code>account_creati.txt</code>, <code>com_prov.json</code> e la cartella <code>cookies/</code>. Non vengono sovrascritti.</li>
  <li><b>Aggiungi</b> il nuovo script <code>Libero-Virglio Creazione Automatizzata v1.1.1 recap brows.py</code> nella stessa cartella.</li>
  <li><b>Avvia</b> il nuovo script. Al primo avvio:
    <ul>
      <li>Se <code>config.txt</code> esiste già, <code>update_config_file()</code> aggiunge <b>in automatico</b> le nuove chiavi mancanti (<code>Risolvi captcha con 2captcha (browser)</code>, ecc.) <b>preservando i tuoi valori attuali</b> e i commenti di sezione.</li>
      <li>Se <code>config.txt</code> non esiste, viene creato da zero con tutti i default.</li>
    </ul>
  </li>
  <li><b>Controlla</b> <code>config.txt</code>: se vuoi il captcha automatico in browser, imposta:
    <pre><code>Risolvi captcha con 2captcha (browser) = Si</code></pre>
    Se lo lasci <code>No</code>, in browser il captcha va risolto manualmente come nella v1.0.
  </li>
  <li><b>Per passare a <code>curl</code></b>: imposta <code>METODO = curl</code> e assicurati che <code>2CAPTCHA_API_KEY</code> sia valorizzata. Il resto dei file resta identico.</li>
</ol>
<p>Nessuna migrazione manuale dei file dati. La v1.0 continua a funzionare in parallelo se vuoi tenerla come fallback.</p>

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
<blockquote><p>Se usi solo <code>METODO = curl</code>, CloakBrowser non serve. Playwright serve comunque (per il cookie iubenda).</p></blockquote>

<hr>

<h2>⚙️ Come funziona (in breve)</h2>

<p><b>Metodo <code>browser</code></b> (v1.0 + v1.1):</p>
<ol>
  <li>Legge <code>config.txt</code> e <code>dati_account.txt</code>.</li>
  <li>Apre il browser (CloakBrowser) sulla pagina di registrazione.</li>
  <li>Compila i 3 step: credenziali → dati anagrafici → numero di telefono.</li>
  <li>Se compare il captcha v2 e <code>Risolvi captcha con 2captcha (browser) = Si</code>, lo risolve con 2Captcha; altrimenti attende l'intervento manuale.</li>
  <li>Richiede un numero a OnlineSim, attende l'SMS, inserisce il PIN.</li>
  <li>Salva i cookie in <code>cookies/USERNAME.json</code> (se attivo).</li>
  <li>Sposta gli account creati in <code>account_creati.txt</code>.</li>
</ol>

<p><b>Metodo <code>curl</code></b> (v1.1):</p>
<ol>
  <li>Legge <code>config.txt</code> e <code>dati_account.txt</code>.</li>
  <li>Apre una sessione <code>curl_cffi</code> con fingerprint Chrome.</li>
  <li>Recupera il cookie <code>iolcmp-exp</code> (iubenda) via Playwright headless.</li>
  <li>Pre-validazione reCAPTCHA v3 → se il server richiede il v2, lo risolve con 2Captcha.</li>
  <li>Check username opzionale (con <code>check_username.php</code>).</li>
  <li>Esegue <code>check1.php</code> → <code>check2.php</code> → <code>check3.php</code>.</li>
  <li>Richiede il numero a OnlineSim (o fallback), invia <code>challenge1_check.php</code>, attende l'SMS, invia <code>challenge2_check.php</code>.</li>
  <li>Salva i cookie in <code>cookies/USERNAME.json</code> (se attivo).</li>
  <li>Sposta gli account creati in <code>account_creati.txt</code>.</li>
</ol>

<hr>

<h2>🧩 File del progetto</h2>

<table>
  <thead><tr><th>File</th><th>Descrizione</th></tr></thead>
  <tbody>
    <tr><td><code>Libero-Virglio Creazione Automatizzata v1.1._rev2</code></td><td>Script principale v1.1 (browser + curl)</td></tr>
    <tr><td><code>Libero-Virglio Creazione Automatizzata v1.0.py</code></td><td>Script legacy v1.0 (solo browser)</td></tr>
    <tr><td><code>Login con cookie json per accesso istantaneo.py</code></td><td>Login rapido con i cookie salvati</td></tr>
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

<p><b>Q: Posso usare la v1.0 e la v1.1 insieme?</b> Sì. Stessa cartella, stesso <code>config.txt</code> (la v1.1 aggiunge le chiavi nuove preservando le tue), stessi <code>dati_account.txt</code> e <code>account_creati.txt</code>. Avvia lo script che preferisci.</p>

<p><b>Q: La v1.1 modifica i miei file?</b> Solo <code>config.txt</code>, e solo per aggiungere le chiavi nuove mancanti. I valori esistenti e le chiavi custom vengono preservati. <code>dati_account.txt</code> e <code>account_creati.txt</code> non vengono toccati se non per le righe degli account processati.</p>

<p><b>Q: Quale metodo scelgo?</b> <code>browser</code> è più semplice (nessuna chiave 2Captcha obbligatoria, CloakBrowser gestisce il fingerprint). <code>curl</code> è più veloce e leggero ma richiede 2Captcha e può essere bloccato più facilmente se il fingerprint non basta.</p>

<hr>

<h2>📄 Licenza</h2>
<p>Codice del progetto: <b>MIT</b> — vedi <code>LICENSE</code>. Binario CloakBrowser: licenza proprietaria CloakHQ — vedi <code>BINARY-LICENSE.md</code>.</p>
