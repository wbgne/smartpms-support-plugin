#!/usr/bin/env python3
"""Aggiunge una riga al foglio "Pluno Responses to Fix" (tab "Pluno Fixes") per un errore del virtual agent.

Uso:
  python3 pluno-fix.py --opzioni
      stampa le opzioni dei menu Brand e Reporter (per scegliere i valori esatti)
  python3 pluno-fix.py --ticket 129686 --reporter "Marco Chi." [--brand Smartpms] [--dry-run] "Expected outcome"

Scrive come il service account copilot-sheets, impersonato con gcloud (nessuna chiave): serve gcloud installato,
`gcloud auth login` fatto con l'account @smartpricing.it e l'appartenenza al gruppo cs-team@smartpricing.it.
Una riga per ticket: se il link del ticket è già nel foglio si ferma senza scrivere.
In colonna A scrive il mese (es. "OTTOBRE 2026") solo se è la prima riga del mese. Status resta vuoto.
"""

import argparse
import datetime
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

SHEET_ID = os.environ.get("PLUNO_SHEET_ID", "1xAFFNCZ0IbpBQ30gey31BMYrTjW-v1aGS0jqsW7jBxY")
TAB = "Pluno Fixes"
SA = "copilot-sheets@smartness-internal-tools.iam.gserviceaccount.com"
API = f"https://sheets.googleapis.com/v4/spreadsheets/{SHEET_ID}"
MESI = ["GENNAIO", "FEBBRAIO", "MARZO", "APRILE", "MAGGIO", "GIUGNO",
        "LUGLIO", "AGOSTO", "SETTEMBRE", "OTTOBRE", "NOVEMBRE", "DICEMBRE"]


def fail(msg):
    print(f"ERRORE: {msg}", file=sys.stderr)
    sys.exit(1)


def token():
    try:
        out = subprocess.run(
            ["gcloud", "auth", "print-access-token", f"--impersonate-service-account={SA}",
             "--scopes=https://www.googleapis.com/auth/spreadsheets"],
            capture_output=True, text=True)
    except FileNotFoundError:
        fail("gcloud non è installato (vedi il README del plugin, setup)")
    if out.returncode != 0:
        err = out.stderr
        if "Reauthentication" in err or "gcloud auth login" in err:
            fail("login gcloud scaduto: esegui `gcloud auth login` in un terminale e riprova")
        if "PERMISSION_DENIED" in err or "getAccessToken" in err:
            fail(f"il tuo account non può impersonare {SA}: serve l'appartenenza a cs-team@smartpricing.it")
        fail(err.strip().splitlines()[-1] if err.strip() else "gcloud non ha restituito un token")
    return out.stdout.strip()


def call(tok, method, url, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {tok}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")
        if e.code == 403:
            fail(f"il service account non ha accesso al foglio (va condiviso con {SA} come Editor): {detail}")
        fail(f"Sheets API {e.code}: {detail}")


def rng(a1):
    return urllib.parse.quote(f"'{TAB}'!{a1}", safe="")


def opzioni(tok):
    res = call(tok, "GET", f"{API}?ranges={rng('B2:C200')}"
               "&fields=sheets.data.rowData.values.dataValidation")
    seen = {"Brand": [], "Reporter": []}
    for row in res["sheets"][0]["data"][0].get("rowData", []):
        for col, cell in zip(("Brand", "Reporter"), row.get("values", [])):
            cond = cell.get("dataValidation", {}).get("condition", {})
            for v in cond.get("values", []):
                val = v.get("userEnteredValue")
                if val and val not in seen[col]:
                    seen[col].append(val)
    for col, vals in seen.items():
        print(f"{col}: {', '.join(vals) if vals else '(nessun menu)'}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--opzioni", action="store_true")
    p.add_argument("--ticket")
    p.add_argument("--reporter")
    p.add_argument("--brand", default="Smartpms")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("outcome", nargs="?")
    a = p.parse_args()

    tok = token()
    if a.opzioni:
        opzioni(tok)
        return
    if not (a.ticket and a.reporter and a.outcome):
        fail("servono --ticket, --reporter e il testo dell'Expected Outcome")
    if not a.ticket.isdigit():
        fail("--ticket deve essere il numero del ticket Zendesk")

    rows = call(tok, "GET", f"{API}/values/{rng('A1:F2000')}").get("values", [])
    link_re = re.compile(rf"/tickets/{a.ticket}(?!\d)")
    last, mese_corrente = 1, ""
    for i, row in enumerate(rows[1:], start=2):
        row = row + [""] * (6 - len(row))
        if row[0].strip():
            mese_corrente = row[0].strip().upper()
        if any(c.strip() for c in row[1:]):
            last = i
        if link_re.search(row[3]):
            fail(f"il ticket {a.ticket} è già nel foglio (riga {i}): nessuna scrittura")

    oggi = datetime.date.today()
    mese = f"{MESI[oggi.month - 1]} {oggi.year}"
    outcome = a.outcome.strip()
    if outcome[:1] in "=+-@":
        outcome = "'" + outcome  # testo, non formula
    riga = [mese if mese != mese_corrente else "", a.brand, a.reporter,
            f"https://smartness.zendesk.com/agent/tickets/{a.ticket}", outcome, ""]
    n = last + 1

    if a.dry_run:
        print(f"Riga {n} (non scritta): " + json.dumps(riga, ensure_ascii=False))
        return
    if last > 1:
        # Le righe nuove non hanno i menu Brand/Reporter: si copiano menu e formato dall'ultima riga compilata.
        meta = call(tok, "GET", f"{API}?fields=sheets.properties(sheetId,title)")
        sheet_id = next(s["properties"]["sheetId"] for s in meta["sheets"] if s["properties"]["title"] == TAB)
        src = {"sheetId": sheet_id, "startRowIndex": last - 1, "endRowIndex": last, "startColumnIndex": 0, "endColumnIndex": 6}
        dst = dict(src, startRowIndex=n - 1, endRowIndex=n)
        call(tok, "POST", f"{API}:batchUpdate", {"requests": [
            {"copyPaste": {"source": src, "destination": dst, "pasteType": t}}
            for t in ("PASTE_FORMAT", "PASTE_DATA_VALIDATION")]})
    call(tok, "PUT", f"{API}/values/{rng(f'A{n}:F{n}')}?valueInputOption=USER_ENTERED",
         {"values": [riga]})
    check = call(tok, "GET", f"{API}/values/{rng(f'A{n}:F{n}')}").get("values", [[]])[0]
    print(f"OK riga {n}: " + json.dumps(check, ensure_ascii=False))


if __name__ == "__main__":
    main()
