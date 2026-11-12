import json
import os
import random
import re
import time
import logging
from datetime import datetime
from pathlib import Path

import requests
from colorama import init as colorama_init, Fore, Style

try:
    import cloakbrowser
    CLOAKBROWSER_AVAILABLE = True
except ImportError:
    cloakbrowser = None
    CLOAKBROWSER_AVAILABLE = False

try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    curl_requests = None
    CURL_CFFI_AVAILABLE = False

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    sync_playwright = None
    PLAYWRIGHT_AVAILABLE = False

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
        return f"{c}{super().format(record)}{Style.RESET_ALL}"

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
!@!  !!!  !!!  !!@!@!    !!! !!@!!  !!!  !!!       !!!  @!@  !!!
:!:  !!:  !!:  !!: :!!   :!!   !!:  !!:  !!:       !!:  !!:  !!!
 ::!!:!   :!:  :!:  !:!  :!:   !::  :!:   :!:      :!:  :!:  !:!
  ::::     ::  ::   :::   ::: ::::   ::   :: ::::   ::  ::::: ::
   :      :     :   : :   :: :: :   :    : :: : :  :     : :  :


@@@  @@@    @@@        @@@
@@@  @@@   @@@@       @@@@
@@!  @@@  @@@!!      @@@!!
!@!  @!@    !@!        !@!
@!@  !@!    @!@        @!@
!@!  !!!    !@!        !@!
:!:  !!:    !!:        !!:
 ::!!:!     :!:  :!:   :!:
  ::::      :::  :::   :::
   :        :::  :::   :::


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
# Metodo registrazione: "browser" (cloakbrowser) oppure "curl" (curl_cffi)
METODO = browser

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

# Browser (solo METODO = browser)
HEADLESS = false
HUMANIZE = true
HUMAN_PRESET = "careful"
ALLOW_3P_COOKIES = true
TRANSPARENT_PROXY = false

# Salvataggio cookie di accesso
Salvare cookie di accesso = Si
Cartella cookie = cookies

# ============================================================
# 2CAPTCHA (curl + opzionale browser)
# ============================================================
2CAPTCHA_API_KEY = "INCOLLA_QUI_LA_TUA_CHIAVE_2CAPTCHA"
RECAPTCHA_SITEKEY_V3 = "6Ld6OtQZAAAAAEoUAMxGZfzboeicLPJ3GSrAJgsQ"
RECAPTCHA_SITEKEY_V2 = "6LeGN_8SAAAAAMVXRVletwdjUedq_qtJfk8VFvaO"
RECAPTCHA_MIN_SCORE = 0.3

# Risolvi captcha con 2captcha anche in METODO = browser (Si / No)
# Se No, in browser il captcha va risolto manualmente.
Risolvi captcha con 2captcha (browser) = Si

# ============================================================
# CHECK USERNAME (evita di sprecare numeri se già esistente)
# ============================================================
# Comportamento se lo username è già in uso:
#   scarta    -> salta l'account (nessun numero/token sprecato)
#   suggerito -> usa il primo username suggerito dal server
#   errore    -> blocca tutto e avvisa l'utente
Comportamento username esistente = scarta

# Abilita il check preventivo dello username prima della registrazione
Check username prima registrazione = Si

# ============================================================
# FALLBACK NUMERO (solo METODO = curl)
# ============================================================
# Se attivo, quando OnlineSim non fornisce un numero (o tutti i
# tentativi OTP falliscono) usa il numero di fallback sotto.
Fallback numero curl = No
Numero fallback curl = 3511490097
# Se Si, salta OnlineSim e usa SEMPRE il numero di fallback.
# Con numero di fallback non si attende l'OTP: se il sito lo richiede,
# l'account viene scartato subito (nessun SMS leggibile).
Usare solo fallback = No

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

CONFIG_REQUIRED_KEYS = {
    "METODO": None,
    "2CAPTCHA_API_KEY": None,
    "RECAPTCHA_SITEKEY_V3": None,
    "RECAPTCHA_SITEKEY_V2": None,
    "RECAPTCHA_MIN_SCORE": None,
    "Fallback numero curl": None,
    "Numero fallback curl": None,
    "Usare solo fallback": None,
    "Comportamento username esistente": None,
    "Check username prima registrazione": None,  
    "Risolvi captcha con 2captcha (browser)": None,
}

