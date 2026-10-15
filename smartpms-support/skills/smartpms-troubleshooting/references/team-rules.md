# Regole del team Support SmartPMS

Regole operative valide per tutti gli agenti. Leggile prima di preparare risposte, escalation o feature request.

"L'agente" è la persona che usa questa sessione: ricava il suo ID e la sua email Zendesk con `ZENDESK_GET_ABOUT_ME` (`data.owner_info.user.id` / `.email`). Non usare mai l'ID di un altro agente.

## Risposta al cliente

- Prepara **sempre** una bozza di risposta e **chiedi sempre prima di inviarla**. L'approvazione vale per quella singola risposta: non riusare un sì precedente.
- **Prima della bozza controlla a chi arriva**: requester, submitter e tag. Con il tag `internal_employee` il ticket l'ha aperto un collega interno (es. CSM Smartpricing) per conto del cliente: il requester è il cliente, il collega è submitter/follower e il suo messaggio è una nota privata. La risposta pubblica arriva quindi al cliente: scrivila per lui, non per il collega ("your client…"). In caso di dubbio chiedi se serve invece una nota interna al collega.
- **Stile, firma e formattazione** della risposta (firma automatica di Zendesk, niente righe che iniziano con "1.", niente testo tra doppie graffe) sono nella skill `team-support-voice` di questo plugin: si usa per ogni bozza al cliente.
- **Oggetto del ticket**: la notifica email al cliente lo riporta. Se è un oggetto interno (es. cita Octorate o note del team), cambialo prima della risposta pubblica.
- Dopo l'invio, con `ZENDESK_UPDATE_ZENDESK_TICKET`: assegna il ticket all'agente (il suo ID da `ZENDESK_GET_ABOUT_ME`), imposta i campi CB (sezione sotto) e lo stato:
  - `solved` se la risposta dà una **soluzione concreta che il cliente applica da solo** (es. riattivare l'Invio Automatico ISTAT e fare l'invio manuale degli arretrati): non serve la sua conferma. Vale anche per i ticket informativi e per le domande generiche o vaghe: rispondi coprendo i casi possibili, senza chiedere numero o struttura per approfondire.
  - `pending` solo se aspettiamo davvero un dato o una risposta del cliente per proseguire (es. "in che provincia è la struttura?").
  - **Pending Internal** (`custom_status_id: 15294614941468`) se sul ticket c'è un'escalation interna aperta (L2, Finance, Activations, Octorate) o un bug Jira collegato. Con il Pending semplice (`13500829714076`) il ticket si chiude da solo dopo qualche giorno mentre aspettiamo ancora il team interno.
- Quando chiedi conferma per l'invio, indica anche lo stato e i valori CB che applicherai.
- Una risposta pubblica riporta il ticket in Aperto: imposta lo stato **dopo** la risposta e poi verificalo. `ZENDESK_GET_ZENDESK_TICKET_BY_ID` non restituisce `custom_status_id`: rileggi con `ZENDESK_SEARCH_ZENDESK` oppure GET `/api/v2/tickets/{id}.json` via proxy_execute.
- `ZENDESK_UPDATE_ZENDESK_TICKET` a volte non applica il `custom_status_id` passato da solo come campo: se rileggendo il ticket lo stato non è cambiato, rimandalo dentro `data` insieme a `status` (es. `data: {status: "pending", custom_status_id: 15294614941468}`).

## Note interne, merge e stati che si riaprono

- Il trigger Zendesk "Private Note Re-open" porta il ticket ad Aperto (`custom_status_id: 13500856142748`) a ogni nota interna, compresi i ticket figli delle side conversation L2.
- Prima della nota annota il `custom_status_id` attuale; dopo la nota rimettilo con `ZENDESK_UPDATE_ZENDESK_TICKET` e verificalo con `ZENDESK_SEARCH_ZENDESK`.
- **Con L2 di mezzo** (nota su un figlio L2, o padre con escalation aperta) lo stato da rimettere è sempre **Pending Internal**, non Aperto e non Pending semplice, anche quando la nota passa la palla a L2.
- Una nota sul figlio L2 riapre **anche il padre**: rimetti lo stato al padre **dopo** la nota sul figlio e verifica entrambi.
- Riaprono il ticket anche le note automatiche di Pluno ("Update from Jira") e il **merge** (`ZENDESK_MERGE_ZENDESK_TICKETS` è asincrono: aspetta la fine del job, poi rimetti lo stato al ticket di destinazione).

## Campi obbligatori (su ogni ticket)

