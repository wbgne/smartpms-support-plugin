# Conoscenze di prodotto confermate dal team

Fatti chiariti dal team su casi reali. Usali per non proporre cause o soluzioni sbagliate.

## Channel manager e OTA

### Octorate: Channel Full Sync spento = configurazione standard

- Channel Full Sync (ADMIN CONFIG) è **disattivato di proposito su tutte le strutture**: è il funzionamento standard, anche se il codice (`CreateNewCustomer`) crea le strutture con Full Sync attivo.
- Con Full Sync spento le variazioni di disponibilità generate dal PMS (prenotazioni, blocchi, spostamenti, cancellazioni) sono SKIPPED (`UpdateAvailabilities::saveHistory`, salvo `process_availability`): la disponibilità da prenotazioni OTA la gestisce Octorate da solo (prenotazioni che passano da Octorate + AutoPilot Chiusura).
- Lo smart tool `smartpms_analyze_overbooking` segnala comunque `channel_full_sync_disattivo` come anomalia: **ignoralo**. Non proporre di riattivarlo e non indicarlo al cliente come causa.
- Negli overbooking Octorate cerca invece cosa Octorate non può sapere da solo: blocchi automatici delle suite sulle unità comprese, spostamenti fatti nel PMS, blocchi manuali creati solo nel PMS, AutoPilot Chiusura Octorate spento, tariffe master multiple della stessa tipologia senza derivazione di disponibilità (= inventari separati in Octorate).
- Playbook Payload di riferimento: `octorate-overbooking-disponibilita-non-riallineata` (passo 3 "Non riattivare Channel Full Sync").

### Octorate: disattivare le recensioni automatiche Airbnb

