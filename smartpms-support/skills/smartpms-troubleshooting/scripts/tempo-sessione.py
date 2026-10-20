#!/usr/bin/env python3
"""Calcola quanto tempo Claude ha lavorato a un ticket in questa sessione, dal transcript di Claude Code.

Uso:
  tempo-sessione.py --ticket 126257                 # dal turno in cui compare il ticket fino ad ora
  tempo-sessione.py --since 2026-10-20T12:28:28Z    # da un istante preciso (es. "a=" di un calcolo precedente)
  tempo-sessione.py --ticket 126257 --until 2026-10-20T13:10:00Z   # fino a quando si è passati a un altro ticket
  tempo-sessione.py --ticket 126257 --list          # anche il dettaglio per turno

Conta solo il tempo attivo: la somma degli intervalli tra un evento e il successivo del transcript
(ragionamento, chiamate ai tool, risposte), esclusi
  - l'attesa tra la fine di un turno e il messaggio successivo dell'agente;
  - le pause più lunghe di --max-gap secondi (default 300) dentro un turno (permessi, domande in attesa).
Il turno in corso conta fino ad ora.

Output: secondi=, minuti=, turni=, da=, a= (UTC). "a=" si passa come --since se si torna sullo stesso ticket
dopo aver già scritto il tempo, così nulla viene contato due volte.
Sessione: CLAUDE_CODE_SESSION_ID dall'ambiente, oppure --session. Non scrive nulla.
"""

import argparse
import glob
import json
import os
import re
import sys
from datetime import datetime, timezone


def parse_ts(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def fmt(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def is_prompt(entry):
    """Messaggio dell'agente (inizio turno), non un risultato di tool né un messaggio di sistema."""
    if entry.get("type") != "user" or entry.get("isMeta"):
        return False
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        return not any(isinstance(c, dict) and c.get("type") == "tool_result" for c in content)
    return isinstance(content, str)


def prompt_text(entry):
    content = (entry.get("message") or {}).get("content")
    if isinstance(content, list):
        content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return " ".join(str(content).split())[:80]


def main():
    ap = argparse.ArgumentParser(description="Tempo attivo di Claude su un ticket in questa sessione")
    ap.add_argument("--ticket", help="numero del ticket Zendesk: si parte dal turno in cui compare per la prima volta")
    ap.add_argument("--since", help="inizio (ISO 8601, UTC); prevale su --ticket")
    ap.add_argument("--until", help="fine (ISO 8601, UTC); default: ora")
    ap.add_argument("--session", default=os.environ.get("CLAUDE_CODE_SESSION_ID"))
    ap.add_argument("--max-gap", type=int, default=300, help="pause più lunghe di N secondi non contano")
    ap.add_argument("--list", action="store_true", help="mostra anche il dettaglio per turno")
    args = ap.parse_args()

    if not args.ticket and not args.since:
        sys.exit("ERRORE: serve --ticket oppure --since")
    if not args.session:
        sys.exit("ERRORE: CLAUDE_CODE_SESSION_ID non impostato: passa --session <id>")
    files = glob.glob(os.path.expanduser(f"~/.claude/projects/*/{args.session}.jsonl"))
    if not files:
        sys.exit(f"ERRORE: transcript della sessione {args.session} non trovato in ~/.claude/projects")

    entries = []
    with open(files[0], encoding="utf-8") as fh:
        for line in fh:
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if entry.get("type") in ("user", "assistant") and entry.get("timestamp") and not entry.get("isSidechain"):
                entries.append((parse_ts(entry["timestamp"]), entry, line))
    entries.sort(key=lambda e: e[0])
    if not entries:
        sys.exit("ERRORE: transcript vuoto")

    now = datetime.now(timezone.utc)
    until = parse_ts(args.until) if args.until else now

    if args.since:
        since = parse_ts(args.since)
    else:
        pattern = re.compile(rf"(?<!\d){re.escape(args.ticket)}(?!\d)")
        # Solo messaggi dell'agente e risultati dei tool: le chiamate di Claude (compresa questa) non contano.
        first = next((i for i, (_, entry, line) in enumerate(entries)
                      if entry.get("type") == "user" and pattern.search(line)), None)
        if first is None:
            sys.exit(f"ERRORE: il ticket {args.ticket} non compare nella sessione: passa --since")
        start = next((i for i in range(first, -1, -1) if is_prompt(entries[i][1])), first)
        since = entries[start][0]

    window = [(ts, entry) for ts, entry, _ in entries if since <= ts <= until]
    if not window:
        sys.exit("ERRORE: nessun evento della sessione nell'intervallo indicato")
    if not args.until:
        window.append((now, {"type": "now"}))

    turns = []  # [inizio, secondi attivi, testo del messaggio]
    for i, (ts, entry) in enumerate(window):
        if i == 0 or is_prompt(entry):
            turns.append([ts, 0.0, prompt_text(entry) if is_prompt(entry) else "(turno già iniziato)"])
            continue
        gap = (ts - window[i - 1][0]).total_seconds()
        if gap <= args.max_gap:
            turns[-1][1] += gap

    total = round(sum(t[1] for t in turns))
    if args.list:
        for start, secs, text in turns:
            print(f"{fmt(start)}  {round(secs):>5} s  {text}")
    print(f"secondi={total}")
    print(f"minuti={round(total / 60)}")
    print(f"turni={len(turns)}")
    print(f"da={fmt(since)}")
    print(f"a={fmt(until)}")


if __name__ == "__main__":
    main()