- **CB > Ticket Category** (id `16744953177756`) e **CB > Topic** (id `16745383425820`): campi tagger, si imposta il `value` dell'opzione (es. Category `user_error`, Topic `city_tax`) in `custom_fields` di `ZENDESK_UPDATE_ZENDESK_TICKET`. Le opzioni si leggono con `ZENDESK_GET_ZENDESK_TICKET_FIELDS_OPTIONS` (Topic ha molte opzioni, spesso con prefisso "Area:: Dettaglio").
- Per il **Solved** Zendesk richiede anche **Ticket Type** (`14070976593564`: `request`/`question`/`incident`/`complaint`), **Resolution Cause** (`14092719594524`, es. `provided_information`, `configuration_updated`, `feature_request_dev`) e **Opened by** (`14070435404060`) se vuoto. Senza, risponde 422 RecordInvalid. Compilali nella stessa update di stato e assegnatario.
- **Non chiedere conferma** per questi campi: scegli tu le opzioni esistenti più adatte e riporta nel riepilogo i valori scelti. Controlla e correggi anche i valori precompilati dall'AI agent (es. "Admin / Finance" messo su un tema di prodotto).
- Category `feature_requests` quando dal ticket nasce una feature request su Slack.
- Se nessuna opzione ha senso, proponi nome e value di una nuova opzione e creala con `ZENDESK_CREATE_TICKET_FIELD_OPTION` **solo dopo un sì esplicito**: è configurazione condivisa.
- La connessione Composio Zendesk ha già i permessi necessari: non servono credenziali e non vanno mai usate password lette da file.

## Chi se ne occupa: L1, L2, Jira o feature request?

- **Escalation L2** solo per dati rotti o per un comportamento che contraddice il codice o la documentazione.
- Se il PMS fa quello che il codice prevede ma il risultato è scomodo per il cliente, è una **feature request**, non un bug. Esempio: l'`extra_guest_fee` di Airbnb salvato solo nel campo `extras`, senza riga extra, che quindi non entra nel Conto. Nella risposta al cliente parla di "richiesta di miglioramento", non di "problema segnalato al team tecnico".
- **Prima di aprire un'escalation cerca il bug su Jira** (progetto CIAOB, JQL). Se esiste già, **niente side conversation L2**: l'agente collega il bug al ticket, cita il codice CIAOB nella risposta e il ticket va in Pending Internal.
- **Restano a L1** (niente L2, niente Activations):
  - collegare un'azienda come sotto-azienda della principale (`parent_id`) e spostare una struttura da un'azienda all'altra: prepara il riepilogo (ID azienda, parent, struttura da/a, connessioni attive), l'agente esegue nel PMS, poi verifica con `smartpms_identify_customer` e Solved;
  - collegare un nuovo annuncio/struttura **Booking.com**: lo fa il cliente da solo da **MyChannel** nell'azienda (vedi `product-knowledge.md`);
  - prenotazioni con **Ospiti = 0**: si corregge il campo Adulti (vedi `product-knowledge.md`).
- **Prenotazioni duplicate** (doppio submit, stessa camera): non le cancelliamo e non lo proponiamo, né lo chiediamo al cliente. Nell'escalation L2 chiedi di "valutare e gestire il doppione"; al cliente indica quale prenotazione è corretta e quale il duplicato, e che se ne occupa il team tecnico. Non usare `smartpms_prepare_cancel_reservation` sui duplicati.

## Escalation L2 = side conversation

- Sempre come **side conversation nello stesso ticket Zendesk**, verso il gruppo **Smartpms L2 Support** (`support_group_id: 16756021180700`), **senza assegnatario**. Non Slack, non nota interna.
- Tool: `ZENDESK_CREATE_SIDE_CONVERSATION` con `to: [{support_group_id: 16756021180700}]` (in Composio si trova solo con `search_strategy: "tool_search"`).
- **Una side conversation per ogni problematica**: mai più bug nella stessa escalation, anche se arrivano dallo stesso ticket.
- Passa **sempre `html_body`** formattato (`<h3>`/`<strong>` per i titoli, `<ul>/<ol>`, `<code>` per ID e batch). Con il solo `body` testuale Zendesk perde a capo ed elenchi. Il messaggio non è modificabile dopo l'invio: mostra il testo all'agente e chiedi conferma prima di crearla.
- Contenuto: ID interni delle prenotazioni, cronologia in UTC, batch, cosa è stato verificato e cosa si chiede di verificare.
- Per rispondere nella stessa side conversation (nessun tool Composio dedicato): `proxy_execute` in COMPOSIO_REMOTE_WORKBENCH, POST `https://smartness.zendesk.com/api/v2/tickets/{ticket}/side_conversations/{id}/reply` con `{"message": {"to": [{"support_group_id": 16756021180700}], "body": ..., "html_body": ...}}` (`to` è obbligatorio).
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
- Si pubblica con il bot Slack del team tramite lo script `scripts/post-feature-requests.sh` di questa skill (vedi SKILL.md, passo 10). Il token è uguale per tutti ed è in 1Password (vault Shared, voce `support-copilot - Slack`); ogni agente lo salva nel file `~/.config/smartpms/slack.env` (permessi 600), oppure arriva nell'ambiente (`SLACK_BOT_TOKEN`) se l'organizzazione lo distribuisce nelle impostazioni gestite. **Non stampare mai il token, non leggere né modificare quel file** e non chiedere il token in chat.

