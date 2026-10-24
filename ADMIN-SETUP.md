# Distributing smartpms-support to the Support team

Repo: `wbgne/smartpms-support-plugin` (**public**, github.com). Marketplace name: `smartness-support`. Plugin: `smartpms-support`.

`plugin.json` and `marketplace.json` have no `version` field on purpose: the commit SHA is the version, so **every push to `main` is a new release**. Don't add a version back, or updates stop until you bump it by hand.

Because the repo is public, it can't be synced into the claude.ai org catalog (that sync only accepts private or internal repos). Everyone installs it from GitHub as a marketplace with auto-update on. No GitHub account, token or app is needed on the agents' machines.

**Never commit secrets here**: the Slack bot token lives in 1Password (section B), never in this repo.

## A. Install with auto-update

### Each agent (no admin needed)

1. Add this to `~/.claude/settings.json` (merge with what's already there):

   ```json
   {
     "extraKnownMarketplaces": {
       "smartness-support": {
         "source": { "source": "github", "repo": "wbgne/smartpms-support-plugin" },
         "autoUpdate": true
       }
     },
     "enabledPlugins": {
       "smartpms-support@smartness-support": true
     }
   }
   ```

2. Quit and reopen the Claude desktop app, open a Code session and ask *"che skill hai a disposizione?"*: `smartpms-support:smartpms-troubleshooting` must be in the list.

Same result by hand, from a terminal `claude` session:

```
/plugin marketplace add wbgne/smartpms-support-plugin
/plugin install smartpms-support@smartness-support
```

Then turn on auto-update for `smartness-support` in `/plugin` → Marketplaces (or add the settings above).

### For everyone at once (optional, claude.ai Owner/Admin)

Put the same JSON in the **server-managed settings** (claude.ai admin console → Claude Code → Managed settings) instead of each agent's file.

### Test before telling the team

On **one colleague's** machine: do step A, check the skill is listed, then push a trivial change (e.g. a typo fix in `smartpms-support/README.md`), restart their app and check the change arrived. If it didn't, run `/plugin marketplace update smartness-support` from a terminal `claude` session and tell Joseph.

## B. Slack bot token

The feature-request script reads `SLACK_BOT_TOKEN` from the environment first, then from `~/.config/smartpms/slack.env`.

- The token is in **1Password**: vault `Shared`, item `support-copilot - Slack`, field `credential`. It's a copy of the item the Support Copilot deploy reads from vault `Support copilot` (`deploy/sync-secrets.sh`): same token, so when you rotate it update both items. Each agent copies it from there into the file (plugin README, setup step 4). Never in this repo, a chat or a ticket.
- Optional, if a claude.ai admin manages settings for the team: set it once there instead, and agents can skip the file:

  ```json
  { "env": { "SLACK_BOT_TOKEN": "xoxb-…" } }
  ```

  Type the real value only in the admin console.
- If someone leaves the team or the token leaks: rotate it in Slack, update both 1Password items (Shared and Support copilot) and the managed setting if used, and tell agents to update their file.
- Check on a machine without printing it: `[ -n "$SLACK_BOT_TOKEN" ] || [ -f ~/.config/smartpms/slack.env ] && echo ok`.

## Releasing a change

```bash
cd "/Users/wbgne/Projects/MCP Brainrot/plugins"
git add -A && git commit -m "team-rules: <cosa cambia>" && git pull --rebase && git push
```

Pull before pushing: pull requests merged on GitHub aren't in this local copy until you pull, and the push is refused without them.

### Reviewing colleagues' pull requests

Colleagues propose changes with pull requests from their own fork (`CONTRIBUTING.md`); nobody else has write access, so nothing reaches `main` until you merge. Review on github.com (Pull requests tab), or ask Claude here to list them, show the diff and merge on your ok (`gh pr list` / `gh pr diff` / `gh pr merge` with the `wbgne` login). Before merging, check: right file and section, Italian, no tokens or customer personal data (the repo and its pull requests are public).

The push goes to `wbgne` over HTTPS with that account's `gh` login (a credential helper set only in this repo's `.git/config`; the SSH key on this Mac belongs to `wbgne59100`). Clients pick the change up at their next app start. Before pushing, validate:

```bash
cd "/Users/wbgne/Projects/MCP Brainrot/plugins" && "$(ls -d "$HOME/Library/Application Support/Claude/claude-code/"*/*/claude.app/Contents/MacOS/claude | tail -1)" plugin validate .
```

(The path picks the app's installed `claude`, whose version folder changes with every app update. Run it from `plugins/`: elsewhere it validates the wrong folder. The only expected warning is "No version specified": that is intentional.)