- Lo fa il supporto: il cliente non può farlo da SmartPMS.
- Percorso: Octorate → Channel Manager → **Modifica** sulla riga della connessione Airbnb → sezione "Recensione di Default" in fondo alla pagina → disattivare "Invio automatico delle recensioni".
- Va fatto struttura per struttura e ripetuto per i nuovi annunci collegati. Dopo la modifica verifica ogni struttura (in un caso una non l'aveva recepita).
- Guida interna Payload: `octorate-airbnb-disattivazione-recensioni-automatiche`.

### Booking.com: nuovo annuncio via MyChannel, in autonomia

- Il collegamento di un annuncio/struttura Booking.com lo fa **il cliente da solo** dalla sezione **MyChannel** dell'azienda (Impostazioni > Azienda > MyChannel): richiesta a MyGuestCare dall'Extranet, Crea Connessione Portale, Gestisci Mapping Stanze, Dettagli Portale (Abilita download + sincronizzazione). Guida interna Payload: `ota-booking-mychannel-attivazione`.
- Niente escalation ad Activations e non scrivere al cliente "lo attiviamo noi".
- Restano al supporto (pulsanti visibili solo internamente): **Importa prenotazioni storiche** (dopo l'attivazione) e **Importa planner portale** (prima dell'attivazione, se il cliente vuole tenere i prezzi Booking).
- `smartpms_check_company_channels` può riportare "nessun account MyChannel per l'azienda" anche quando la sezione è attiva per il cliente: non è un blocco.

### Booking.com: prenotazione non consegnata al CM

- Se l'extranet Booking segnala che una prenotazione non è stata registrata da CM/PMS, il problema è di Booking (mancata consegna), non del PMS. L'import lo facciamo noi.
- Al cliente chiedi **solo le date di check-in** e la **struttura** (se l'azienda ne ha più d'una), non ospite, importi, camera o check-out.
- Verifica comunque che la connessione Booking sia attiva e che gli ID non esistano già (`check_import_reservation_ids`).

### Promozioni del PMS: solo sul Booking Engine e su alcuni canali

- Le promozioni create nel PMS (Impostazioni → Proprietà → Promozioni) **non arrivano a Booking.com né ad Airbnb**. SmartChannel le pubblica solo su Google Hotel, Holidu, Vrbo, Agoda, Expedia e Trip.com (`cb-channel-go/internal/domain/promotionpub/capabilities.go`); con MyChannel non passano comunque.
- Il cliente le deve ricreare nell'extranet di ciascun portale. Su **Airbnb** consiglia gli **Sconti** dell'annuncio (Prezzi → Sconti, es. soggiorni lunghi) e **non le Promozioni** di Airbnb, che sembrano sostituire i prezzi inviati dal PMS.
- È un limite del prodotto: soluzione via extranet, feature request su Slack, ticket in Solved.

### SmartChannel: prezzo fisso su Airbnb ("CAL" sulla riga OCC)

- Sintomo: Airbnb via SmartChannel fermo a un prezzo fisso. Nel calendario della connessione SmartChannel la riga OCC 1 è "CAL" (valore digitato a calendario) invece di derivare da una regola.
- Causa: nel PMS il Prezzo per ospite della tipologia × piano ha la riga 1 ospite disattivata (`is_enabled: 0`); sulle strutture sane è attiva con amount 0. `smartpms_check_rate_setup` **non mostra le righe con amount 0**, quindi non rivela righe disattivate.
- La correzione la fa il cliente (istruzioni nella risposta, Pending); dopo la sua conferma facciamo Rates Sync e verifichiamo su SmartChannel.

### Vrbo: audit con errore 500

- Gli "Integration Audit Report" Vrbo (CSV con `Advertiser Id` / `Listing External Id`) riportano solo lo statusCode. `Advertiser Id` = ID connessione SmartChannel, `Listing External Id` = ID tipologia (unit category) in SmartChannel.
- L'errore vero si legge nella Diagnostica della connessione SmartChannel (vedi "Strumenti interni nel browser" sotto), es. `More than one rate plan combination found` = mappature multiple sulla stessa tipologia.
- Il pulsante "Perché non funziona?" (assistente ops) non legge i feed Vrbo e può dare consigli sbagliati (es. mappare altre tariffe).

### Sorgente "Direct" = inserimento manuale

- Sorgente `pms` / "Direct" significa prenotazione **inserita a mano** dagli utenti della struttura nel gestionale. Le prenotazioni dal sito del cliente hanno come sorgente il nome del Booking Engine.
- In un overbooking con prenotazioni "Direct" non chiedere al cliente se arrivano dal sito: trattale come inserimenti manuali (causa operativa, non problema di sincronizzazione).

## Tariffe e disponibilità

### Modifica massiva dal calendario: disponibilità su AUTO

- Quando spieghi al cliente come modificare i prezzi in blocco (**Calendario > Modifica massiva**), scrivi di impostare il campo disponibilità **sull'opzione AUTO**, non di "lasciarlo vuoto".
- Caso tipico: il cliente scrive un prezzo nel campo disponibilità (es. 150) e forza la disponibilità → overbooking.

### Chiusura automatica: va impostata su ogni piano

- Lo stop sell della chiusura automatica (`RoomTypeRatesAutoClose.php`, modification 7 nello storico tariffe) è scritto con `skip_derived => TRUE`: **non si propaga ai piani derivati**, anche se hanno la derivazione stop sell attiva. Ogni piano (Standard, NR, Weekly…) deve avere la sua Chiusura automatica 0 giorni + Ora chiusura. (Con 8 giorni chiude la data a +8, non il giorno stesso.)
- Diagnosi: `smartpms_list_activity_logs` log_name `rate_plans` sul piano (autoclose_days/autoclose_time) + `smartpms_get_rate_history` della tariffa per la data: c'è un record modification 7 con stop_sell 1 all'ora di chiusura? `check_rate_setup` mostra autoclose_days ma non l'ora.
- Correzione nel PMS: Piani tariffari → matita → Regole di Disponibilità → "Abilita chiusura automatica", giorni 0, Ora chiusura → "Modifica". Verifica nel log `rate_plans`. (Nel codice `!empty(autoclose_days)` sembrerebbe scartare lo 0, ma in produzione lo 0 chiude regolarmente.)

### Regole del piano tariffario e metodo di pagamento

- I tool Smarty non espongono le regole del piano tariffario. Nel PMS: Impostazioni > Proprietà > struttura > Unità e tariffe > **Tariffe** (`/properties/<id>/room-types`, colonna "Piano Tariffario") e > **Piani tariffari** (`/properties/<id>/rate-plans`: ID, policy, soggiorno minimo e massimo). La pagina `/rate-plans/<id>` diretta non esiste.
- `payment_method` della prenotazione (`ConstReservationPaymentMethods`): 0 sconosciuto, **1 carta di credito**, 2 bonifico, 3 prepagato, 4 contanti, 5 all'arrivo. Verificalo sempre prima di dire al cliente il metodo.
- Per le prenotazioni da preventivo (sorgente Quotes, 198), se l'ospite sceglie SmartPay il filtro `isPaidViaSmartpayBE` salta la richiesta automatica.

### API: ruolo `external-revenue-manager` scarta le restrizioni

- Se un'utenza API ha il ruolo `external-revenue-manager`, `RateCalendarService::sanitizeDataForRms` toglie da ogni riga del bulk availability, stop_sell, max_stay, cut_off, cta, ctd, forza auto_availability=0 e registra la modifica come RMS (15). Risponde 200 senza errore; nella risposta il campo manca (resta solo `auto_availability: 0`): è il segnale per riconoscerlo. Passano solo amount e min_stay.
- "Scrivo via API ma stop_sell/disponibilità non cambiano" → controlla prima di tutto i ruoli dell'utenza con `smartpms_identify_customer`. Togliere il ruolo vale per tutte le aziende collegate all'utenza; finché resta, per chiudere una notte si usa un blocco (POST /reservations type 3) oppure il pannello.

## Prenotazioni e report

### Ospiti = 0 → si corregge il campo Adulti

- Il campo **Ospiti** della tab Principale è in sola lettura (Adulti + Bambini). Con `guests = 0` ogni salvataggio dà "errore di validazione" (le API vogliono guests ≥ 1). Correzione L1, niente L2: si cambia **Adulti** e si salva.
- Il salvataggio ricalcola tassa di soggiorno (per n. ospiti), totale lordo (include pulizie) e revenue share: avvisa il cliente (es. tassa di soggiorno da incassare). Poi Solved.

### Report Revenues: occupazione oltre il 100%

- Il report Revenues (`RevenueReportService::getNights`) conta le notti dalle righe di `reservation_amount_details`, non dalle date della prenotazione; il denominatore è unità non jolly × giorni del mese. Quando Airbnb (log "Sistema", causer null) cambia le date, le righe giornaliere non vengono rigenerate: restano le notti vecchie e mancano le nuove.
- È il bug esistente **CIAOB-3031**: niente side conversation L2, si collega il bug al ticket e il ticket va in Pending Internal.
- Verifica: `smartpms_list_reservations` con include `reservation_amount_details`, confronto tra numero di righe e notti (`daily_details` è un'altra tabella e contiene anche il giorno di check-out).

## Pagamenti

### SmartPay: importo realmente addebitato

- Se ricevuta SmartPay ("Payment Successfully Completed") e pagamento nel PMS mostrano importi diversi, l'importo addebitato si ricava dalla commissione in `smartpms_smartpay_payouts` (con `payout_id`): commissione ≈ **1,83% + €0,25** (carte EEA) oppure **3,17% + €0,25** (altre carte); netto bonificato = addebitato − commissione.
- Il `gross_total` della liquidazione può riportare l'importo nominale della richiesta e generare un `unexplained` negativo che non è una trattenuta reale.
- Prima di dire al cliente che l'ospite ha pagato troppo o troppo poco, controlla liquidazione e commissione e cerca nel PMS pagamenti manuali successivi (es. al check-in).

### SmartPay: condizioni economiche IC++

- **Vecchio modello flat**: carte UE 1,5% + 0,20 € + IVA 22% (= 1,83% + 0,25 € IVA inclusa, come nelle liquidazioni). Extra-UE 3,17% + 0,25 € IVA inclusa.
- **IC++**: 1,1% standard (comprende Stripe, uguale per ogni carta) + costi di network al costo (consumer UE 0,35–0,5%) + 0,20 € a transazione, + IVA 22% sulla somma.
- **Rimborsi**: commissione dovuta solo se il pagamento è già stato trasferito sul conto (liquidazione ogni giorno lavorativo con l'incassato del giorno prima).
- Nessun canone né costo di attivazione. Disattivazione totale o parziale in autonomia, senza penali, riattivabile, senza conseguenze sugli altri servizi.
- Un confronto esatto sullo storico del cliente non è possibile (mix di carte): esempio 100 € consumer UE, oggi 2,07 €, con IC++ tra 2,03 € e 2,29 €.
- Le condizioni sono nella macro Zendesk "CS | T&C e Modello Smartpay IC++" (sezione [CONDIZIONI ECONOMICHE IC++]), che prevede Solved: parti da lì. Per domande non coperte: Federico Di Mella (Slack).

### Carta a garanzia senza addebito (SECOM)

- Esiste, in due modi:
  - **Area ospite** (link del campo "Cliente - Link Portale", `https://hub.bookpage.io/portal/<client.nano_id>/reservations`): su ogni prenotazione futura e non cancellata c'è il pulsante carta a garanzia. Il salvataggio scrive solo `ccs_token`: niente addebito, niente cambio di stato, **niente activity log**. Il link dà accesso come l'ospite (può cancellare o cambiare la carta): usalo in sola lettura.
  - **Preventivo**: con la sorgente Quotes (198) tra i Canali esclusi di SmartPay e il metodo "Carta di credito - Solo visualizzazione" attivo, il preventivo usa SECOM al posto di SmartPay: l'ospite inserisce la carta e il preventivo si conferma senza addebito, anche con tariffa non rimborsabile.
- **Non affermare mai che una carta "non c'è" basandoti su Smarty o sui log**: `has_credit_card_meta` riguarda solo le carte cifrate delle OTA ed è false anche con una carta SECOM; il `ccs_token` non è esposto da Smarty. Verifica con il pulsante "Visualizza carta di credito" nel pannello di modifica della prenotazione, senza leggere i dati della carta. Su Octorate il campo `technicalCreditCardChange` è valorizzato.
- Per i test non usare mai la propria carta: il token resta visibile al cliente anche a prenotazione cancellata.

### Stripe diretto dismesso

- Il collegamento diretto di un account Stripe del cliente (vecchio gateway in `booking_payment_providers`) è dismesso: i pagamenti online con carta passano solo da SmartPay. Per problemi di bonifici (es. "Debit Not Authorized") va completata la procedura di remediation SmartPay.

## Fiscale e compliance

### ISTAT Lazio: RADAR dismesso → Ross1000

- Il portale **RADAR non è più attivo da maggio 2025** (comunicazione della Regione Lazio): i dati ISTAT vanno inviati su **Ross1000** (in SmartPMS account ISTAT tipo 22 "ISTAT Lazio Turismo5", famiglia turismo5).
- Quando un cliente del Lazio parla di RADAR: spiega che non è più attivo e che va configurato Ross1000 con le credenziali dirette Ross1000 Lazio (le strutture dovrebbero averle ricevute dalla Regione; se non le hanno, devono contattare la Regione Lazio). Aggiorna l'etichetta della configurazione ISTAT se cita ancora Radar, poi Convalida, Invio Automatico e Invio Manuale dalla data di attivazione.
- Guida pubblica di riferimento: `ross1000-turismo5`.

### "Le schedine sono partite da sole": spesso è l'invio ISTAT

- Se il cliente dice che le schedine sono partite in automatico verso la Questura con Invio Automatico Alloggiati spento, guarda `police_in_status` della richiesta di check-in, non lo `status` aggregato.
- L'invio automatico ISTAT (es. Veneto Turismo5, ogni giorno alle 06:30, giornata di due giorni prima) imposta `stat_in_status: 4` e fa avanzare lo `status` aggregato (1→3 o 3→4) con causer null: nella lista check-in sembra "partita".
- Verifica: `smartpms_check_alloggiati_requests` + log `legal_compliance_requests` (causer: gli invii Alloggiati reali hanno l'utenza del cliente) + `smartpms_list_istat_logs` (`last_attempt_at` nello stesso secondo del cambio di stato). Se l'arrivo è slittato e la schedina non è partita, il cliente può ancora inviarla correggendo la data nel tab Check-in.

### SDI: scarto 00404 "Fattura duplicata" da doppio invio

- Fattura in stato 7 con RicevutaScarto **00404** e nel log documents due `status null→9` (o due `9→5`) nello stesso secondo = **doppio invio**: lo SDI ha accettato una copia e l'altra, scartata, ha sovrascritto stato e `idtrx`. **La fattura è emessa**: non va reinviata né riemessa. Bug Jira esistente **CIAOB-207**: niente side conversation L2.
- Per distinguerli dagli scarti veri guarda il codice dell'ultima RicevutaScarto (00306/00200/00324 = da correggere).
- Gestione: il cliente conferma su Fatture e Corrispettivi, poi il supporto riallinea lo stato dal campo stato del supporto nel PMS. Stato da ripristinare = ultimo esito prima del 00404 (6 Consegnata, 8 Mancata consegna); se c'era solo 5, esito dal portale AdE (di norma XXXXXXX → 6, 0000000 → 8).
- `smartpms_list_company_documents` si ferma a 100 documenti al giorno: per i giorni pieni filtra per stato Errore nella lista del PMS.
- Per rispondere al cliente basta confermare il doppio invio su **una** fattura. L'elenco completo con lo stato da ripristinare serve solo al riallineamento, che aspetta comunque la conferma del cliente: ricavalo allora dal filtro Errore del PMS, non con una scansione dei log di tutte le fatture.

## Self check-in e serrature (IoT / Nuki)

- Con il nuovo setup IoT i campi `pin` e `nuki_smart_lock_auth_id` della prenotazione restano null: **non provano nulla**.
- Il meta `smart_iot_locks` si legge con `smartpms_list_reservations` / `smartpms_get_reservation` con include `meta`: pins (lock_id, lock_name, pin, active, active_from/until), `error`, `unit_lock_first_unlock_at`. `pins: []` su prenotazioni nuove di un'unità = unità probabilmente non mappata a nessun lock.
- `active_from` / `active_until` / `active` li scrive smart-iot solo dal deploy del 07/10/2026: i meta scritti prima hanno finestra null e `active: true` di default e **non indicano né successo né errore** dell'invio al lucchetto. Dopo il deploy: `active_from` = check-in − 15 min, `active` = PIN presente sul device.
- L'invio della PIN al lucchetto (~15 min prima del check-in) lo fa smart-iot e non è visibile dal PMS. PIN nel meta ma non sul lucchetto → escalation L2.
- Non "rigenerare" le PIN modificando la prenotazione (cambio unità/date) per forzare un re-sync: il codice può cambiare e l'ospite ha già quello vecchio nel messaggio.

## Strumenti interni nel browser (solo se l'agente ha già la sessione)

Valgono solo se l'agente ha una sessione attiva nel browser integrato (`mcp__Claude_Browser__*`). Se non c'è, non aprirla e non chiedere credenziali: usa i tool Smarty. Tutto in **sola lettura**: mai salvare, modificare, rigenerare o inviare senza conferma esplicita; non ripetere in chat i numeri di documento degli ospiti.

### PMS superadmin (https://pms.smartness.com)

- Pagina prenotazione: `https://pms.smartness.com/reservations/<id>` → tab in basso PRINCIPALE / DETTAGLI / PAGAMENTI / CHECKIN. È **sola lettura**: per modificare una prenotazione scrivi l'ID interno nella barra in alto "Cerca prenotazione", che apre il flyout di modifica ("Salva" / "Salva e chiudi"). Cambiando tariffa con ⇆ gli importi non vengono ricalcolati.
- Il pannello è stretto: allargalo a 1440 solo se serve e poi ripristina il preset "desktop".
- **Ricerca per codice canale in timeout** (Smarty con `reservation_code` senza struttura, o barra di ricerca globale): pagina Prenotazioni → icona imbuto in alto a destra → "Filtro aziende e figlie" → scegli l'azienda → ✓ verde, poi cerca il codice nel campo "Cerca" della pagina. Nota la struttura, i tool Smarty con `reservation_code` + `property_id` rispondono.
- **Imposta di soggiorno per ospite** (importo, esenzione, `nightly_breakdown`, residenza): non è visibile nella lista UI. Rileggila rieseguendo la GET dell'app `https://pms-api.smartness.com/api/3.0/guests/paginated?...&legal_compliance_request_id=<id>` con `fetch(url,{credentials:'include'})`; l'URL completo è in `performance.getEntriesByType('resource')` dopo aver aperto il tab CHECKIN. Il pivot dell'ospite contiene `city_tax_amount`, `city_tax_exclusion`, `city_tax_exclusions_reductions`. Non aprire i form "Modifica" degli ospiti solo per leggere.
- **Prezzo per ospite**: `fetch('https://pms-api.smartness.com/api/3.0/unit-categories/price-per-guest-config/get?rate_plan_id=X&unit_category_id=Y', {credentials:'include'})`.
- **IoT** (GET con `fetch(url,{credentials:'include'})`): `.../api/3.0/reservation-meta/collected?reservation_id=<id>` (meta `smart_iot_locks`); `.../3.0/iot-marketplace/business-rules/reservation-meta?reservation_id=<id>`; `.../3.0/iot-marketplace/accounts/paginated?iot_integration_id=10` (10 = Nuki; `data.nuki.units` = mappatura `unit_id → lock_ids`; gli account stanno sulla company madre e coprono le figlie).

### SmartChannel (https://manage.smartness.com)

- Console del channel manager interno (channel.smartness.com è solo l'API).
- Prenotazioni → cerca per ID esterno o nome ospite → icona occhio → schede Sistemazioni / **Pagamenti OTA** (payout comunicato dall'OTA) / **Dati tecnici** (ID connessione, **JSON grezzo** con `paymentsTotal`, `toPay`, `otaFee`, `paymentMethod`). Il `paymentsTotal` del gruppo è ciò che il PMS trasforma nel pagamento "OTA PAYOUT".
- Diagnostica connessione: `https://manage.smartness.com/connections/<id>/diagnosis` (menu Admin → Diagnostica) rilancia i feed e mostra il messaggio d'errore.
- Le mappature non visibili in console (Mappature/Annunci mostrano solo quelle esposte) si trovano nel Registro attività: `/audit-log?search=<nome azienda>` → eventi "Mapping creato" con `ratePlanUnitCategoryCombinationId`. La ricerca per ID connessione mostra solo le modifiche alla connessione.