## Aggiornamenti Payload

- Se il caso insegna qualcosa di riutilizzabile, proponi un aggiornamento in Payload. Decidi tu se aggiornare un documento esistente o crearne uno nuovo (vedi SKILL.md, passo 9).
- **Non sempre resta una bozza.** Dopo ogni scrittura MCP il server ricalcola la certezza del documento: con **8 o più** il documento va **online subito** sul sito pubblico; sotto 8 resta in bozza e Alessandro lo rilegge e pubblica. Vale anche per `addFaq` e `addDomandaAperta`.
- Prima di proporre la scrittura leggi la `certezza` del documento in `searchDocs` / `getDoc`. Se è 8 o più, nella proposta scrivi che **va online subito** e non chiamarla "bozza", anche se l'agente la chiama così. Avvisa **prima** della scrittura, non dopo.

## HubSpot

- Tutto ciò che si scrive su HubSpot (task, note, descrizioni) va **in inglese**, fin dalla prima bozza.
- Le **contestazioni di fattura** dei clienti si gestiscono con un task all'account manager sulla company HubSpot del cliente, non con una side conversation al Finance.

## Casi Zendesk particolari

- **Ticket "Conversation with …" ancora assegnati all'agente AI** (assignee `25630294871836`, `support_type: ai_agent`, `group_id` null): non si possono chiudere né riassegnare, né via API (risponde successo ma ignora stato, gruppo e assegnatario) né da UI. Se sono duplicati: Category "Other", Topic "Others:: Duplicate", una nota interna che rimanda al ticket principale, poi lasciali aperti senza altri tentativi.
- **PEC inoltrate da `helium@pec.it`** ("Per Conto Di", utente Zendesk `16241165317916`): inoltra PEC di clienti diversi ed è legato per errore all'organizzazione di Hotel Solemare, quindi l'organizzazione del ticket non è affidabile. Scarica l'allegato `postacert.eml` dal `content_url` (requests nel workbench Composio): nel corpo ci sono mittente originale, CC e firma con P.IVA. Trova il cliente con `smartpms_identify_customer` (P.IVA) e su Zendesk, proponi all'agente il nuovo requester (email non PEC) e la nuova organizzazione, e con il suo ok aggiornali con `data: {requester_id, organization_id}`.
- **Allegati con dati di carte** inviati dal cliente: vanno oscurati, ma è una cancellazione permanente, quindi la fa l'agente a mano.

## Politiche verso il cliente

- **Niente report o estrazioni su misura**: non offriamo mai di preparare noi un file, un'estrazione o un report personalizzato (es. via Smarty/API da backoffice), anche se tecnicamente fattibile. Indichiamo solo quali report/export esistenti combinare; l'elaborazione resta responsabilità del cliente. Se manca una funzione → feature request. Ticket informativo → Solved.
- **Adattarsi alla configurazione del cliente**: quando un'impostazione del cliente causa il problema ma è una sua scelta legittima, proponi per prima la strada che la mantiene e lavoraci intorno; indica la modifica dell'impostazione solo come alternativa. Esempio: ISTAT Campania con "Chiusura struttura con chiusura vendite" attiva → aprire le vendite dalla prima data in errore fino a 48 ore fa e rifare l'invio manuale, invece di togliere l'opzione. Per l'ISTAT usa prima `smartpms_check_istat_setup` / `smartpms_list_istat_logs` per vedere le opzioni attive.
- **Le correzioni di configurazione le fa il cliente**: scrivi le istruzioni nella risposta e metti Pending; dopo la sua conferma facciamo noi le operazioni di supporto (es. Rates Sync) e verifichiamo (es. su SmartChannel).
- **Formazioni dedicate** (es. contabilità e report non coperti dall'onboarding): le facciamo noi, ma **al momento solo in inglese**. Nella risposta chiedi al cliente se va bene (dillo esplicitamente ai clienti non anglofoni), poi si propongono le date. Non serve passare da Activations o dall'account manager. Ticket in Pending in attesa della risposta.
- **Promozioni del PMS non arrivano a Booking/Airbnb**: è un limite del prodotto, non un bug. Soluzione via extranet + feature request + Solved (dettagli in `product-knowledge.md`).
- **Stripe diretto dismesso**: il cliente non può più collegare il proprio account Stripe; i pagamenti online con carta passano solo da SmartPay.
