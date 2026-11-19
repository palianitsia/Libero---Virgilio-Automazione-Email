import json
import os
import random
import re
import time
import logging
from datetime import datetime
from pathlib import Path

import requests
import cloakbrowser
from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)

SCRIPT_DIR      = Path(__file__).resolve().parent
CONFIG_FILE     = SCRIPT_DIR / "config.txt"
ACCOUNTS_FILE   = SCRIPT_DIR / "dati_account.txt"
CREATED_FILE    = SCRIPT_DIR / "account_creati.txt"
PREFS_FILE      = SCRIPT_DIR / "preferenze.txt"
COMUNI_FILE     = SCRIPT_DIR / "com_prov.json"

class ColorFormatter(logging.Formatter):
    COLORS = {
        logging.DEBUG:    Fore.CYAN,
        logging.INFO:     Fore.WHITE,
        logging.WARNING:  Fore.YELLOW + Style.BRIGHT,
        logging.ERROR:    Fore.RED + Style.BRIGHT,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + Style.BRIGHT,
    }
    def format(self, record):
        c = self.COLORS.get(record.levelno, Fore.WHITE)
        return f"{c}{super().format(record)}{RESET}"

_handler = logging.StreamHandler()
_handler.setFormatter(ColorFormatter("%(asctime)s %(levelname)s %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[_handler])

LOGO_GREEN = Fore.GREEN + Style.BRIGHT
LOGO_BLUE  = Fore.BLUE  + Style.BRIGHT
RESET      = Style.RESET_ALL

LOGO = r"""
@@@       @@@  @@@@@@@   @@@@@@@@  @@@@@@@    @@@@@@
@@@       @@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@
@@!       @@!  @@!  @@@  @@!       @@!  @@@  @@!  @@@
!@!       !@!  !@   @!@  !@!       !@!  @!@  !@!  @!@
@!!       !!@  @!@!@!@   @!!!:!    @!@!!@!   @!@  !@!  @!@!@!@!@
!!!       !!!  !!!@!!!!  !!!!!:    !!@!@!    !@!  !!!  !!!@!@!!!
!!:       !!:  !!:  !!!  !!:       !!: :!!   !!:  !!!
 :!:      :!:  :!:  !:!  :!:       :!:  !:!  :!:  !:!
 :: ::::   ::   :: ::::   :: ::::  ::   :::  ::::: ::
: :: : :  :    :: : ::   : :: ::    :   : :   : :  :


@@@  @@@  @@@  @@@@@@@    @@@@@@@@  @@@  @@@       @@@   @@@@@@
@@@  @@@  @@@  @@@@@@@@  @@@@@@@@@  @@@  @@@       @@@  @@@@@@@@
@@!  @@@  @@!  @@!  @@@  !@@        @@!  @@!       @@!  @@!  @@@
!@!  @!@  !@!  !@!  @!@  !@!        !@!  !@!       !@!  !@!  @!@
@!@  !@!  !!@  @!@!!@!   !@! @!@!@  !!@  @!!       !!@  @!@  !@!
!@!  !!!  !!!  !!@!@!    !!! !!@!!  !!!  !!!       !!!  !@!  !!!
:!:  !!:  !!:  !!: :!!   :!!   !!:  !!:  !!:       !!:  !!:  !!!
 ::!!:!   :!:  :!:  !:!  :!:   !::  :!:   :!:      :!:  :!:  !:!
  ::::     ::  ::   :::   ::: ::::   ::   :: ::::   ::  ::::: ::
   :      :     :   : :   :: :: :   :    : :: : :  :     : :  :


@@@  @@@    @@@        @@@@@@@@
@@@  @@@   @@@@       @@@@@@@@@@
@@!  @@@  @@@!!       @@!   @@@@
!@!  @!@    !@!       !@!  @!@!@
@!@  !@!    @!@       @!@ @! !@!
!@!  !!!    !@!       @!@!!  !!!
:!:  !!:    !!:       !!:!   !!!
 ::!!:!     :!:  :!:  :!:    !:!
  ::::      :::  :::  ::::::: ::
   :         ::  :::   : : :  :


                             ██████  ██    ██
                             ██   ██  ██  ██
                             ██████    ████
                             ██   ██    ██
                             ██████     ██


██████   █████  ██      ██  █████  ███    ██ ██ ████████ ███████ ██  █████
██   ██ ██   ██ ██      ██ ██   ██ ████   ██ ██    ██    ██      ██ ██   ██
██████  ███████ ██      ██ ███████ ██ ██  ██ ██    ██    ███████ ██ ███████
██      ██   ██ ██      ██ ██   ██ ██  ██ ██ ██    ██         ██ ██ ██   ██
██      ██   ██ ███████ ██ ██   ██ ██   ████ ██    ██    ███████ ██ ██   ██
"""

SIGNATURE = "by Palianitsia"

def print_logo():
    print(LOGO_GREEN + LOGO + RESET)
    print(LOGO_BLUE + f"{SIGNATURE:^80}" + RESET)
    print()
    
def log(msg):
    ts = f"{datetime.now():%H:%M:%S}"

    if msg.startswith("[***]"):
        color = Fore.GREEN + Style.BRIGHT
    elif msg.startswith("[+]"):
        color = Fore.GREEN
    elif msg.startswith("[i]"):
        color = Fore.CYAN
    elif msg.startswith("[!]"):
        color = Fore.YELLOW + Style.BRIGHT
    elif msg.startswith("[-]"):
        color = Fore.RED + Style.BRIGHT
    elif msg.startswith("[?]"):
        color = Fore.MAGENTA
    elif msg.startswith("###"):
        color = Fore.WHITE + Style.BRIGHT
    elif msg.startswith("==="):
        color = Fore.WHITE + Style.DIM
    else:
        color = Fore.WHITE

    print(f"{Fore.BLACK + Style.BRIGHT}[{ts}]{RESET} {color}{msg}{RESET}")    

DEFAULT_CONFIG = """# ============================================================
# CONFIGURAZIONE
# ============================================================
ONLINESIM_API_KEY = "INCOLLA_QUI_LA_TUA_CHIAVE_API"
ONLINESIM_SERVICE = "libero"
ONLINESIM_COUNTRY_IT = "39"
ONLINESIM_BASE_URL = "https://onlinesim.io/api"

# Provider registrazione: "libero" oppure "virgilio"
PROVIDER = "libero"

# Timeout attesa SMS (secondi)
SMS_TIMEOUT = 60

# Tentativi con numeri diversi se OTP non arriva
MAX_ATTEMPTS = 3

# Pausa tra un account e il successivo (secondi)
PAUSA_TRA_ACCOUNT = 30

# Browser
HEADLESS = false
HUMANIZE = true
HUMAN_PRESET = "careful"
ALLOW_3P_COOKIES = true
TRANSPARENT_PROXY = false

# Salvataggio cookie di accesso
Salvare cookie di accesso = Si
Cartella cookie = cookies

# ============================================================
# PROXY WEBSHARE
# ============================================================
# Attiva l'uso del proxy (Si / No). Se No, i parametri sotto vengono ignorati.
Uso_proxy = No

# URL API Webshare per scaricare la lista proxy.
# Formato atteso: una riga per proxy -> ip:porta:username:password
WEBSHARE_API_URL = ""

# Tempo di cache della lista proxy (secondi). Default 3600 = 1 ora.
WEBSHARE_CACHE_TIME = 3600
"""

DEFAULT_ACCOUNTS = """# Compila dati in formato
# USERNAME-PASSWORD-FIRSTNAME-LASTNAME-DOB-GENDER-COMUNE
# oppure USERNAME-PASSWORD-FIRSTNAME-LASTNAME-DOB-GENDER-R
# (R = COMUNE casuale da com_prov.json)
# Ogni riga rappresenta un account.
# Le righe con successo vengono spostate in account_creati.txt.
#
# Esempi:
# emaildicasper333-superpassword534-Mario-Biondo-01/01/1959-M-R
# emaildicasper333-superpassword534-Mario-Biondo-01/01/1959-M-Alessandria del Carretto (CS)
"""

DEFAULT_CREATED = """# Account creati con successo
# Formato: DATA | PROVIDER | USERNAME | PASSWORD | NOME COGNOME | DOB | GENDER | COMUNE
"""


def ensure_default_files():
    if not CONFIG_FILE.exists():
        CONFIG_FILE.write_text(DEFAULT_CONFIG, encoding="utf-8")
        log(f"[+] Creato {CONFIG_FILE.name}")
    if not ACCOUNTS_FILE.exists():
        ACCOUNTS_FILE.write_text(DEFAULT_ACCOUNTS, encoding="utf-8")
        log(f"[+] Creato {ACCOUNTS_FILE.name}")
    if not CREATED_FILE.exists():
        CREATED_FILE.write_text(DEFAULT_CREATED, encoding="utf-8")
        log(f"[+] Creato {CREATED_FILE.name}")

def parse_config():
    cfg = {}
    text = CONFIG_FILE.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if v.lower() in ("true", "si", "sì", "yes", "1"):
            v = True
        elif v.lower() in ("false", "no", "0"):
            v = False
        elif re.fullmatch(r"-?\d+", v):
            v = int(v)
        cfg[k] = v
    return cfg

def load_comuni():
    if COMUNI_FILE.exists():
        try:
            data = json.loads(COMUNI_FILE.read_text(encoding="utf-8"))
            if isinstance(data, list) and data:
                return data
        except Exception as e:
            log(f"[!] com_prov.json non valido: {e}")
    log("[!] com_prov.json mancante o vuoto: uso fallback")
    return ["Roma (RM)", "Milano (MI)", "Napoli (NA)", "Torino (TO)", "Palermo (PA)"]

def load_accounts():
    accounts = []
    raw_lines = ACCOUNTS_FILE.read_text(encoding="utf-8").splitlines()
    for idx, raw in enumerate(raw_lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("-", 6)
        if len(parts) < 7:
            log(f"[!] Riga {idx} non valida (attesi 7 campi): {line}")
            continue
        username, password, firstname, lastname, dob, gender, comune = parts
        accounts.append({
            "_line": raw,
            "username": username.strip(),
            "password": password.strip(),
            "firstname": firstname.strip(),
            "lastname": lastname.strip(),
            "dob": dob.strip(),
            "gender": gender.strip().upper(),
            "comune": comune.strip(),
        })
    return accounts

def remove_account_line(account):
    try:
        lines = ACCOUNTS_FILE.read_text(encoding="utf-8").splitlines(keepends=True)
        target = account.get("_line", "").strip()
        for i, ln in enumerate(lines):
            if ln.strip() == target:
                del lines[i]
                break
        ACCOUNTS_FILE.write_text("".join(lines), encoding="utf-8")
        log(f"[i] Riga rimossa da {ACCOUNTS_FILE.name}: {account['username']}")
    except Exception as e:
        log(f"[!] Errore rimozione riga: {e}")

def append_created_account(account, comune_finale, provider):
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = (f"{ts} | {provider} | {account['username']} | {account['password']} | "
                f"{account['firstname']} {account['lastname']} | "
                f"{account['dob']} | {account['gender']} | {comune_finale}\n")
        with CREATED_FILE.open("a", encoding="utf-8") as f:
            f.write(line)
        log(f"[+] Account aggiunto a {CREATED_FILE.name} (provider: {provider})")
    except Exception as e:
        log(f"[!] Errore scrittura account_creati.txt: {e}")

PROVIDERS = {
    "libero": {
        "reg_base": "https://registrazione.libero.it",
        "mail_host": "mail1.libero.it",
        "domain": "libero.it",
    },
    "virgilio": {
        "reg_base": "https://registrazione.virgilio.it",
        "mail_host": "mail1.virgilio.it",
        "domain": "virgilio.it",
    },
}

def build_urls(provider):
    p = PROVIDERS[provider]
    reg_url = (
        f"{p['reg_base']}/?service_id=webmail"
        f"&redirect_uri=https%3A%2F%2F{p['mail_host']}%2Fappsuite%2Fapi%2Flogin"
        "%3Faction%3DliberoLogin&ref=lg"
    )
    return p["reg_base"], p["mail_host"], reg_url

def onlinesim_get_number(cfg, max_retries=3):
    params = {
        "apikey": cfg["ONLINESIM_API_KEY"],
        "service": cfg["ONLINESIM_SERVICE"],
        "country": cfg["ONLINESIM_COUNTRY_IT"],
        "number": "true",
    }
    for attempt in range(1, max_retries + 1):
        try:
            log(f"OnlineSim getNum ({attempt}/{max_retries})...")
            r = requests.get(f"{cfg['ONLINESIM_BASE_URL']}/getNum.php",
                             params=params, timeout=40)
            if r.status_code != 200:
                time.sleep(5); continue
            data = r.json()
            if isinstance(data, dict) and str(data.get("response", "")) == "1":
                tzid = data.get("tzid")
                number = data.get("number")
                if tzid and number:
                    if number.startswith("+39"): number = number[3:]
                    elif number.startswith("39"): number = number[2:]
                    log(f"Numero OnlineSim: {number} (tzid: {tzid})")
                    return tzid, number
            else:
                err = data.get("response_text") or data.get("msg") or "unknown"
                log(f"OnlineSim errore: {err}")
                if "NO_NUMBERS" in str(err).upper(): time.sleep(30)
                elif "NO_BALANCE" in str(err).upper(): return None, None
                else: time.sleep(5)
        except Exception as e:
            log(f"Eccezione getNum: {e}"); time.sleep(5)
    return None, None

def onlinesim_get_sms(cfg, tzid, timeout=None):
    timeout = timeout or cfg.get("SMS_TIMEOUT", 60)
    start = time.time()
    log(f"Attendo SMS OnlineSim (tzid={tzid}, timeout={timeout}s)...")
    while time.time() - start < timeout:
        try:
            params = {
                "apikey": cfg["ONLINESIM_API_KEY"],
                "tzid": tzid,
                "message_to_code": "0",
                "msg_list": "1",
                "clean": "1",
                "lang": "en",
            }
            r = requests.get(f"{cfg['ONLINESIM_BASE_URL']}/getState.php",
                             params=params, timeout=20)
            if r.status_code != 200: time.sleep(5); continue
            data = r.json()
            messages = []
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict) and "msg" in item:
                        m = item["msg"]
                        messages.extend(m if isinstance(m, list) else [m])
            elif isinstance(data, dict) and "msg" in data:
                m = data["msg"]
                messages.extend(m if isinstance(m, list) else [m])
            for msg in messages:
                if isinstance(msg, str) and msg.strip(): return msg
                if isinstance(msg, dict):
                    txt = msg.get("msg") or msg.get("text") or msg.get("message")
                    if txt: return txt
        except Exception as e:
            log(f"Errore getState: {e}")
        time.sleep(5)
    log("Timeout SMS")
    return None

def onlinesim_close_operation(cfg, tzid):
    try:
        requests.get(f"{cfg['ONLINESIM_BASE_URL']}/getState.php",
                     params={"apikey": cfg["ONLINESIM_API_KEY"], "tzid": tzid, "close": "1"},
                     timeout=15)
    except Exception:
        pass

def extract_pin_from_sms(sms_text):
    if not sms_text: return None
    text = sms_text.strip()
    idx = text.rfind(": ")
    if idx != -1:
        cand = text[idx + 2:].strip().rstrip(" .,;!?")
        if cand:
            first = cand.split()[0]
            if re.fullmatch(r"[A-Za-z0-9]{4,10}", first):
                return first
    blacklist = {"codice", "verifica", "account", "libero", "mail", "virgilio"}
    for m in re.finditer(r"\b([A-Za-z0-9]{4,10})\b", text):
        tok = m.group(1)
        if tok.lower() in blacklist: continue
        if re.fullmatch(r"[a-z]{4,10}", tok) or re.fullmatch(r"[A-Za-z0-9]{4,10}", tok):
            return tok
    m = re.search(r"\b(\d{4,8})\b", text)
    return m.group(1) if m else None

WEBSHARE_API_URL = ""
WEBSHARE_CACHE_TIME = 3600
WEBSHARE_PROXIES = []
WEBSHARE_LAST_FETCH = None


def fetch_webshare_proxies():
    global WEBSHARE_PROXIES, WEBSHARE_LAST_FETCH
    if (WEBSHARE_LAST_FETCH
            and (datetime.now() - WEBSHARE_LAST_FETCH).total_seconds() < WEBSHARE_CACHE_TIME
            and WEBSHARE_PROXIES):
        logging.info(f"Cache proxy valida: {len(WEBSHARE_PROXIES)}")
        return True
    try:
        r = requests.get(WEBSHARE_API_URL, timeout=30)
        if r.status_code != 200:
            logging.error(f"Errore fetch proxy: {r.status_code}")
            return False
        proxies = []
        for line in r.text.split("\n"):
            line = line.strip()
            if not line:
                continue
            parts = line.split(":")
            if len(parts) >= 4:
                ip, porta, user, pwd = parts[0], parts[1], parts[2], parts[3]
                proxies.append({
                    "server": f"http://{ip}:{porta}",
                    "username": user,
                    "password": pwd,
                })
        WEBSHARE_PROXIES = proxies
        WEBSHARE_LAST_FETCH = datetime.now()
        logging.info(f"Caricati {len(WEBSHARE_PROXIES)} proxy")
        return True
    except Exception as e:
        logging.error(f"Eccezione fetch proxy: {e}")
        return False


def pick_proxy():
    return random.choice(WEBSHARE_PROXIES) if WEBSHARE_PROXIES else None

def accept_cookies_if_present(page, timeout_ms=8000):
    for sel in ["button.iubenda-cs-accept-btn",
                "button.ubl-cst__btn--accept",
                "text=Accetta e Chiudi"]:
        try:
            btn = page.wait_for_selector(sel, timeout=timeout_ms, state="visible")
            if btn:
                btn.click()
                log(f"[+] Cookie accettati ({sel})")
                try:
                    page.wait_for_selector("button.iubenda-cs-accept-btn",
                                           state="detached", timeout=5000)
                except Exception:
                    pass
                return True
        except Exception:
            continue
    log("[i] Banner cookie non presente.")
    return False

def force_fill(page, selector, value):
    try:
        page.evaluate(
            "(sel) => { const el=document.querySelector(sel); if(el) el.removeAttribute('readonly'); }",
            selector,
        )
    except Exception:
        pass
    try:
        page.fill(selector, value, timeout=5000)
    except Exception:
        try:
            page.fill(selector, value, force=True, timeout=5000)
        except Exception:
            page.evaluate(
                """([sel,v]) => {
                    const el = document.querySelector(sel);
                    el.removeAttribute('readonly');
                    el.value = v;
                    el.dispatchEvent(new Event('input', {bubbles:true}));
                    el.dispatchEvent(new Event('change', {bubbles:true}));
                    el.dispatchEvent(new Event('keyup', {bubbles:true}));
                }""",
                [selector, value],
            )
    for ev in ("input", "change", "keyup"):
        try: page.dispatch_event(selector, ev)
        except Exception: pass

def fill_date_of_birth(page, selector, value):
    page.evaluate(
        """([sel, v]) => {
            const el = document.querySelector(sel);
            if (!el) return;
            el.removeAttribute('readonly');
            el.focus();
            el.value = v;
            el.dispatchEvent(new Event('input', {bubbles:true}));
            el.dispatchEvent(new Event('change', {bubbles:true}));
            el.dispatchEvent(new Event('keyup', {bubbles:true}));
            el.dispatchEvent(new Event('blur', {bubbles:true}));
        }""",
        [selector, value],
    )
    time.sleep(0.3)
    current = page.evaluate(
        "(sel) => { const el=document.querySelector(sel); return el ? el.value : ''; }",
        selector,
    )
    log(f"[i] dateofbirth = '{current}' (atteso '{value}')")
    if current != value:
        page.evaluate(
            """([sel, v]) => {
                const el = document.querySelector(sel);
                el.value = v;
                el.dispatchEvent(new Event('change', {bubbles:true}));
                el.dispatchEvent(new Event('blur', {bubbles:true}));
            }""",
            [selector, value],
        )
        time.sleep(0.3)
        log("[i] dateofbirth corretto")

def set_radio(page, selector):
    try:
        page.check(selector, timeout=5000)
    except Exception:
        page.evaluate(
            "(sel) => { const el=document.querySelector(sel); if(el){el.checked=true;"
            "el.dispatchEvent(new Event('change',{bubbles:true}));"
            "el.dispatchEvent(new Event('click',{bubbles:true}));} }",
            selector,
        )

def auto_click_or_wait_captcha(page, timeout_s=300, captcha_grace_s=8):
    start = time.time()
    captcha_seen = False
    clicked = False
    sels = ["iframe[src*='recaptcha']", "iframe[title*='recaptcha']",
            "div.g-recaptcha", "#recaptcha", ".g-recaptcha",
            "#captcha", ".captcha"]
    while time.time() - start < timeout_s:
        if "join2.phtml" in page.url:
            return True
        captcha = False
        for s in sels:
            try:
                el = page.query_selector(s)
                if el and el.is_visible():
                    captcha = True; break
            except Exception:
                pass
        if captcha:
            if not captcha_seen:
                log("[!] CAPTCHA visibile: risolvilo tu, poi clicca Avanti.")
                captcha_seen = True
            time.sleep(1.0); continue
        if not clicked and (time.time() - start) >= captcha_grace_s:
            log("[+] Nessun CAPTCHA: clicco Avanti.")
            try:
                page.click("#button_submit", timeout=10000)
                clicked = True
            except Exception:
                try:
                    page.evaluate("document.querySelector('form')?.submit()")
                    clicked = True
                except Exception:
                    pass
        time.sleep(1.0)
    return False

def go_back_to_phone_page(page):
    log("Clicco la X per tornare alla pagina del numero...")
    for sel in ["#button_back", "button[name='button_back']",
                "button.close", "button[aria-label='Close']"]:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click(); log(f"[+] Click su '{sel}'"); break
        except Exception:
            continue
    else:
        log("[-] Pulsante chiusura non trovato."); return False
    try:
        page.wait_for_selector("[name='cellulare_challenge']", timeout=30000)
        return True
    except Exception:
        log(f"[-] cellulare_challenge non riapparsa. URL: {page.url}")
        return False

def finalize_after_pin(page):
    try:
        page.wait_for_selector("button[data-action='close'], button[data-action='done']",
                               timeout=60000)
    except Exception:
        log("[i] Pulsanti Annulla/Fine non comparsi subito.")
    log("Clicco 'Annulla'...")
    try:
        btn = page.query_selector("button[data-action='close']")
        if btn: btn.click(); log("[+] 'Annulla' cliccato")
    except Exception as e:
        log(f"[!] Errore click Annulla: {e}")
    time.sleep(3)
    log("Clicco 'Fine'...")
    try:
        btn = page.query_selector("button[data-action='done']")
        if btn: btn.click(); log("[+] 'Fine' cliccato")
    except Exception as e:
        log(f"[!] Errore click Fine: {e}")

def save_auth_json(context, page, username, cookie_dir):
    try:
        cookie_dir.mkdir(parents=True, exist_ok=True)
        cookies = context.cookies()
        origins = []
        try:
            origins = page.evaluate(
                """() => {
                    const o = [];
                    try {
                        const ls = window.localStorage;
                        if (ls && ls.length >= 0) {
                            const items = [];
                            for (let i = 0; i < ls.length; i++) {
                                const k = ls.key(i);
                                items.push({name: k, value: ls.getItem(k)});
                            }
                            o.push({origin: location.origin, localStorage: items});
                        }
                    } catch (e) {}
                    return o;
                }"""
            )
        except Exception:
            origins = []
        out = {"cookies": cookies, "origins": origins}
        path = cookie_dir / f"{username}.json"
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"[+] Cookie salvati in {path}")
    except Exception as e:
        log(f"[!] Errore salvataggio cookie: {e}")

def run_account(cfg, acc, comuni, save_cookies, cookie_dir):
    username = acc["username"]
    password = acc["password"]
    firstname = acc["firstname"]
    lastname = acc["lastname"]
    dob = acc["dob"]
    gender = acc["gender"]
    comune = acc["comune"]

    provider = str(cfg.get("PROVIDER", "libero")).lower()
    if provider not in PROVIDERS:
        log(f"[-] PROVIDER sconosciuto: {provider}, uso libero")
        provider = "libero"
    reg_base, mail_host, reg_url = build_urls(provider)

    if comune.strip().upper() == "R":
        comune = random.choice(comuni)
        log(f"[i] Comune casuale scelto: {comune}")

    log("=" * 60)
    log(f"Provider: {provider} | {reg_base} -> {mail_host}")
    log(f"Account: {username} | {firstname} {lastname} | {dob} | {gender} | {comune}")
    log("=" * 60)

    args = []
    if cfg.get("ALLOW_3P_COOKIES", True):
        args.append("--fingerprint-allow-3p-cookies")
    if cfg.get("TRANSPARENT_PROXY", False):
        args.append("--fingerprint-transparent-proxy")
    launch_kwargs = {
        "headless": bool(cfg.get("HEADLESS", False)),
        "humanize": bool(cfg.get("HUMANIZE", True)),
        "human_preset": cfg.get("HUMAN_PRESET", "careful"),
    }
    if args:
        launch_kwargs["args"] = args

    if cfg.get("Uso_proxy", False):
        proxy_cfg = pick_proxy()
        if proxy_cfg:
            server = proxy_cfg["server"].replace("http://", "")
            proxy_url = f"http://{proxy_cfg['username']}:{proxy_cfg['password']}@{server}"
            launch_kwargs["proxy"] = proxy_url
            launch_kwargs["geoip"] = True
            log(f"[i] Proxy Webshare: {proxy_cfg['server']} (user={proxy_cfg['username']})")
            # Assicura che --fingerprint-allow-3p-cookies sia presente
            existing_args = launch_kwargs.get("args", [])
            if "--fingerprint-allow-3p-cookies" not in existing_args:
                existing_args.append("--fingerprint-allow-3p-cookies")
            launch_kwargs["args"] = existing_args
        else:
            log("[!] Nessun proxy disponibile, proseguo senza.")

    browser = cloakbrowser.launch(**launch_kwargs)

    context = browser.new_context(
        locale="it-IT",
        viewport={"width": 1600, "height": 800},
    )
    page = context.new_page()

    try:
        page.goto(reg_url, wait_until="domcontentloaded", timeout=60000)
        accept_cookies_if_present(page)
        force_fill(page, "#username", username)
        force_fill(page, "#password", password)

        log("=" * 55)
        log("Attendo: se c'è CAPTCHA lo risolvi tu; altrimenti clicco Avanti.")
        log("=" * 55)
        if not auto_click_or_wait_captcha(page, timeout_s=300, captcha_grace_s=8):
            log(f"[-] join2.phtml non raggiunto. URL: {page.url}")
            return False

        force_fill(page, "#firstname", firstname)
        force_fill(page, "#lastname", lastname)
        fill_date_of_birth(page, "#dateofbirth", dob)
        set_radio(page, "#male" if gender == "M" else "#female")

        log(f"Comune: {comune}")
        force_fill(page, "#comune_provincia", comune)
        try:
            page.wait_for_selector(".mdb-autocomplete-wrap li, .autocomplete-items div",
                                   timeout=5000)
            clicked = page.evaluate(
                """(comune) => {
                    const sels = ['.mdb-autocomplete-wrap li', '.autocomplete-items div',
                                  '.dropdown-content li'];
                    for (const s of sels) {
                        const items = document.querySelectorAll(s);
                        for (const it of items) {
                            if (it.textContent.trim().toLowerCase() === comune.toLowerCase()) {
                                it.click(); return true;
                            }
                        }
                    }
                    for (const s of sels) {
                        const it = document.querySelector(s);
                        if (it) { it.click(); return true; }
                    }
                    return false;
                }""", comune,
            )
            log(f"[+] Comune selezionato: {clicked}")
        except Exception:
            log("[!] Nessun dropdown per il comune")

        try:
            page.click("#button_submit", timeout=10000)
        except Exception:
            page.evaluate("document.querySelector('form')?.submit()")

        try:
            page.wait_for_url("**/join3.phtml", timeout=60000)
            log("[+] Arrivato a join3.phtml")
        except Exception:
            log(f"[-] join3.phtml non raggiunto. URL: {page.url}")
            return False

        tzid, number = onlinesim_get_number(cfg)
        if not number:
            log("[-] OnlineSim non ha dato numero.")
            return False
        log(f"[+] Numero: {number} (tzid: {tzid})")
        force_fill(page, "#emailsecondaria", number)
        set_radio(page, "#privacy_S")
        set_radio(page, "#extprivacy_S")
        try:
            page.click("#button_submit", timeout=10000)
        except Exception:
            page.evaluate("document.querySelector('form')?.submit()")

        pin = None
        otp_skipped = False
        for attempt in range(1, int(cfg.get("MAX_ATTEMPTS", 3)) + 1):
            log(f"--- Tentativo {attempt} ---")
            if attempt > 1:
                tzid, number = onlinesim_get_number(cfg)
                if not number:
                    log("[-] Niente numero."); return False
                log(f"[+] Nuovo numero: {number} (tzid: {tzid})")

            try:
                page.wait_for_selector(
                    "[name='cellulare_challenge'], #pin_challenge",
                    timeout=20000,
                )
            except Exception:
                if mail_host in page.url:
                    log(f"[+] OTP saltato: siamo su {mail_host}.")
                    otp_skipped = True; break
                log(f"[-] Nessun campo challenge. URL: {page.url}")
                if tzid: onlinesim_close_operation(cfg, tzid)
                continue

            if mail_host in page.url:
                log(f"[+] OTP saltato: siamo su {mail_host}.")
                otp_skipped = True; break

            if page.query_selector("#pin_challenge"):
                log("[i] Campo PIN già presente.")
            else:
                force_fill(page, "[name='cellulare_challenge']", number)
                try:
                    page.click("#button_submit_challenge", timeout=10000)
                except Exception:
                    page.evaluate("document.querySelector('form')?.submit()")
                try:
                    page.wait_for_selector("#pin_challenge", timeout=30000)
                except Exception:
                    if mail_host in page.url:
                        otp_skipped = True; break
                    log(f"[-] PIN non apparso. URL: {page.url}")
                    if tzid: onlinesim_close_operation(cfg, tzid)
                    go_back_to_phone_page(page)
                    continue

            sms = onlinesim_get_sms(cfg, tzid) if tzid else None
            if sms:
                log(f"[+] SMS: {sms[:200]}")
                pin = extract_pin_from_sms(sms)
                if pin:
                    log(f"[+] PIN: {pin}")
                    break
                log("[-] PIN non trovato.")
            else:
                log("[-] Nessun SMS.")

            if tzid: onlinesim_close_operation(cfg, tzid)
            if not go_back_to_phone_page(page):
                return False

        if otp_skipped:
            log("[i] Procedo con Annulla + Fine.")
        elif not pin:
            log("[-] Nessun PIN.")
            return False
        else:
            force_fill(page, "#pin_challenge", pin)
            try:
                page.click("#button_submit_pin", timeout=10000)
            except Exception:
                page.evaluate("document.querySelector('form')?.submit()")

        finalize_after_pin(page)

        success = False
        try:
            page.wait_for_url(f"**/{mail_host}/**", timeout=120000)
            log(f"[***] REGISTRAZIONE COMPLETATA: {page.url} [***]")
            success = True
        except Exception:
            log(f"[?] URL finale: {page.url}")
            success = mail_host in page.url

        if success:
            if save_cookies:
                save_auth_json(context, page, username, cookie_dir)
            append_created_account(acc, comune, provider)
            remove_account_line(acc)
        return success

    except Exception as e:
        log(f"[-] Eccezione account {username}: {e}")
        return False
    finally:
        try: browser.close()
        except Exception: pass

def main():
    global WEBSHARE_API_URL, WEBSHARE_CACHE_TIME

    ensure_default_files()
    print_logo()
    cfg = parse_config()
    if str(cfg.get("ONLINESIM_API_KEY", "")).startswith("INCOLLA"):
        log("[-] Configura ONLINESIM_API_KEY in config.txt")
        return

    save_cookies = bool(cfg.get("Salvare cookie di accesso", True))
    cookie_dir_rel = str(cfg.get("Cartella cookie", "cookies")).strip() or "cookies"
    cookie_dir = SCRIPT_DIR / cookie_dir_rel
    comuni = load_comuni()

    provider = str(cfg.get("PROVIDER", "libero")).lower()
    if provider not in PROVIDERS:
        log(f"[!] PROVIDER '{provider}' non valido, uso 'libero'")
        provider = "libero"
        cfg["PROVIDER"] = provider

    log(f"[i] Provider: {provider}")
    log(f"[i] Salva cookie: {save_cookies} (cartella: {cookie_dir})")
    log(f"[i] Pausa tra account: {cfg.get('PAUSA_TRA_ACCOUNT', 30)}s")

    if cfg.get("Uso_proxy", False):
        WEBSHARE_API_URL = str(cfg.get("WEBSHARE_API_URL", "")).strip()
        WEBSHARE_CACHE_TIME = int(cfg.get("WEBSHARE_CACHE_TIME", 3600))
        log("[i] Proxy ATTIVO — provider: webshare")
        if not WEBSHARE_API_URL:
            log("[!] WEBSHARE_API_URL vuoto: proseguo senza proxy.")
        elif not fetch_webshare_proxies():
            log("[!] Impossibile caricare i proxy Webshare: proseguo senza proxy.")
        else:
            log(f"[i] {len(WEBSHARE_PROXIES)} proxy Webshare in cache")
    else:
        log("[i] Proxy DISATTIVATO (Uso_proxy = No)")

    while True:
        try:
            accounts = load_accounts()
            if not accounts:
                logging.info("Nessun account da registrare. Attesa 60 secondi...")
                time.sleep(60)
                continue

            logging.info(f"\nTrovati {len(accounts)} account da registrare.")
            for i, acc in enumerate(accounts, 1):
                log(f"\n### ACCOUNT {i}/{len(accounts)} — {acc['username']} ###")
                ok = run_account(cfg, acc, comuni, save_cookies, cookie_dir)
                if ok:
                    log(f"[+] Account {acc['username']} completato.")
                else:
                    log(f"[-] Account {acc['username']} FALLITO. Riga lasciata in dati_account.txt.")

                pausa = int(cfg.get("PAUSA_TRA_ACCOUNT", 30))
                if i < len(accounts) and pausa > 0:
                    log(f"[i] Pausa {pausa}s prima del prossimo account...")
                    time.sleep(pausa)

            logging.info("Lista completata. Ricontrollo dati_account.txt...")
            time.sleep(5)
        except KeyboardInterrupt:
            log("[i] Interrotto da tastiera.")
            break
        except Exception as e:
            log(f"[-] Errore nel loop principale: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()
