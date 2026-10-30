# Strumenti interni nel browser integrato

Valgono solo se l'agente ha una sessione attiva nel browser integrato (`mcp__Claude_Browser__*`). Se non c'è, non aprirla e non chiedere credenziali: usa i tool dell'MCP Gateway. Tutto in **sola lettura**: mai salvare, modificare, rigenerare o inviare senza conferma esplicita; non ripetere in chat i numeri di documento degli ospiti.

Come si usano il PMS con l'utenza superadmin e la console SmartChannel (pagina prenotazione in sola lettura, modifica dalla barra di ricerca, ricerca per codice canale, Pagamenti OTA, JSON grezzo, Diagnostica, Registro attività) è nelle guide interne Payload `prenotazioni-superadmin-consultazione-modifica` e `smartchannel-console-prenotazioni-diagnostica-registro`. Qui restano solo le tecniche per Claude.

## PMS superadmin (https://pms.smartness.com)

- Il pannello è stretto: allargalo a 1440 solo se serve e poi ripristina il preset "desktop".
- **Regole del piano tariffario** (non esposte dai tool dell'MCP Gateway): Impostazioni > Proprietà > struttura > Unità e tariffe > **Tariffe** (`/properties/<id>/room-types`, colonna "Piano Tariffario") e > **Piani tariffari** (`/properties/<id>/rate-plans`: ID, policy, soggiorno minimo e massimo). La pagina `/rate-plans/<id>` diretta non esiste.
- **Imposta di soggiorno per ospite** (importo, esenzione, `nightly_breakdown`, residenza): non è visibile nella lista UI. Rileggila rieseguendo la GET dell'app `https://pms-api.smartness.com/api/3.0/guests/paginated?...&legal_compliance_request_id=<id>` con `fetch(url,{credentials:'include'})`; l'URL completo è in `performance.getEntriesByType('resource')` dopo aver aperto il tab CHECKIN. Il pivot dell'ospite contiene `city_tax_amount`, `city_tax_exclusion`, `city_tax_exclusions_reductions`. Non aprire i form "Modifica" degli ospiti solo per leggere.
- **Prezzo per ospite**: `fetch('https://pms-api.smartness.com/api/3.0/unit-categories/price-per-guest-config/get?rate_plan_id=X&unit_category_id=Y', {credentials:'include'})`.
- **IoT** (GET con `fetch(url,{credentials:'include'})`): `.../api/3.0/reservation-meta/collected?reservation_id=<id>` (meta `smart_iot_locks`); `.../3.0/iot-marketplace/business-rules/reservation-meta?reservation_id=<id>`; `.../3.0/iot-marketplace/accounts/paginated?iot_integration_id=10` (10 = Nuki; `data.nuki.units` = mappatura `unit_id → lock_ids`; gli account stanno sulla company madre e coprono le figlie).
