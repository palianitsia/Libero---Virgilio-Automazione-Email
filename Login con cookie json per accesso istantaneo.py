# Usa questo script per login istantaneo con cookie gia esistenti, salvati dopo registrazioni ad es per confermare tuo acc bidone e ricevere codice di conferma

# Per un funzionamento corretto installa se non hai gia fatto le librerie con prossimo commando da terminale || pip install playwright || di seguito || playwright install chromium oppure playwright install ||


import asyncio
import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from playwright.async_api import async_playwright


def seleziona_file_cookie() -> str | None:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)  # porta la finestra in primo piano

    percorso = filedialog.askopenfilename(
        title="Seleziona il file dei cookie",
        initialdir=os.getcwd(),
        filetypes=[
            ("File JSON cookie", "*.json"),
            ("Tutti i file", "*.*"),
        ],
    )

    root.destroy()
    return percorso or None


def chiedi_url_login_manuale() -> str:
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    from tkinter import simpledialog
    url = simpledialog.askstring(
        "Login manuale",
        "Inserisci l'URL della webmail per il login manuale\n"
        "(es. https://mail1.virgilio.it):",
        initialvalue="https://mail1.virgilio.it",
        parent=root,
    )
    root.destroy()

    if not url:
        url = "https://mail1.virgilio.it"
    if not url.startswith("http"):
        url = "https://" + url
    return url


def rileva_target_da_cookie(auth_file: str) -> str:
    with open(auth_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    cookies = data.get("cookies", [])
    if not cookies:
        raise ValueError(f"Nessun cookie trovato in '{auth_file}'.")

    for c in cookies:
        domain = (c.get("domain") or "").lstrip(".").lower()
        if domain.startswith("mail1.") or domain.startswith("mail."):
            return f"https://{domain}"

    for origin in data.get("origins", []):
        url = (origin.get("origin") or "").strip()
        if url:
            host = url.split("://", 1)[-1].split("/", 1)[0].lower()
            if host.startswith("mail1.") or host.startswith("mail."):
                return url

    escludi = (
        "google.com", "doubleclick.net", "bing.com", "clarity.ms",
        "criteo.com", "rubiconproject.com", "mgid.com", "insurads.com",
        "id5-sync.com", "nexx360.io", "imrworldwide.com", "prmutv.co",
        "wt-eu02.net", "evnt.iol.it", "iolam.it",
    )

    conteggio = {}
    for c in cookies:
        domain = (c.get("domain") or "").lstrip(".").lower()
        if not domain:
            continue
        if any(domain == e or domain.endswith("." + e) for e in escludi):
            continue
        conteggio[domain] = conteggio.get(domain, 0) + 1

    if not conteggio:
        raise ValueError(
            f"Impossibile dedurre un URL target dai cookie in '{auth_file}'."
        )

    dominio_top = max(conteggio, key=conteggio.get)
    return f"https://{dominio_top}"


async def login_manuale(auth_file: str, target_url: str):
    print("=" * 60)
    print(f"👉 Verrà aperto il browser su: {target_url}")
    print("   Effettua il LOGIN MANUALE.")
    print("   Quando sei dentro la webmail, torna qui e premi INVIO.")
    print("=" * 60)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(target_url)

        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None, input,
            "\n✅ Login completato? Premi INVIO per salvare lo stato... "
        )

        await context.storage_state(path=auth_file)
        print(f"💾 Stato salvato in: {auth_file}")
        await browser.close()


async def main():
    auth_file = seleziona_file_cookie()

    if not auth_file:
        print("❌ Nessun file selezionato. Uscita.")
        return

    print(f"✅ File cookie selezionato: {auth_file}")

    if os.path.exists(auth_file) and os.path.getsize(auth_file) > 0:
        try:
            target_url = rileva_target_da_cookie(auth_file)
            print(f"🎯 URL target rilevato dai cookie: {target_url}")
        except Exception as e:
            print(f"⚠️  Impossibile dedurre l'URL dai cookie: {e}")
            target_url = chiedi_url_login_manuale()
    else:
        target_url = chiedi_url_login_manuale()
        await login_manuale(auth_file, target_url)

    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    context = await browser.new_context(storage_state=auth_file)

    page = await context.new_page()
    await page.goto(target_url)

    print(f"✅ Browser aperto con sessione da: {auth_file}")
    print(f"🎯 URL: {target_url}")
    print("🔄 Naviga liberamente. Chiudi il browser quando hai finito.")
    print("=" * 60)

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Chiusura in corso...")

    await browser.close()
    await playwright.stop()


if __name__ == "__main__":
    asyncio.run(main())
