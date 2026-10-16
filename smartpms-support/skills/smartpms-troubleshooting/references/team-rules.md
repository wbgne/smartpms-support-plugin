# Regole del team Support SmartPMS

Regole operative valide per tutti gli agenti, da leggere su ogni ticket. Le procedure per agire (side conversation, Jira, feature request, Payload, HubSpot, casi Zendesk particolari) sono in `azioni.md`, da leggere prima di quelle azioni.

"L'agente" è la persona che usa questa sessione: ricava il suo ID e la sua email Zendesk con `ZENDESK_GET_ABOUT_ME` (`data.owner_info.user.id` / `.email`). Non usare mai l'ID di un altro agente.

## Risposta al cliente

- Prepara **sempre** una bozza di risposta e **chiedi sempre prima di inviarla**. L'approvazione vale per quella singola risposta: non riusare un sì precedente.
- **Le promesse dell'agente AI di Zendesk non ci vincolano** (es. "verificheremo i log con il team"): non seguirle, rispondi nel merito di quello che hai verificato.
- **Prima della bozza controlla a chi arriva**: requester, submitter e tag. Con il tag `internal_employee` il ticket l'ha aperto un collega interno (es. CSM Smartpricing) per conto del cliente: il requester è il cliente, il collega è submitter/follower e il suo messaggio è una nota privata. La risposta pubblica arriva quindi al cliente: scrivila per lui, non per il collega ("your client…"). In caso di dubbio chiedi se serve invece una nota interna al collega.
- **Stile, firma e formattazione** della risposta (firma automatica di Zendesk, niente righe che iniziano con "1.", niente testo tra doppie graffe) sono nella skill `team-support-voice` di questo plugin: si usa per ogni bozza al cliente.
- **Oggetto del ticket**: la notifica email al cliente lo riporta. Se è un oggetto interno (es. cita Octorate o note del team), cambialo prima della risposta pubblica.
- Dopo l'invio, con `ZENDESK_UPDATE_ZENDESK_TICKET`: assegna il ticket all'agente (il suo ID da `ZENDESK_GET_ABOUT_ME`), imposta i campi CB (sezione sotto) e lo stato:
  - `solved` se la risposta dà una **soluzione concreta che il cliente applica da solo** (es. riattivare l'Invio Automatico ISTAT e fare l'invio manuale degli arretrati): non serve la sua conferma. Vale anche per i ticket informativi e per le domande generiche o vaghe: rispondi coprendo i casi possibili, senza chiedere numero o struttura per approfondire.
  - `pending` solo se aspettiamo davvero un dato o una risposta del cliente per proseguire (es. "in che provincia è la struttura?").
  - **Pending Internal** (`custom_status_id: 15294614941468`) se sul ticket c'è un'escalation interna aperta (L2, Finance, Activations, Octorate) o un bug Jira collegato. Con il Pending semplice (`13500829714076`) il ticket si chiude da solo dopo qualche giorno mentre aspettiamo ancora il team interno.
- Quando chiedi conferma per l'invio, indica anche lo stato e i valori CB che applicherai.
- **La bozza deve essere visibile all'agente**: per intero nel messaggio finale, mai solo nel riquadro di fine turno (vedi `SKILL.md`, passo 7).
- **Bozza in tedesco**: subito sotto mostra anche la traduzione in italiano, così l'agente può controllarla prima di approvare. Al cliente si invia solo il testo in tedesco.
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

