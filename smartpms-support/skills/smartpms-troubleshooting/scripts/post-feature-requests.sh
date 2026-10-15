#!/usr/bin/env bash
# Pubblica una o più feature request di un ticket Zendesk su Slack (#sall-feature-requests-zendesk)
# con il bot Slack del team.
#
# Uso:
#   post-feature-requests.sh --ticket 126140 --org "Nome organizzazione (struttura)" \
#     --assignee nome.cognome@smartpricing.it --customer cliente@example.com \
#     "Prima descrizione" ["Seconda descrizione" ...]
#
# Ogni descrizione diventa un messaggio separato (una FR per richiesta), preceduto dall'intestazione del template.
# Token: SLACK_BOT_TOKEN nell'ambiente oppure nel file ~/.config/smartpms/slack.env (permessi 600).
# Canale: SLACK_CHANNEL (default "sall-feature-requests-zendesk"). Il bot deve essere membro del canale.
# NON idempotente: non rieseguire dopo un successo, duplica i messaggi.

set -euo pipefail

TICKET="" ORG="" ASSIGNEE="" CUSTOMER=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --ticket)   TICKET="$2"; shift 2 ;;
    --org)      ORG="$2"; shift 2 ;;
    --assignee) ASSIGNEE="$2"; shift 2 ;;
    --customer) CUSTOMER="$2"; shift 2 ;;
    --) shift; break ;;
    -*) echo "ERRORE: opzione sconosciuta $1" >&2; exit 1 ;;
    *) break ;;
  esac
done

: "${TICKET:?Manca --ticket}"; : "${ORG:?Manca --org}"; : "${ASSIGNEE:?Manca --assignee}"; : "${CUSTOMER:?Manca --customer}"
if [[ $# -eq 0 ]]; then
  echo "ERRORE: serve almeno una descrizione" >&2
  exit 1
fi

# Se il token non è nell'ambiente, lo legge dal file delle credenziali (mai stampato).
ENV_FILE="${SLACK_ENV_FILE:-$HOME/.config/smartpms/slack.env}"
if [[ -z "${SLACK_BOT_TOKEN:-}" && -f "$ENV_FILE" ]]; then
  perms=$(stat -f '%Lp' "$ENV_FILE" 2>/dev/null || stat -c '%a' "$ENV_FILE")
  if [[ "$perms" != "600" && "$perms" != "400" ]]; then
    echo "ERRORE: $ENV_FILE deve avere permessi 600 (attuali: $perms)" >&2
    exit 1
  fi
  # shellcheck disable=SC1090
  source "$ENV_FILE"
fi

: "${SLACK_BOT_TOKEN:?Imposta SLACK_BOT_TOKEN o crea $ENV_FILE}"
CHANNEL="${SLACK_CHANNEL:-sall-feature-requests-zendesk}"

HEADER="Product: Smartpms
Ticket ID: ${TICKET}
Organization: ${ORG}
Assignee email: ${ASSIGNEE}
Customer email: ${CUSTOMER}"

post() {
  local text="$1"
  local payload
  payload=$(CHANNEL="$CHANNEL" TEXT="$text" python3 -c \
    'import json, os; print(json.dumps({"channel": os.environ["CHANNEL"], "text": os.environ["TEXT"]}))')
  local response
  response=$(curl -sS -X POST https://slack.com/api/chat.postMessage \
    -H "Authorization: Bearer ${SLACK_BOT_TOKEN}" \
    -H "Content-Type: application/json; charset=utf-8" \
    --data "$payload")
  if echo "$response" | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin).get("ok") else 1)'; then
    echo "OK"
  else
    echo "ERRORE: $response" >&2
    exit 1
  fi
}

count=0
for desc in "$@"; do
  printf 'Invio feature request... '
  post "${HEADER}
Description: ${desc}"
  count=$((count + 1))
  sleep 1  # limite Slack ~1 messaggio/secondo
done

echo "Fatto: ${count} feature request pubblicate su ${CHANNEL}."
