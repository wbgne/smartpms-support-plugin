---
name: proporre-regola
description: Proporre una regola nuova o una correzione per il team Support SmartPMS. Usala quando l'utente dice "aggiungi questa regola", "questa regola è sbagliata", "aggiungi al plugin…", oppure vuole registrare un fatto di prodotto (come si comporta il PMS, un caso noto, un bug aperto). Le regole del team diventano una pull request sul plugin smartpms-support; i fatti di prodotto vanno in Payload.
---

# Proporre una regola o un fatto di prodotto

Quando l'agente dice "aggiungi questa regola", "questa regola è sbagliata" o durante un caso emerge qualcosa che vale per tutto il team, la modifica si propone con una **pull request** sul repository pubblico `wbgne/smartpms-support-plugin`; la approva il responsabile del supporto.

- **Non modificare mai i file installati del plugin** (`~/.claude/plugins/`): vengono sovrascritti al prossimo aggiornamento e non arrivano agli altri.
- Se la cartella di lavoro contiene già `plugins/smartpms-support` con un `CLAUDE.md` che spiega come pubblicare (è la postazione del responsabile), segui quelle istruzioni invece di questa procedura.
- Le regole personali (preferenze del singolo agente, liste legate a un solo ticket) non vanno nel plugin.
- Se è un **fatto di prodotto** (come si comporta il PMS, il channel manager o SmartPay, un caso noto, un bug Jira aperto) non aprire una pull request: va in **Payload**. Leggi prima la sezione "Aggiornamenti Payload" di `${CLAUDE_SKILL_DIR}/../smartpms-troubleshooting/references/azioni.md`, poi `getGuidelines` del tipo giusto, `searchDocs` / `checkDuplicates`, e proponi all'agente la scrittura (documento, testo, fonte, ticket, certezza e se va online subito). Scrivi solo dopo un sì.

Procedura:
1. Scegli file e sezione, tutti in `smartpms-support/skills/smartpms-troubleshooting/`: regole sempre valide (risposte, stati, campi CB, chi se ne occupa, politiche) → `references/team-rules.md`; procedure per agire (side conversation, Jira, feature request, Payload, HubSpot) → `references/azioni.md`; metodo di indagine e insidie dei tool → `SKILL.md`. I **fatti di prodotto non vanno nel plugin** (vedi sopra). Scrivi in italiano, nello stile del testo vicino. Mai token, password o dati personali di clienti/ospiti: il repository e le pull request sono pubblici (negli esempi usa il numero del ticket).
2. Controlla `gh auth status`. Se `gh` non è installato o non è collegato, di' all'agente di eseguire in un terminale `gh auth login` (GitHub.com → HTTPS → login dal browser; il login lo fa lui, non tu). Se non ha o non vuole un account GitHub, prepara invece il testo da mandare al responsabile del supporto su Slack (regola, ticket di esempio, perché vale per tutti) e fermati qui.
3. Lavora in una cartella temporanea, partendo sempre dall'ultima versione del team:
   ```bash
   D=$(mktemp -d) && cd "$D" && gh repo fork wbgne/smartpms-support-plugin --clone --remote && cd smartpms-support-plugin
   git fetch upstream && git checkout -b regola-<breve-descrizione> upstream/main
   ```
4. Applica la modifica e mostra all'agente il diff (`git diff`) e il testo della pull request. **Chiedi conferma prima di aprirla**: è pubblica.
5. Dopo il sì:
   ```bash
   git add -A && git commit -m "team-rules: <cosa cambia>" && git push -u origin HEAD
   gh pr create --repo wbgne/smartpms-support-plugin --title "<titolo breve>" --body-file <file>
   ```
   Il corpo segue il modulo del repository: `## Regola o correzione`, `## Ticket di esempio`, `## Perché vale per tutto il team`.
6. Dai all'agente il link della pull request: la modifica arriva a tutti solo dopo l'approvazione, al riavvio dell'app.