- **Escalation L2** solo per dati rotti o per un comportamento che contraddice il codice o la documentazione. Le verifiche che l'agente può fare da solo restano a L1 (es. esito di consegna di un'email in Intool, Email > Events).
- Se il PMS fa quello che il codice prevede ma il risultato è scomodo per il cliente, è una **feature request**, non un bug. Esempio: l'`extra_guest_fee` di Airbnb salvato solo nel campo `extras`, senza riga extra, che quindi non entra nel Conto. Nella risposta al cliente parla di "richiesta di miglioramento", non di "problema segnalato al team tecnico".
- **Prima di aprire un'escalation cerca il bug su Jira** (progetto CIAOB, JQL). Se esiste già, **niente side conversation L2**: l'agente collega il bug al ticket, cita il codice CIAOB nella risposta e il ticket va in Pending Internal.
- **Restano a L1** (niente L2, niente Activations):
  - collegare un'azienda come sotto-azienda della principale (`parent_id`) e spostare una struttura da un'azienda all'altra: prepara il riepilogo (ID azienda, parent, struttura da/a, connessioni attive), l'agente esegue nel PMS, poi verifica con `smartpms_identify_customer` e Solved;
  - collegare un nuovo annuncio/struttura **Booking.com**: lo fa il cliente da solo da **MyChannel** nell'azienda (guida interna Payload `ota-booking-mychannel-attivazione`);
  - prenotazioni con **Ospiti = 0**: si corregge il campo Adulti (FAQ della guida Payload `prenotazioni-scheda-gestione-tab`);
  - tutto ciò che il cliente vede in piattaforma e corregge da solo: risposta con le istruzioni e Solved. Esempio: **account Smartpay limitato** da Stripe, con i requisiti visibili in Configurazione Smartpay (caso noto del playbook Payload `smartpay-contestazione-chargeback-ospite`). L2 solo se in piattaforma il problema non si vede o la correzione del cliente non basta.
- **Prenotazioni duplicate** (doppio submit, stessa camera): non le cancelliamo e non lo proponiamo, né lo chiediamo al cliente. Nell'escalation L2 chiedi di "valutare e gestire il doppione"; al cliente indica quale prenotazione è corretta e quale il duplicato, e che se ne occupa il team tecnico. Non usare `smartpms_prepare_cancel_reservation` sui duplicati.

## Politiche verso il cliente

- **Niente report o estrazioni su misura**: non offriamo mai di preparare noi un file, un'estrazione o un report personalizzato (es. via Smarty/API da backoffice), anche se tecnicamente fattibile. Indichiamo solo quali report/export esistenti combinare; l'elaborazione resta responsabilità del cliente. Se manca una funzione → feature request. Ticket informativo → Solved.
- **Adattarsi alla configurazione del cliente**: quando un'impostazione del cliente causa il problema ma è una sua scelta legittima, proponi per prima la strada che la mantiene e lavoraci intorno; indica la modifica dell'impostazione solo come alternativa. Esempio: ISTAT Campania con "Chiusura struttura con chiusura vendite" attiva → si mantiene il flag e si riaprono le vendite (playbook Payload `istat-campania-smart-invii-in-errore`). Per l'ISTAT usa prima `smartpms_check_istat_setup` / `smartpms_list_istat_logs` per vedere le opzioni attive.
- **Le correzioni di configurazione le fa il cliente**: scrivi le istruzioni nella risposta e metti Pending; dopo la sua conferma facciamo noi le operazioni di supporto (es. Rates Sync) e verifichiamo (es. su SmartChannel).
- **Formazioni dedicate** (es. contabilità e report non coperti dall'onboarding): le facciamo noi, ma **al momento solo in inglese**. Nella risposta chiedi al cliente se va bene (dillo esplicitamente ai clienti non anglofoni), poi si propongono le date. Non serve passare da Activations o dall'account manager. Ticket in Pending in attesa della risposta.
- **Promozioni del PMS non arrivano a Booking/Airbnb**: è un limite del prodotto, non un bug. Soluzione via extranet + feature request + Solved (FAQ della guida Payload `booking-engine-extra-promozioni`).
- **Stripe diretto dismesso**: non si possono più collegare nuovi account Stripe del cliente; per i pagamenti online con carta si propone SmartPay. Le aziende che avevano già Stripe collegato possono ancora addebitare dalla prenotazione (playbook Payload `smartpay-migrazione-stripe-nativo`).
