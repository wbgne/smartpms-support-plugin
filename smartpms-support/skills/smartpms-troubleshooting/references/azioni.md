# Azioni del team Support SmartPMS

Regole di dettaglio per agire fuori dalla risposta al cliente. **Leggi questo file prima di** creare una side conversation (L2, Finance, Activations, Smartpricing, Octorate), aprire un'issue Jira, pubblicare una feature request o scrivere a un collega su Slack, scrivere in Payload o su HubSpot, o gestire uno dei casi Zendesk particolari in fondo. Le regole sempre valide sono in `team-rules.md`.

## Escalation L2 = side conversation

- Sempre come **side conversation nello stesso ticket Zendesk**, verso il gruppo **Smartpms L2 Support** (`support_group_id: 16756021180700`), **senza assegnatario**. Non Slack, non nota interna.
- Tool: `ZENDESK_CREATE_SIDE_CONVERSATION` con `to: [{support_group_id: 16756021180700}]` (in Composio si trova solo con `search_strategy: "tool_search"`).
- **Una side conversation per ogni problematica**: mai più bug nella stessa escalation, anche se arrivano dallo stesso ticket.
- Passa **sempre `html_body`** formattato (`<h3>`/`<strong>` per i titoli, `<ul>/<ol>`, `<code>` per ID e batch). Con il solo `body` testuale Zendesk perde a capo ed elenchi. Il messaggio non è modificabile dopo l'invio: mostra il testo all'agente e chiedi conferma prima di crearla.
- Contenuto: ID interni delle prenotazioni, cronologia in UTC, batch, cosa è stato verificato e cosa si chiede di verificare.
- Per rispondere nella stessa side conversation (nessun tool Composio dedicato): `proxy_execute` in COMPOSIO_REMOTE_WORKBENCH, POST `https://smartness.zendesk.com/api/v2/tickets/{ticket}/side_conversations/{id}/reply` con `{"message": {"to": [{"support_group_id": 16756021180700}], "body": ..., "html_body": ...}}` (`to` è obbligatorio). In alternativa, un commento pubblico sul ticket figlio (`ZENDESK_REPLY_ZENDESK_TICKET` con l'ID del figlio) entra nella side conversation come `reply` verso il gruppo L2 (verificato sul ticket 121062), ma Zendesk aggiunge la firma dell'agente: preferisci la POST. In entrambi i casi poi rimetti il padre in Pending Internal e verificalo.
- Dopo l'escalation il ticket va in **Pending Internal** (`custom_status_id: 15294614941468`). Vale anche per le side conversation verso Finance Team e Activations Team. Dopo ogni risposta pubblica su un ticket in escalation, reimposta Pending Internal e verificalo.
- Il ticket figlio che Zendesk crea per la side conversation risulta assegnato al Virtual Agent e al gruppo di supporto standard: va bene così, non riassegnarlo e non segnalarlo.
- **Side conversation aperta per errore** (es. il bug era già su Jira): chiudila con PUT `/api/v2/tickets/{padre}/side_conversations/{id}` `{"side_conversation":{"state":"closed"}}`, poi metti in Solved il figlio (assegnatario + Category/Topic/Ticket Type/Resolution Cause/Opened by) e rimetti il padre in Pending Internal: chiudere la side conversation lo riporta in Aperto.

### Brand della side conversation

- Il brand dell'escalation è **il brand del ticket padre**. Brand Zendesk: Smartpms `16653484213276`, Smartpricing `13500829701020` (default), Smartchat `21097520438172`, Smartconnect `27513874501020`, Smartsite `26399265894428`.
- Leggi `brand_id` del padre prima di creare la side conversation. Dopo la creazione trova il figlio (search `via:side_conversation`, `external_id` = `zen:side_conversation:<uuid>:ticket:<padre>`) e fai una GET. Se il `brand_id` è diverso da quello del padre, correggilo con PUT `/api/v2/tickets/{figlio}.json` `{"ticket":{"brand_id":...}}`. Il figlio eredita il brand alla creazione, ma i trigger "CiaoBooking re-alignment" e "CiaoBooking re-alignment (copia)" possono cambiarlo subito dopo. Il controllo va fatto su ogni side conversation (L2, L1, Finance).
- **Eccezione: le side conversation verso l'Activations Team restano sempre su Smartpricing**, anche se il padre è Smartpms, perché le attivazioni sono di Smartpricing.
- Quando correggi il brand, il trigger "[Brand for HS]" allinea da solo il campo custom `23829217684892`: va bene così.

### Temi Smartpricing su un ticket Smartpms

- Se il cliente solleva un tema **Smartpricing** (es. competitor disattivati), la parte Smartpms si risponde nel ticket e quella Smartpricing va in **side conversation al gruppo "Smartpricing L1 Support"** (`support_group_id: 17896873237916`), con **il cliente come requester** del ticket figlio, così L1 Smartpricing gli risponde direttamente.
- Brand del figlio = **Smartpricing** (`13500829701020`), eccezione alla regola "brand del padre". Alla creazione i trigger spostano il figlio su brand Smartpms e gruppo Smartpms L1 (`16743124489628`); se cambi solo il `brand_id` un trigger lo riporta indietro. Funziona solo mandando **`brand_id` 13500829701020 e `group_id` 17896873237916 nella stessa update**.
- Requester: `data: {requester_id: <cliente>}` (l'organizzazione si allinea da sola). Il figlio è privato: al cliente non arriva nulla finché L1 non risponde in pubblico. Verifica con GET `/api/v2/tickets/{figlio}/audits.json` (la ricerca Zendesk restituisce dati in ritardo). Il padre va in Pending Internal.

### Attivazione HRS per strutture su Octorate

- Non si fa al telefono: side conversation email a **reseller@octorate.com** dal ticket, con ID Octorate della struttura e HRS hotel ID. Poi il ticket va in Pending Internal.
- Il cliente deve chiedere lui a HRS la connessione al channel manager Octorate: è l'unico punto in cui al cliente si nomina Octorate. Per il resto resta vago ("the activation has to be requested through our channel connection, we take care of it"). La mappatura camere/tariffe HRS la fa il Support dopo l'attivazione. Guida Payload: `ota-hrs-octorate-attivazione`.

### Prenotazioni o cancellazioni OTA mai arrivate a Octorate

- Se in Octorate (`read_octorate` → `findReservations` con `refer` = codice OTA) la prenotazione non ha ricevuto la modifica o la cancellazione fatta sul portale (es. cancellata su Expedia a giugno, in Octorate `CONFIRMED` fino a ottobre), il PMS non ha perso nulla: **niente L2**. Si apre una **side conversation email a reseller@octorate.com** dal ticket.
- Contenuto: alloggio Octorate, hotel ID del portale, ID prenotazione Octorate e codice OTA, data della modifica sul portale, `status`/`cancelledBy`/`cancelledTime` letti in Octorate, orario di arrivo nel PMS (UTC). Chiedi se il portale ha inviato la modifica e cosa ha generato lo stato attuale. `html_body` formattato come per L2.
- Il ticket va in **Pending Internal**. Al cliente non si nomina Octorate ("il collegamento con Expedia", "il fornitore del collegamento"); gli si dice se la disponibilità è già riallineata e gli si chiede, se serve, chi ha fatto la modifica sul portale.

## Bug per gli sviluppatori = Jira CIAOB

- La side conversation serve per passare da L1 a L2. Quando un ticket è già in L2 (es. il figlio di una side conversation) e serve la correzione degli sviluppatori, si apre un **Bug** in Jira, progetto **CIAOB** ("Smartpms", issue type Bug id `10004`), con il connettore Atlassian (sito smartpricing-it.atlassian.net, cloudId `75d58419-ef23-4a75-a2ce-72550efcdca4`). Obbligatorio solo il summary; priorità e label (`backend`, `mychannel`…) facoltative.
- Un difetto trovato nel codice senza un problema aperto del cliente può andare direttamente su Jira se l'agente lo chiede.
- Prima cerca duplicati con JQL su CIAOB. Bozza **in inglese**, nello stile dei bug recenti: descrizione, evidenze (payload/ID), Root cause (file:metodo), Expected, Workaround, Real case (con "Zendesk (internal tracking): #id"), Steps to reproduce. **Mostra la bozza e crea solo dopo un sì.** Poi cita il codice CIAOB nella risposta Zendesk e metti il ticket in Pending Internal.
- **Task, non Bug**: per una miglioria chiesta dai colleghi interni, o per un difetto notato durante l'analisi che non è quello del ticket del cliente. Stessa struttura in inglese (Context, Request, Expected, Real case, Related) e collegamento "Relates" al bug correlato (`createJiraIssueLink`).

## Feature request su Slack

- Canale **#sall-feature-requests-zendesk**, **una per richiesta**, con il template:
  ```
  Product: Smartpms
  Ticket ID:
  Organization:
  Assignee email:
  Customer email:
  Description:
  ```
  Assignee email = email dell'assegnatario del ticket.
- **Non serve la conferma del testo**: pubblica direttamente e riporta il testo nel resoconto finale. Chiedi solo se l'agente non ha ancora deciso se aprire o meno la feature request.
- Si pubblica con il bot Slack del team tramite lo script `scripts/post-feature-requests.sh` della skill:
  ```bash
  bash "${CLAUDE_SKILL_DIR}/scripts/post-feature-requests.sh" \
    --ticket 126140 --org "Organizzazione (struttura)" \
    --assignee <email assegnatario> --customer <email cliente> \
    "Descrizione FR 1" "Descrizione FR 2"
  ```
  - Ogni descrizione diventa un messaggio separato con l'intestazione del template. Nelle descrizioni metti esempi concreti (ID prenotazione, numero documento), senza dati personali degli ospiti.
  - Il token è uguale per tutti ed è in 1Password (vault Shared, voce `support-copilot - Slack`). Lo script lo legge dall'ambiente (`SLACK_BOT_TOKEN`, se l'organizzazione lo distribuisce nelle impostazioni gestite) o dal file `~/.config/smartpms/slack.env` (permessi 600, altrimenti si ferma). **Non stampare mai il token** (niente `env`, `echo $SLACK_BOT_TOKEN` o simili), **non leggere né modificare quel file** e non chiedere il token in chat. Se manca, di' all'agente di copiarlo da 1Password e salvarlo con il comando del README del plugin (passo 4 del setup).
  - Esito: una riga `OK` per messaggio. Lo script si ferma al primo errore e stampa la risposta di Slack (`not_in_channel` = invitare il bot nel canale; `channel_not_found` = mettere l'ID del canale in `SLACK_CHANNEL`; `invalid_auth` = token scaduto o revocato: avvisa il responsabile del supporto, che lo ruota e aggiorna 1Password; poi l'agente risalva il file).
  - **Non rieseguire lo script dopo un successo**: non è idempotente e duplica i messaggi.
  - Dopo la pubblicazione imposta Category `feature_requests`.

## Messaggi ai colleghi su Slack

- Quando l'agente chiede di scrivere a un collega con il bot del team, il messaggio va **sempre in un DM di gruppo con dentro anche l'agente che lo chiede** (bot + collega + agente), mai in un DM solo tra bot e collega: così l'agente vede la risposta e può continuare lui.
- `conversations.open` con `users` = "IDcollega,IDagente" e `return_im: false`, poi `chat.postMessage` sul canale restituito. Token come per le feature request: mai stamparlo né leggere il file.
- Testo in mrkdwn Slack (`*grassetto*`, `•` per gli elenchi). Mostralo all'agente e invia solo dopo il suo ok. **Non rieseguire dopo un `OK`**: non è idempotente.

## Aggiornamenti Payload

- I fatti di prodotto vanno solo in Payload, mai nel plugin. Decidi tu se aggiornare un documento esistente o crearne uno nuovo (SKILL.md, passo 9).
- **Non sempre resta una bozza.** Dopo ogni scrittura MCP il server ricalcola la certezza del documento: con **8 o più** il documento va **online subito** (sul sito pubblico, se è una guida pubblica); sotto 8 resta in bozza e Alessandro lo rilegge e pubblica. Vale anche per `addFaq` e `addDomandaAperta`.
- Prima di proporre la scrittura leggi la `certezza` del documento in `searchDocs` / `getDoc`. Se è 8 o più, nella proposta scrivi che **va online subito** e non chiamarla "bozza", anche se l'agente la chiama così. Avvisa **prima** della scrittura, non dopo.
- La certezza bassa di una singola FAQ o di un caso noto (es. fonte `ticketNonConfermato`) non impedisce la pubblicazione: conta la certezza del documento. Chiedi conferma prima di ogni scrittura.
- `ticketConfermato` solo se il cliente ha confermato esplicitamente che la soluzione ha funzionato; altrimenti `ticketNonConfermato`. `codice` solo se dedotto dal codice. Un elemento nato da un ticket si conferma con lo stesso ticket solo se poi il cliente conferma l'esito.
- Lo stato di pubblicazione affidabile è quello nella risposta della scrittura (`pubblicazioneAutomatica`): `searchDocs` può mostrare "bozza" anche su documenti pubblicati.
- Con una chiave Payload su più prodotti passa sempre `prodotto` nelle create (`createPlaybooks`, `createInternalGuides`), altrimenti il server risponde "Moduli inesistenti".

## HubSpot

- Tutto ciò che si scrive su HubSpot (task, note, descrizioni) va **in inglese**, fin dalla prima bozza.
- Le **contestazioni di fattura** dei clienti si gestiscono con un task all'account manager sulla company HubSpot del cliente, non con una side conversation al Finance.

## Casi Zendesk particolari

- **Ticket "Conversation with …" ancora assegnati all'agente AI** (assignee `25630294871836`, `support_type: ai_agent`, `group_id` null): non si possono chiudere né riassegnare, né via API (risponde successo ma ignora stato, gruppo e assegnatario) né da UI. Se sono duplicati: Category "Other", Topic "Others:: Duplicate", una nota interna che rimanda al ticket principale, poi lasciali aperti senza altri tentativi.
- **PEC inoltrate da `helium@pec.it`** ("Per Conto Di", utente Zendesk `16241165317916`): inoltra PEC di clienti diversi ed è legato per errore all'organizzazione di Hotel Solemare, quindi l'organizzazione del ticket non è affidabile. Scarica l'allegato `postacert.eml` dal `content_url` (requests nel workbench Composio): nel corpo ci sono mittente originale, CC e firma con P.IVA. Trova il cliente con `smartpms_identify_customer` (P.IVA) e su Zendesk, proponi all'agente il nuovo requester (email non PEC) e la nuova organizzazione, e con il suo ok aggiornali con `data: {requester_id, organization_id}`.
- **Allegati con dati di carte** inviati dal cliente: vanno oscurati, ma è una cancellazione permanente, quindi la fa l'agente a mano.