CONFIG_MISSING_BLOCK = """
# ============================================================
# AGGIUNTE AUTOMATICHE (v1.1)
# ============================================================
# Metodo registrazione: "browser" (cloakbrowser) oppure "curl" (curl_cffi)
METODO = browser

# ============================================================
# 2CAPTCHA (curl + opzionale browser)
# ============================================================
2CAPTCHA_API_KEY = "INCOLLA_QUI_LA_TUA_CHIAVE_2CAPTCHA"
RECAPTCHA_SITEKEY_V3 = "6Ld6OtQZAAAAAEoUAMxGZfzboeicLPJ3GSrAJgsQ"
RECAPTCHA_SITEKEY_V2 = "6LeGN_8SAAAAAMVXRVletwdjUedq_qtJfk8VFvaO"
RECAPTCHA_MIN_SCORE = 0.3

# Risolvi captcha con 2captcha anche in METODO = browser (Si / No)
Risolvi captcha con 2captcha (browser) = Si

# ============================================================
# CHECK USERNAME
# ============================================================
# scarta / suggerito / errore
Comportamento username esistente = scarta
Check username prima registrazione = Si

# ============================================================
# FALLBACK NUMERO (solo METODO = curl)
# ============================================================
Fallback numero curl = No
Numero fallback curl = 3511490097
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


def update_config_file():
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
    except Exception as e:
        log(f"[!] Impossibile leggere {CONFIG_FILE.name}: {e}")
        return

    current_values = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        current_values[k.strip()] = line.rstrip("\n")

    expected_keys = set()
    for line in DEFAULT_CONFIG.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        expected_keys.add(s.split("=", 1)[0].strip())

    has_all_keys = all(k in current_values for k in expected_keys)
    marker_comments = [
        "# Metodo registrazione:",
        "# 2CAPTCHA (solo METODO = curl)",
        "# FALLBACK NUMERO (solo METODO = curl)",
    ]
    has_all_comments = all(m in text for m in marker_comments)

    if has_all_keys and has_all_comments:
        log(f"[i] {CONFIG_FILE.name} già aggiornato.")
        return

    new_lines = []
    used_keys = set()
    for line in DEFAULT_CONFIG.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            new_lines.append(line)
            continue
        k = s.split("=", 1)[0].strip()
        if k in current_values:
            new_lines.append(current_values[k])
            used_keys.add(k)
        else:
            new_lines.append(line)  # default per chiavi nuove

    custom = [(k, ln) for k, ln in current_values.items() if k not in expected_keys]
    if custom:
        new_lines.append("")
        new_lines.append("# ============================================================")
        new_lines.append("# CHIAVI CUSTOM (preservate)")
        new_lines.append("# ============================================================")
        for _, ln in custom:
            new_lines.append(ln)

    new_text = "\n".join(new_lines) + "\n"

    try:
        CONFIG_FILE.write_text(new_text, encoding="utf-8")
        log(f"[+] {CONFIG_FILE.name} riscritto in formato pulito "
            f"({len(used_keys)} valori preservati, "
            f"{len(custom)} chiavi custom).")
    except Exception as e:
        log(f"[!] Errore scrittura {CONFIG_FILE.name}: {e}")

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
        elif re.fullmatch(r"-?\d+\.\d+", v):
            v = float(v)
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


def build_urls_curl(provider):
    p = PROVIDERS[provider]
    if provider == "virgilio":
        reg_url = f"{p['reg_base']}/?service_id=hp&ref=hp-hd"
    else:
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
                    if number.startswith("+39"):
                        number = number[3:]
                    elif number.startswith("39"):
                        number = number[2:]
                    log(f"Numero OnlineSim: {number} (tzid: {tzid})")
                    return tzid, number
            else:
                err = data.get("response_text") or data.get("msg") or "unknown"
                log(f"OnlineSim errore: {err}")
                if "NO_NUMBERS" in str(err).upper():
                    time.sleep(30)
                elif "NO_BALANCE" in str(err).upper():
                    return None, None
                else:
                    time.sleep(5)
        except Exception as e:
            log(f"Eccezione getNum: {e}"); time.sleep(5)
    return None, None

def get_curl_number(cfg):
    use_only_fb = bool(cfg.get("Usare solo fallback", False))
    fb = str(cfg.get("Numero fallback curl", "")).strip()

    if use_only_fb:
        if not fb:
            log("[-] 'Usare solo fallback = Si' ma 'Numero fallback curl' è vuoto.")
            return None, None, False
        log(f"[i] 'Usare solo fallback = Si': salto OnlineSim, uso {fb}")
        return None, fb, True

    tzid, number = onlinesim_get_number(cfg)
    if number:
        return tzid, number, False

    if bool(cfg.get("Fallback numero curl", False)):
        if fb:
            log(f"[!] OnlineSim non disponibile: uso numero di fallback {fb}")
            return None, fb, True
        log("[!] Fallback attivo ma 'Numero fallback curl' vuoto.")
    return None, None, False

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
            if r.status_code != 200:
                time.sleep(5); continue
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
                if isinstance(msg, str) and msg.strip():
                    return msg
                if isinstance(msg, dict):
                    txt = msg.get("msg") or msg.get("text") or msg.get("message")
                    if txt:
                        return txt
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
    if not sms_text:
        return None
    text = sms_text.strip()

    # 1) Formato "[provider] ... e': CODICE" / "...: CODICE"
    #    Prende l'ULTIMO ":" e prova il token subito dopo.
    idx = text.rfind(":")
    if idx != -1:
        cand = text[idx + 1:].strip().rstrip(" .,;!?'\"")
        if cand:
            first = cand.split()[0].strip("'\"")
            if re.fullmatch(r"[A-Za-z0-9]{4,10}", first):
                return first

    # 2) Fallback: pattern "codice ... e' XXX" o "codice ...: XXX"
    m = re.search(
        r"(?:codice|code|pin|otp)[^A-Za-z0-9]{0,40}(?:e['’]?\s*:?\s*)?([A-Za-z0-9]{4,10})\b",
        text, re.IGNORECASE,
    )
    if m:
        tok = m.group(1)
        if tok.lower() not in {"codice", "verifica", "account", "libero",
                               "mail", "virgilio", "sender", "receiver"}:
            return tok

    # 3) Fallback generico (comportamento precedente)
    blacklist = {"codice", "verifica", "account", "libero", "mail", "virgilio",
                 "sender", "receiver", "smsc", "scts", "slot"}
    for m in re.finditer(r"\b([A-Za-z0-9]{4,10})\b", text):
        tok = m.group(1)
        if tok.lower() in blacklist:
            continue
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


def build_proxy_url_for_curl():
    p = pick_proxy()
    if not p:
        return None
    server = p["server"].replace("http://", "")
    return f"http://{p['username']}:{p['password']}@{server}", p


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
        try:
            page.dispatch_event(selector, ev)
        except Exception:
            pass


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


def auto_click_or_wait_captcha(page, cfg, timeout_s=300, captcha_grace_s=8):
    start = time.time()
    captcha_seen = False
    clicked = False
    sels = ["iframe[src*='recaptcha']", "iframe[title*='recaptcha']",
            "div.g-recaptcha", "#recaptcha", ".g-recaptcha",
            "#captcha", ".captcha"]
    solved = False
    while time.time() - start < timeout_s:
        if "join2.phtml" in page.url:
            return True
        captcha = False
        for s in sels:
            try:
                el = page.query_selector(s)
                if el and el.is_visible():
                    captcha = True
                    break
            except Exception:
                pass
        if captcha:
            if not captcha_seen:
                log("[!] CAPTCHA visibile.")
                captcha_seen = True
            if not solved:
                # Tenta la risoluzione automatica
                try:
                    if solve_v2_in_browser(cfg, page):
                        solved = True
                        time.sleep(2)
                        continue
                except Exception as e:
                    log(f"[!] Errore risoluzione v2: {e}")
                # Se non risolto, attende l'intervento manuale
                log("[!] Risolvilo tu, poi clicca Avanti.")
            time.sleep(1.0)
            continue
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

def solve_v2_in_browser(cfg, page):
    if not bool(cfg.get("Risolvi captcha con 2captcha (browser)", True)):
        log("[i] Risoluzione automatica captcha disattivata (config): attesa manuale.")
        return False

    try:
        captcha_box_visible = page.evaluate(
            """() => {
                const b = document.getElementById('captcha_box');
                return !!(b && b.offsetParent !== null);
            }"""
        )
    except Exception:
        captcha_box_visible = False

    if not captcha_box_visible:
        sels = ["iframe[src*='recaptcha']", "div.g-recaptcha", "#recaptcha",
                ".g-recaptcha", "#recaptcha_regmail"]
        found = False
        for s in sels:
            try:
                el = page.query_selector(s)
                if el and el.is_visible():
                    found = True
                    break
            except Exception:
                pass
        if not found:
            return False

    log("[i] CAPTCHA v2 rilevato: risolvo con 2Captcha...")

    sitekey = None
    try:
        sitekey = page.evaluate(
            """() => {
                const el = document.querySelector('.g-recaptcha, div[data-sitekey]');
                if (el && el.getAttribute('data-sitekey')) return el.getAttribute('data-sitekey');
                const ifr = document.querySelector("iframe[src*='recaptcha']");
                if (ifr) {
                    const m = ifr.src.match(/[?&]k=([^&]+)/);
                    if (m) return decodeURIComponent(m[1]);
                }
                return null;
            }"""
        )
    except Exception:
        pass

    if not sitekey:
        sitekey = cfg.get("RECAPTCHA_SITEKEY_V2", "")
    if not sitekey:
        log("[-] Sitekey v2 non trovata.")
        return False

    token = solve_v2(cfg, page.url, sitekey)
    if not token:
        log("[-] 2Captcha non ha risolto il v2.")
        return False

    try:
        page.evaluate(
            """() => {
                const b = document.getElementById('captcha_box');
                if (b) b.style.display = 'block';
            }"""
        )
    except Exception:
        pass

    page.evaluate(
        """(token) => {
            let ta = document.getElementById('g-recaptcha-response');
            if (!ta) {
                ta = document.createElement('textarea');
                ta.id = 'g-recaptcha-response';
                ta.name = 'g-recaptcha-response';
                ta.style.display = 'none';
                document.body.appendChild(ta);
            }
            ta.value = token;
            ta.innerHTML = token;
            ta.style.display = '';
        }""",
        token,
    )

    try:
        called = page.evaluate(
            """(token) => {
                if (typeof window.verifyCallback === 'function') {
                    window.verifyCallback(token);
                    return true;
                }
                if (window.grecaptcha && typeof window.grecaptcha.getResponse === 'function') {
                    const ev = new Event('change', { bubbles: true });
                    const ta = document.getElementById('g-recaptcha-response');
                    if (ta) ta.dispatchEvent(ev);
                    return false;
                }
                return false;
            }""",
            token,
        )
        if called:
            log("[+] verifyCallback(token) invocato.")
        else:
            log("[!] verifyCallback non trovato: provo a proseguire comunque.")
    except Exception as e:
        log(f"[!] Errore invocazione verifyCallback: {e}")

    try:
        page.evaluate(
            """() => {
                const b = document.getElementById('captcha_box');
                if (b) b.style.display = 'none';
                const err = document.getElementById('checkstr_error');
                if (err) err.style.display = 'none';
            }"""
        )
    except Exception:
        pass

    log("[+] Token v2 iniettato e callback attivata.")
    return True

def go_back_to_phone_page(page):
    log("Clicco la X per tornare alla pagina del numero...")
    for sel in ["#button_back", "button[name='button_back']",
                "button.close", "button[aria-label='Close']"]:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                log(f"[+] Click su '{sel}'")
                break
        except Exception:
            continue
    else:
        log("[-] Pulsante chiusura non trovato.")
        return False
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
        if btn:
            btn.click()
            log("[+] 'Annulla' cliccato")
    except Exception as e:
        log(f"[!] Errore click Annulla: {e}")
    time.sleep(3)
    log("Clicco 'Fine'...")
    try:
        btn = page.query_selector("button[data-action='done']")
        if btn:
            btn.click()
            log("[+] 'Fine' cliccato")
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


def save_auth_json_curl(session, username, cookie_dir):
    try:
        cookie_dir.mkdir(parents=True, exist_ok=True)
        cookies = []
        try:
            for c in session.cookies.jar:
                cookie = {
                    "name": c.name,
                    "value": c.value,
                    "domain": c.domain or "",
                    "path": c.path or "/",
                    "expires": c.expires if c.expires else -1,
                    "httpOnly": False,
                    "secure": bool(c.secure),
                    "sameSite": "Lax",
                }
                cookies.append(cookie)
        except Exception:
            cookies = []
        out = {"cookies": cookies, "origins": []}
        path = cookie_dir / f"{username}.json"
        path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        log(f"[+] Cookie (curl) salvati in {path}")
    except Exception as e:
        log(f"[!] Errore salvataggio cookie (curl): {e}")


def run_account_browser(cfg, acc, comuni, save_cookies, cookie_dir):
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
    log(f"[METODO=browser] Provider: {provider} | {reg_base} -> {mail_host}")
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

    username_check_result = {"exists": None, "suggestions": [], "seen": False}

    def _on_response(response):
        try:
            if "check_username.php" not in response.url:
                return
            if response.request.method != "POST":
                return
            body = response.text()
            username_check_result["seen"] = True
            if re.search(r'r\s*:\s*["\']exist["\']', body):
                username_check_result["exists"] = True
                m = re.search(r"sugg\s*:\s*\[([^\]]*)\]", body)
                if m:
                    username_check_result["suggestions"] = re.findall(
                        r"['\"]([^'\"]+)['\"]", m.group(1)
                    )
            elif re.search(r'r\s*:\s*["\']not_exist["\']', body) or \
                 re.search(r'r\s*:\s*["\']ok["\']', body):
                username_check_result["exists"] = False
            log(f"[i] check_username intercettato: exists={username_check_result['exists']} "
                f"sugg={username_check_result['suggestions']}")
        except Exception:
            pass

    page.on("response", _on_response)

    try:
        page.goto(reg_url, wait_until="domcontentloaded", timeout=60000)
        accept_cookies_if_present(page)
        force_fill(page, "#username", username)
        force_fill(page, "#password", password)

        if bool(cfg.get("Check username prima registrazione", True)):
            log("[i] Attendo check_username dal JS del sito...")
            for _ in range(20):  # max 10s pero intanto faccio cosi
                if username_check_result["seen"]:
                    break
                time.sleep(0.5)

            if username_check_result["seen"] and username_check_result["exists"]:
                nuovo, azione = _handle_username_check_result(
                    cfg, username, True, username_check_result["suggestions"]
                )
                if azione == "errore":
                    log("[-] Check username: comportamento 'errore', blocco l'esecuzione.")
                    return "errore"
                if azione == "scarta":
                    log(f"[-] Account '{username}' scartato (username già in uso). "
                        "Riga RIMOSSA da dati_account.txt.")
                    remove_account_line(acc)
                    return "scartato"
                if nuovo and nuovo != username:
                    log(f"[i] Username suggerito: '{nuovo}', riprovo")
                    username = nuovo
                    acc = dict(acc)
                    acc["username"] = nuovo
                    username_check_result["seen"] = False
                    username_check_result["exists"] = None
                    username_check_result["suggestions"] = []
                    force_fill(page, "#username", nuovo)
                    try:
                        page.evaluate(
                            "(sel) => { const el=document.querySelector(sel); "
                            "if(el){ el.dispatchEvent(new Event('blur',{bubbles:true})); } }",
                            "#username"
                        )
                    except Exception:
                        pass
                    for _ in range(20):
                        if username_check_result["seen"]:
                            break
                        time.sleep(0.5)
                    if username_check_result["seen"] and username_check_result["exists"]:
                        log("[!] Anche il suggerimento è occupato: scarto account.")
                        return False
            elif not username_check_result["seen"]:
                log("[i] check_username non rilevato dal JS: proseguo senza check.")

        log("=" * 55)
        log("Attendo: se c'è CAPTCHA lo risolvi tu; altrimenti clicco Avanti.")
        log("=" * 55)
        #if not auto_click_or_wait_captcha(page, timeout_s=300, captcha_grace_s=8): # prima
        if not auto_click_or_wait_captcha(page, cfg, timeout_s=300, captcha_grace_s=8): # dopo
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
                    log("[-] Niente numero.")
                    return False
                log(f"[+] Nuovo numero: {number} (tzid: {tzid})")

            try:
                page.wait_for_selector(
                    "[name='cellulare_challenge'], #pin_challenge",
                    timeout=20000,
                )
            except Exception:
                if mail_host in page.url:
                    log(f"[+] OTP saltato: siamo su {mail_host}.")
                    otp_skipped = True
                    break
                log(f"[-] Nessun campo challenge. URL: {page.url}")
                if tzid:
                    onlinesim_close_operation(cfg, tzid)
                continue

            if mail_host in page.url:
                log(f"[+] OTP saltato: siamo su {mail_host}.")
                otp_skipped = True
                break

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
                        otp_skipped = True
                        break
                    log(f"[-] PIN non apparso. URL: {page.url}")
                    if tzid:
                        onlinesim_close_operation(cfg, tzid)
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

            if tzid:
                onlinesim_close_operation(cfg, tzid)
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
                save_auth_json(context, page, username, cookie_dir) # cookie ok
            append_created_account(acc, comune, provider)
            remove_account_line(acc)
        return success

    except Exception as e:
        log(f"[-] Eccezione account {username}: {e}")
        return False
    finally:
        try:
            browser.close()
        except Exception:
            pass


def get_iolcmp_exp_via_browser_playwright(page_url, extra_selectors=None):
    if not PLAYWRIGHT_AVAILABLE:
        log("[-] Playwright non installato. Necessario per METODO=curl.")
        log("[-] Installa con:  pip install playwright  &&  playwright install chromium")
        return None

    selectors = [
        "button.iubenda-cs-accept-btn",
        "button.ubl-cst__btn--accept",
        "button.iubenda-cs-btn-primary",
        "text=Accetta e Chiudi",
        "text=Accetta tutto",
        "text=Accetta",
    ]
    if extra_selectors:
        selectors.extend(extra_selectors)

    log("[i] Avvio browser headless per ottenere iolcmp-exp...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(locale="it-IT")
            page = context.new_page()
            page.goto(page_url, wait_until="domcontentloaded", timeout=30000)

            accepted = False
            for sel in selectors:
                try:
                    page.wait_for_selector(sel, timeout=5000, state="visible")
                    page.click(sel)
                    log(f"[+] Banner accettato con selettore: {sel}")
                    accepted = True
                    break
                except Exception:
                    continue

            if not accepted:
                log("[!] Nessun banner trovato. Provo a leggere il cookie comunque.")

            page.wait_for_timeout(1500)
            cookies = context.cookies()
            iolcmp_value = None
            for c in cookies:
                if c["name"] == "iolcmp-exp":
                    iolcmp_value = c["value"]
                    break
            browser.close()

            if iolcmp_value:
                log(f"[+] iolcmp-exp ottenuto: {iolcmp_value}")
                return iolcmp_value
            log("[!] Cookie iolcmp-exp non trovato.")
            return None
    except Exception as e:
        log(f"[!] Errore browser headless: {e}")
        return None


def ensure_iubenda_cookie(session, page_url, base, extra_selectors=None):
    try:
        for cookie in session.cookies.jar:
            if cookie.name == "iolcmp-exp":
                log(f"[+] iolcmp-exp già in sessione: {cookie.value}")
                return cookie.value
    except Exception:
        pass

    domain = base.replace("https://", "").replace("http://", "")
    value = get_iolcmp_exp_via_browser_playwright(page_url, extra_selectors)
    if value:
        try:
            session.cookies.set("iolcmp-exp", value, domain=domain, path="/")
        except Exception:
            try:
                session.cookies.set("iolcmp-exp", value)
            except Exception as e:
                log(f"[!] Impossibile impostare iolcmp-exp in sessione: {e}")
        log(f"[+] iolcmp-exp impostato da browser: {value}")
        return value

    log("[-] Impossibile ottenere iolcmp-exp: esecuzione bloccata.")
    return None


def solve_v3(cfg, page_url, action):
    api_key = cfg.get("2CAPTCHA_API_KEY", "")
    sitekey = cfg.get("RECAPTCHA_SITEKEY_V3", "")
    min_score = float(cfg.get("RECAPTCHA_MIN_SCORE", 0.3))
    if not api_key or str(api_key).startswith("INCOLLA"):
        log("[-] 2CAPTCHA_API_KEY non configurata in config.txt.")
        return None
    if not sitekey:
        log("[-] RECAPTCHA_SITEKEY_V3 non configurata in config.txt.")
        return None

    task = {
        "type": "RecaptchaV3TaskProxyless",
        "websiteURL": page_url,
        "websiteKey": sitekey,
        "minScore": min_score,
        "pageAction": action,
        "isEnterprise": False,
    }
    try:
        r = requests.post("https://api.2captcha.com/createTask",
                          json={"clientKey": api_key, "task": task}, timeout=40).json()
    except Exception as e:
        log(f"[-] Errore createTask v3: {e}")
        return None
    if r.get("errorId") != 0:
        log(f"[-] Errore createTask v3: {r}")
        return None
    task_id = r["taskId"]
    log(f"Task v3 ({action}) creato: {task_id}")
    for _ in range(40):
        time.sleep(2)
        try:
            res = requests.post("https://api.2captcha.com/getTaskResult",
                                json={"clientKey": api_key, "taskId": task_id},
                                timeout=40).json()
        except Exception:
            continue
        if res.get("status") == "ready":
            return res["solution"]["gRecaptchaResponse"]
        if res.get("errorId") != 0:
            log(f"[-] Errore v3: {res}")
            return None
    log("[-] Timeout solver v3.")
    return None


def solve_v2(cfg, page_url, sitekey=None):
    api_key = cfg.get("2CAPTCHA_API_KEY", "")
    if not api_key or str(api_key).startswith("INCOLLA"):
        log("[-] 2CAPTCHA_API_KEY non configurata in config.txt.")
        return None

    if not sitekey:
        sitekey = cfg.get("RECAPTCHA_SITEKEY_V2", "")
    if not sitekey:
        log("[-] RECAPTCHA_SITEKEY_V2 non configurata in config.txt.")
        return None

    task = {
        "type": "RecaptchaV2TaskProxyless",
        "websiteURL": page_url,
        "websiteKey": sitekey,
        "isInvisible": False,
    }
    try:
        r = requests.post("https://api.2captcha.com/createTask",
                          json={"clientKey": api_key, "task": task}, timeout=40).json()
    except Exception as e:
        log(f"[-] Errore createTask v2: {e}")
        return None
    if r.get("errorId") != 0:
        log(f"[-] Errore createTask v2: {r}")
        return None

    task_id = r["taskId"]
    log(f"Task v2 creato: {task_id}, attendo...")
    for _ in range(40):
        time.sleep(3)
        try:
            res = requests.post("https://api.2captcha.com/getTaskResult",
                                json={"clientKey": api_key, "taskId": task_id},
                                timeout=40).json()
        except Exception:
            continue
        if res.get("status") == "ready":
            log("[+] Token v2 ricevuto.")
            return res["solution"]["gRecaptchaResponse"]
        if res.get("errorId") != 0:
            log(f"[-] Errore v2: {res}")
            return None
    log("[-] Timeout solver v2.")
    return None

def check_username_available(cfg, base_url, page_url, username, provider,
                              session=None, token_v2=None):
    domain = PROVIDERS[provider]["domain"]

    token_v3 = solve_v3(cfg, page_url, "check_username")
    if not token_v3:
        log("[!] Check username: impossibile ottenere token v3.")
        return None, []

    data = {
        "usr": username,
        "usrdomain": domain,
        "fname": "",
        "lname": "",
        "g_recaptcha_response": token_v2 if token_v2 else "",
        "check_username_recaptchav3_token": token_v3,
    }
    headers = [
        ("Accept", "*/*"),
        ("Accept-Language", "it;q=0.6"),
        ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
        ("Origin", base_url),
        ("Referer", page_url),
        ("X-Requested-With", "XMLHttpRequest"),
    ]
    try:
        if session is not None:
            r = session.post(f"{base_url}/check_username.php",
                             data=data, headers=headers, timeout=30)
        else:
            r = requests.post(f"{base_url}/check_username.php",
                              data=data, headers=headers, timeout=30)
    except Exception as e:
        log(f"[!] Check username: errore rete: {e}")
        return None, []

    log(f"[i] Check username risposta: {r.status_code} - {r.text[:300]}")
    text = r.text or ""

    if re.search(r'r\s*:\s*["\']exist["\']', text):
        sugg = []
        m = re.search(r"sugg\s*:\s*\[([^\]]*)\]", text)
        if m:
            for tok in re.findall(r"['\"]([^'\"]+)['\"]", m.group(1)):
                sugg.append(tok)
        return True, sugg

    if re.search(r'r\s*:\s*["\']ok["\']', text) or \
       re.search(r'r\s*:\s*["\']not_exist["\']', text):
        return False, []

    log("[!] Check username: risposta non riconosciuta.")
    return None, []


def _handle_username_check_result(cfg, username, exists, suggestions):
    if exists is None:
        return username, "procedi"

    if not exists:
        log(f"[+] Username '{username}' disponibile.")
        return username, "procedi"

    comportamento = str(cfg.get("Comportamento username esistente", "scarta")).lower().strip()
    log(f"[!] Username '{username}' già in uso. Suggerimenti: {suggestions}")
    log(f"[i] Comportamento configurato: {comportamento}")

    if comportamento == "suggerito":
        if suggestions:
            nuovo = suggestions[0]
            log(f"[i] Uso username suggerito: '{nuovo}'")
            return nuovo, "procedi"
        log("[-] Nessun suggerimento disponibile: scarto account.")
        return None, "scarta"

    if comportamento == "errore":
        log("[-] Username esistente: blocco l'esecuzione (config = errore).")
        return None, "errore"

    log("[i] Username esistente: scarto account.")
    return None, "scarta"   

def _curl_follow_redirect(session, base, location):
    if not location:
        return None
    if not location.startswith("http"):
        location = base + "/" + location.lstrip("/")
    try:
        return session.get(location, allow_redirects=True, timeout=30)
    except Exception as e:
        log(f"[!] Errore follow redirect: {e}")
        return None


def _curl_check_response(r, expected_fragment, step_name):
    loc = r.headers.get("Location") or ""
    log(f"  [{step_name}] Status: {r.status_code}, Location: {loc}")
    if r.status_code == 302:
        return expected_fragment in loc
    return False


def _curl_step4_challenge1(session, base, phone):
    log(f"  Invio numero a challenge1: {phone}")
    r = session.post(f"{base}/challenge1_check.php",
                     data={"cellulare_challenge": phone},
                     allow_redirects=False, timeout=30)
    loc = r.headers.get("Location") or ""
    log(f"  [challenge1] Status: {r.status_code}, Location: {loc}")

    if "end.phtml" in loc:
        log("[***] OTP non richiesto: registrazione completata. [***]")
        return "done"
    if "join3.phtml" in loc:
        return "otp_required"
    log(f"[-] Risposta inattesa da challenge1: {r.text[:200]}")
    return "error"


def run_account_curl(cfg, acc, comuni, save_cookies, cookie_dir):
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
    base, mail_host, page_url = build_urls_curl(provider)

    if comune.strip().upper() == "R":
        comune = random.choice(comuni)
        log(f"[i] Comune casuale scelto: {comune}")

    log("=" * 60)
    log(f"[METODO=curl] Provider: {provider} | {base} -> {mail_host}")
    log(f"Account: {username} | {firstname} {lastname} | {dob} | {gender} | {comune}")
    log("=" * 60)

    session_kwargs = {"impersonate": "chrome120"}
    if cfg.get("Uso_proxy", False):
        proxy_info = build_proxy_url_for_curl()
        if proxy_info:
            proxy_url, proxy_cfg = proxy_info
            session_kwargs["proxies"] = {"http": proxy_url, "https": proxy_url}
            log(f"[i] Proxy Webshare (curl): {proxy_cfg['server']}")

    s = curl_requests.Session(**session_kwargs)

    try:
        log("=== STEP 0: visita iniziale e cookie ===")
        s.get(page_url, timeout=30)
        log(f"Cookie dopo GET: {dict(s.cookies)}")
        ensure_iubenda_cookie(s, page_url, base)
        log(f"Cookie dopo gestione iubenda: {dict(s.cookies)}")

        log("=== STEP 1a: join1_ready (pre-validazione v3) ===")
        token_v3 = solve_v3(cfg, page_url, "join1")
        if not token_v3:
            log("[-] Impossibile ottenere token v3.")
            return False

        pre_url = f"{base}/join1_ready_get_recaptchav3_score.php"
        pre_headers = [
            ("Accept", "application/json, text/javascript, */*; q=0.01"),
            ("X-Requested-With", "XMLHttpRequest"),
            ("Referer", page_url),
        ]
        r_pre = s.get(pre_url, params={"join1_ready_recaptchav3_token": token_v3},
                      headers=pre_headers, timeout=30)
        log(f"Pre-validazione: {r_pre.status_code} - {r_pre.text}")

        try:
            pre_data = r_pre.json()
        except Exception:
            pre_data = {}

        token_v2 = None
        if pre_data.get("success") == "show_captcha":
            log("Il server richiede il CAPTCHA visivo (v2).")
            token_v2 = solve_v2(cfg, page_url)
            if not token_v2:
                log("[-] Impossibile ottenere token v2.")
                return False
        elif pre_data.get("success") == "ok":
            log("Token v3 accettato direttamente.")

        if bool(cfg.get("Check username prima registrazione", True)):
            log("=== STEP 1b: check_username ===")
            exists, suggestions = check_username_available(
                cfg, base, page_url, username, provider,
                session=s, token_v2=token_v2,
            )
            username_check, azione = _handle_username_check_result(
                cfg, username, exists, suggestions
            )
            if azione == "errore":
                log("[-] Check username: comportamento 'errore', blocco l'esecuzione.")
                return "errore"
            if azione == "scarta":
                log(f"[-] Account '{username}' scartato (username già in uso). "
                    "Riga RIMOSSA da dati_account.txt.")
                remove_account_line(acc)
                return "scartato"
            if username_check != username:
                log(f"[i] Username cambiato da '{username}' a '{username_check}'")
                acc = dict(acc)
                acc["username"] = username_check
                username = username_check

        log("=== STEP 1c: join1 (check1.php) ===")
        data1 = {
            "join1_recaptchav3_token": token_v3,
            "username": username,
            "userdomain": PROVIDERS[provider]["domain"],
            "password": password,
            "g-recaptcha-response": token_v2 if token_v2 else "",
        }
        r = s.post(f"{base}/check1.php", data=data1, allow_redirects=False, timeout=30)
        loc = r.headers.get("Location") or ""
        log(f"  [join1] Status: {r.status_code}, Location: {loc}")

        if r.status_code == 302 and "join2" not in loc:
            log(f"[-] Fallito join1 (Location: {loc}). "
                f"Probabile username occupato o credenziali non valide.")
            return False

        if not _curl_check_response(r, "join2", "join1"):
            log("[-] Fallito join1.")
            return False

        r2 = _curl_follow_redirect(s, base, loc)
        log(f"  Dopo redirect: {r2.url}")
        if "join2.phtml" not in r2.url:
            log("[-] Fallito join1 (non su join2).")
            return False
        log("join1 OK.")

        log("=== STEP 2: join2 (check2.php) ===")
        data2 = {
            "firstname": firstname,
            "lastname": lastname,
            "dateofbirth": dob,
            "gender": gender,
            "comune_provincia": comune,
        }
        r = s.post(f"{base}/check2.php", data=data2, allow_redirects=False, timeout=30)
        if not _curl_check_response(r, "join3", "join2"):
            log("[-] Fallito join2.")
            return False

        loc = r.headers.get("Location") or ""
        r2 = _curl_follow_redirect(s, base, loc)
        log(f"  Dopo redirect: {r2.url}")
        if "join3.phtml" not in r2.url:
            log("[-] Fallito join2 (non su join3).")
            return False
        log("join2 OK.")

        log("=== STEP 3: join3 (check3.php) ===")
        tzid, number, is_fallback = get_curl_number(cfg)
        if not number:
            log("[-] Nessun numero disponibile.")
            return False
        if is_fallback:
            log(f"[+] Numero di fallback: {number}")
        else:
            log(f"[+] Numero OnlineSim: {number} (tzid: {tzid})")

        token_v3_join3 = solve_v3(cfg, page_url, "join3")
        if not token_v3_join3:
            log("[-] Impossibile ottenere token v3 per join3.")
            if tzid:
                onlinesim_close_operation(cfg, tzid)
            return False

        pre_url_join3 = f"{base}/join3_ready_get_recaptchav3_score.php"
        r_pre3 = s.get(pre_url_join3,
                       params={"join3_ready_recaptchav3_token": token_v3_join3},
                       headers=pre_headers, timeout=30)
        log(f"Pre-validazione join3: {r_pre3.status_code} - {r_pre3.text[:200]}")

        token_v2_join3 = None
        try:
            pre_data3 = r_pre3.json()
            if pre_data3.get("success") == "show_captcha":
                log("Il server richiede il CAPTCHA visivo (v2) anche per join3.")
                token_v2_join3 = solve_v2(cfg, page_url)
                if not token_v2_join3:
                    log("[-] Impossibile ottenere token v2 per join3.")
                    if tzid:
                        onlinesim_close_operation(cfg, tzid)
                    return False
        except Exception:
            pass

        data3 = {
            "join3_recaptchav3_token": token_v3_join3,
            "emailsecondaria": number,
            "privacy": "S",
            "extprivacy": "S",
            "g-recaptcha-response": token_v2_join3 if token_v2_join3 else "",
        }
        r = s.post(f"{base}/check3.php", data=data3, allow_redirects=False, timeout=30)
        loc = r.headers.get("Location") or ""
        log(f"  Status: {r.status_code}, Location: {loc}")
        log(f"  Set-Cookie: {r.headers.get('Set-Cookie')}")
        log(f"  Cookie dopo check3: {dict(s.cookies)}")

        if "end.phtml" in loc:
            log("[***] REGISTRAZIONE COMPLETATA (OTP saltato) [***]")
            if save_cookies:
                save_auth_json_curl(s, username, cookie_dir)
            append_created_account(acc, comune, provider)
            remove_account_line(acc)
            return True

        if "join3.phtml" in loc:
            log("join3 OK, il server richiede il numero di telefono.")
        else:
            log(f"[-] Risposta inattesa da check3: {r.text[:600]}")
            if tzid:
                onlinesim_close_operation(cfg, tzid)
            return False

        # STEP 4 — challenge1
        esito = _curl_step4_challenge1(s, base, number)
        if esito == "done":
            if save_cookies:
                save_auth_json_curl(s, username, cookie_dir)
            append_created_account(acc, comune, provider)
            remove_account_line(acc)
            return True
        if esito == "error":
            if tzid:
                onlinesim_close_operation(cfg, tzid)
            return False

        if is_fallback:
            log("[!] Numero di fallback: OTP richiesto, nessun SMS leggibile, scarto account.")
            return False

        max_attempts = int(cfg.get("MAX_ATTEMPTS", 3))
        current_tzid = tzid
        current_number = number
        success = False

        for attempt in range(1, max_attempts + 1):
            log(f"--- Tentativo OTP {attempt}/{max_attempts} ---")

            sms = onlinesim_get_sms(cfg, current_tzid) if current_tzid else None
            if sms:
                log(f"[+] SMS: {sms[:200]}")
                pin = extract_pin_from_sms(sms)
                if pin:
                    log(f"[+] PIN: {pin}")
                    r = s.post(f"{base}/challenge2_check.php",
                               data={"pin_challenge": pin},
                               allow_redirects=False, timeout=30)
                    loc = r.headers.get("Location") or ""
                    log(f"  [challenge2] Status: {r.status_code}, Location: {loc}")
                    if "end.phtml" in loc:
                        log("[***] REGISTRAZIONE COMPLETATA [***]")
                        success = True
                        break
                    log("[!] PIN rifiutato.")
                else:
                    log("[-] PIN non trovato nell'SMS.")
            else:
                log("[-] Nessun SMS ricevuto.")

            if current_tzid:
                onlinesim_close_operation(cfg, current_tzid)
                current_tzid = None

            if attempt >= max_attempts:
                break

            log("[i] Richiedo un nuovo numero (solo OnlineSim)...")
            new_tzid, new_number = onlinesim_get_number(cfg)
            if not new_number:
                log("[-] OnlineSim non ha fornito nuovo numero: interrompo.")
                break
            current_tzid = new_tzid
            current_number = new_number
            log(f"[+] Nuovo numero: {current_number} (tzid: {current_tzid})")

            try:
                r2 = s.get(f"{base}/join3.phtml", allow_redirects=True, timeout=30)
                log(f"  Ritorno a join3: {r2.url}")
            except Exception as e:
                log(f"[!] Errore ritorno a join3: {e}")
                break

            if "pin_challenge" in r2.text:
                try:
                    s.post(f"{base}/challenge2_check.php",
                           data={"button_back": "", "pin_challenge": ""},
                           allow_redirects=False, timeout=30)
                except Exception:
                    pass
                try:
                    s.get(f"{base}/join3.phtml", allow_redirects=True, timeout=30)
                except Exception:
                    pass

            esito = _curl_step4_challenge1(s, base, current_number)
            if esito == "done":
                log("[***] REGISTRAZIONE COMPLETATA (OTP saltato al nuovo tentativo) [***]")
                success = True
                break
            if esito == "error":
                log("[-] challenge1 fallita con il nuovo numero.")
                continue

        if current_tzid:
            onlinesim_close_operation(cfg, current_tzid)

        if success:
            if save_cookies:
                save_auth_json_curl(s, username, cookie_dir)
            append_created_account(acc, comune, provider)
            remove_account_line(acc)
            return True

        log("[-] Registrazione fallita: tentativi esauriti.")
        return False

    except Exception as e:
        log(f"[-] Eccezione account {username} (curl): {e}")
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def run_account(cfg, acc, comuni, save_cookies, cookie_dir):
    metodo = str(cfg.get("METODO", "browser")).lower().strip()
    if metodo == "curl":
        return run_account_curl(cfg, acc, comuni, save_cookies, cookie_dir)
    return run_account_browser(cfg, acc, comuni, save_cookies, cookie_dir)

def check_dependencies(cfg):
    metodo = str(cfg.get("METODO", "browser")).lower().strip()
    ok = True

    if metodo == "browser":
        if not CLOAKBROWSER_AVAILABLE:
            log("[-] METODO=browser richiede 'cloakbrowser' ma NON è installato.")
            log("[-] Installa con:  pip install cloakbrowser")
            ok = False
    elif metodo == "curl":
        if not CURL_CFFI_AVAILABLE:
            log("[-] METODO=curl richiede 'curl_cffi' ma NON è installato.")
            log("[-] Installa con:  pip install curl_cffi")
            ok = False
        if not PLAYWRIGHT_AVAILABLE:
            log("[-] METODO=curl richiede 'playwright' (per iubenda) ma NON è installato.")
            log("[-] Installa con:  pip install playwright  &&  playwright install chromium")
            ok = False
    else:
        log(f"[-] METODO '{metodo}' non riconosciuto. Valori ammessi: 'browser', 'curl'.")
        ok = False

    return ok



def main():
    global WEBSHARE_API_URL, WEBSHARE_CACHE_TIME

    ensure_default_files()
    update_config_file()
    print_logo()
    cfg = parse_config()

    metodo = str(cfg.get("METODO", "browser")).lower().strip()
    log(f"[i] METODO selezionato: {metodo}")

    if not check_dependencies(cfg):
        log("[-] Dipendenze mancanti o METODO non valido: esecuzione bloccata.")
        return

    if str(cfg.get("ONLINESIM_API_KEY", "")).startswith("INCOLLA"):
        log("[-] Configura ONLINESIM_API_KEY in config.txt")
        return

    if metodo == "curl":
        if str(cfg.get("2CAPTCHA_API_KEY", "")).startswith("INCOLLA"):
            log("[-] Configura 2CAPTCHA_API_KEY in config.txt (necessaria per METODO=curl)")
            return
        use_only_fb = bool(cfg.get("Usare solo fallback", False))
        fb = str(cfg.get("Numero fallback curl", "")).strip()
        if use_only_fb:
            if fb:
                log(f"[i] 'Usare solo fallback = Si': salto OnlineSim, uso {fb}")
            else:
                log("[-] 'Usare solo fallback = Si' ma 'Numero fallback curl' è vuoto: blocco.")
                return
        elif bool(cfg.get("Fallback numero curl", False)):
            if fb:
                log(f"[i] Fallback numero curl ATTIVO: {fb}")
            else:
                log("[!] 'Fallback numero curl = Si' ma 'Numero fallback curl' è vuoto.")

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
                if ok is True:
                    log(f"[+] Account {acc['username']} completato.")
                elif ok == "scartato":
                    log(f"[i] Account {acc['username']} scartato (riga rimossa da dati_account.txt).")
                elif ok == "errore":
                    log(f"[-] Account {acc['username']}: comportamento 'errore'. "
                        f"Interrompo l'esecuzione. Riga lasciata in dati_account.txt.")
                    try:
                        input("\n[INVIO] per chiudere...")
                    except (EOFError, KeyboardInterrupt):
                        pass
                    return
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