# Proporre modifiche al plugin SmartPMS Support

Chiunque nel team può proporre una regola nuova o una correzione. La proposta diventa una **pull request**: Joseph la rivede e, se la approva, arriva a tutti al prossimo riavvio dell'app. Nessuno modifica direttamente la versione del team.

## Dove va cosa

Tutti i file sono in `smartpms-support/skills/smartpms-troubleshooting/`:

| File | Cosa contiene |
|---|---|
| `references/team-rules.md` | Regole e procedure del team: risposte, stati, campi CB, escalation L2, Jira, feature request, politiche verso il cliente |
| `references/product-knowledge.md` | Fatti di prodotto confermati (comportamenti del PMS, del channel manager, di SmartPay…) |
| `SKILL.md` | Il metodo di indagine: passi, tool da usare, insidie note |

Scrivi in italiano, nello stile del testo che c'è già, nella sezione giusta.

## Come proporre una modifica (dal browser, senza installare niente)

1. Serve un account GitHub (gratuito).
2. Apri il file su GitHub, per esempio [team-rules.md](smartpms-support/skills/smartpms-troubleshooting/references/team-rules.md), e clicca la matita ✏️ in alto a destra.
3. GitHub crea una tua copia del repository: modifica il testo.
4. Clicca **Commit changes…**, scrivi un titolo breve (es. "team-rules: rimborsi SmartPay sopra 30 giorni") e poi **Propose changes**.
5. Nella pagina successiva clicca **Create pull request** e compila il modulo: la regola, un ticket di esempio, perché vale per tutto il team.

Joseph riceve la notifica, può commentare, chiedere modifiche, approvarla o chiuderla.

Se preferisci non usare GitHub, scrivi a Joseph su Slack (thread in #quelli-dei-ticket o DM) con le stesse tre informazioni.

## Cosa non mettere mai

Il repository è **pubblico**:

- niente token, password, chiavi API (il token Slack resta in 1Password);
- niente dati personali di clienti o ospiti (nomi, email, telefoni, documenti);
- per gli esempi usa il numero del ticket o l'ID della prenotazione, non il nome del cliente.

## Perché non modificare i file sul tuo Mac

La copia installata del plugin viene sovrascritta a ogni aggiornamento: le modifiche locali si perdono e non arrivano agli altri. Passa sempre da una pull request.
