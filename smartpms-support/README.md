# SmartPMS Support

Plugin del team Support SmartPMS per Claude (app desktop, tab Code).

## Cosa contiene

| Skill | A cosa serve |
|---|---|
| `smartpms-support:smartpms-troubleshooting` | Indagine su un ticket o un problema cliente: ticket → cliente → log → dati → codice → doc, con bozza di risposta, escalation L2, feature request e bozza Payload secondo le regole del team. Parte da sola quando descrivi un problema di un cliente o citi un ticket. |

Le regole del team (stati, campi CB, escalation, feature request, politiche verso il cliente) sono in `skills/smartpms-troubleshooting/references/team-rules.md`; i fatti di prodotto confermati in `references/product-knowledge.md`.

## Setup (una volta sola)

1. **Installa il plugin** con aggiornamento automatico: aggiungi a `~/.claude/settings.json` il blocco `extraKnownMarketplaces` + `enabledPlugins` che trovi nella sezione A di [ADMIN-SETUP.md](../ADMIN-SETUP.md) (repo pubblico `wbgne/smartpms-support-plugin`, non serve un account GitHub), poi chiudi e riapri l'app. In alternativa, da un terminale `claude`: `/plugin install smartpms-support --marketplace wbgne/smartpms-support-plugin`.
2. **Attiva i connettori** su claude.ai → Impostazioni → Connettori, accedendo con **il tuo** account:
   - Composio con l'app **Zendesk** (il tuo utente Zendesk)
   - Smarty MCP (dati live SmartPMS)
   - Smartness MCP Gateway (codice e ticket analizzati)
   - Payload MCP (documentazione)
   - Atlassian (Jira, progetto CIAOB: ricerca bug esistenti e nuovi bug per gli sviluppatori)
   - HubSpot (task e note, solo in inglese), se lo usi
3. **Modello**: nel selettore del modello dell'app imposta come predefiniti **Opus 5.5** ed effort **Medium**.
4. **Token Slack** per le feature request: è in **1Password**, vault **Shared**, voce `support-copilot - Slack`, campo `credential` (mai in chat, nei ticket o nel repo; se non vedi la voce, chiedila al responsabile del supporto). Copialo da lì e salvalo con questo comando in un terminale: lo chiede senza mostrarlo e non resta nella cronologia.
   ```bash
   mkdir -p ~/.config/smartpms && read -rs "T?Token Slack: " && (umask 077; printf 'SLACK_BOT_TOKEN=%s\n' "$T" > ~/.config/smartpms/slack.env) && unset T && echo salvato
   ```
   Se l'organizzazione lo distribuisce già nelle impostazioni gestite, puoi saltare questo passo. Verifica (stampa solo sì/no, mai il token):
   ```bash
   { [ -n "$SLACK_BOT_TOKEN" ] || [ -f ~/.config/smartpms/slack.env ]; } && echo "token presente" || echo "token mancante"
   ```

## Come si lavora

- Risposte ai clienti ed escalation L2 si inviano solo dopo il tuo ok. Campi CB e feature request su Slack non richiedono conferma (regola del team).
