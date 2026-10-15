# SmartPMS Support

Plugin del team Support SmartPMS per Claude (app desktop, tab Code).

## Cosa contiene

| Skill | A cosa serve |
|---|---|
| `smartpms-support:smartpms-troubleshooting` | Indagine su un ticket o un problema cliente: ticket → cliente → log → dati → codice → doc, con bozza di risposta, escalation L2, feature request e bozza Payload secondo le regole del team. Parte da sola quando descrivi un problema di un cliente o citi un ticket. |

Le regole del team (stati, campi CB, escalation, feature request, politiche verso il cliente) sono in `skills/smartpms-troubleshooting/references/team-rules.md`; i fatti di prodotto confermati in `references/product-knowledge.md`.

## Setup (una volta sola)

1. **Installa il plugin** dal catalogo plugin dell'organizzazione (di solito è già installato in automatico). Se non lo vedi, da un terminale `claude`: `/plugin install smartpms-support --marketplace smartpricing/smartpms-support-plugin`.
2. **Attiva i connettori** su claude.ai → Impostazioni → Connettori, accedendo con **il tuo** account:
   - Composio con l'app **Zendesk** (il tuo utente Zendesk)
   - Smarty MCP (dati live SmartPMS)
   - Smartness MCP Gateway (codice e ticket analizzati)
   - Payload MCP (documentazione)
   - Atlassian (Jira, progetto CIAOB: ricerca bug esistenti e nuovi bug per gli sviluppatori)
   - HubSpot (task e note, solo in inglese), se lo usi
3. **Modello**: nel selettore del modello dell'app imposta come predefiniti **Opus 5.5** ed effort **Medium**.
5. **Token Slack** per le feature request: chiedi il token del bot del team al responsabile del supporto e salvalo così (mai in chat):
   ```bash
   mkdir -p ~/.config/smartpms && printf 'SLACK_BOT_TOKEN=%s\n' 'xoxb-…' > ~/.config/smartpms/slack.env && chmod 600 ~/.config/smartpms/slack.env
   ```

## Come si lavora

- Risposte ai clienti ed escalation L2 si inviano solo dopo il tuo ok. Campi CB e feature request su Slack non richiedono conferma (regola del team).
