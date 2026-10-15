# Distributing smartpms-support to the Support team

Repo: `smartpricing/smartpms-support-plugin` (private, github.com). Marketplace name: `smartness-support`. Plugin: `smartpms-support`.

`plugin.json` and `marketplace.json` have no `version` field on purpose: the commit SHA is the version, so **every push to `main` is a new release**. Don't add a version back, or updates stop until you bump it by hand.

## A. Org catalog on claude.ai (preferred)

Needs an Owner/Admin of the claude.ai organization.

1. claude.ai → **Organization settings** → **Plugins & skills**.
2. **Add** → **Sync from GitHub**.
3. When asked, install the **Claude GitHub App** on the GitHub org that owns the repo and grant it access to **only** `smartpricing/smartpms-support-plugin` (read access is enough).
4. Pick the repo and the `main` branch. The marketplace root is the repo root (where `.claude-plugin/marketplace.json` is).
5. Turn **Sync automatically** on, so each push to `main` is picked up without touching the admin page again.
6. For `smartpms-support` set availability to **Installed by default** (scope: the Support team / group, if your plan lets you limit it; otherwise the whole org, and tell non-Support people they can disable it).
7. Save. Check the plugin card shows the latest commit SHA.

### Test before telling the team

Support for org-synced plugins in the **desktop app Code tab** is not documented. Before announcing:

1. On **one colleague's** machine: quit and reopen the Claude desktop app, open a Code session.
2. Ask: *"che skill hai a disposizione?"* — `smartpms-support:smartpms-troubleshooting` must be in the list.
3. Push a trivial change (e.g. a typo fix in `README.md`), wait for the sync, restart the app on that machine and check the change arrived.

If step 2 fails, use plan B.

## B. Fallback: marketplace + autoUpdate via managed settings

Use this if the Code tab doesn't pick up the org catalog. It works with any Claude Code client (desktop Code tab, CLI, IDE).

Add this to the **server-managed settings** (claude.ai admin console → Claude Code → Managed settings), or, without admin access, to each agent's `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "smartness-support": {
      "source": { "source": "github", "repo": "smartpricing/smartpms-support-plugin" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": {
    "smartpms-support@smartness-support": true
  }
}
```

Requirements on each agent's machine, because the repo is private:

- A GitHub account that is a member of the org with read access to the repo.
- `gh auth login` done once (git uses those credentials when Claude Code clones/pulls the marketplace).
- For updates in the background at startup, a `GITHUB_TOKEN` (or `GH_TOKEN`) with read access in the environment; without it updates still happen, but only when the agent runs `/plugin marketplace update smartness-support` from a terminal `claude` session.

Manual install for a single person (same result, no managed settings), from a terminal `claude` session:

```
/plugin marketplace add smartpricing/smartpms-support-plugin
/plugin install smartpms-support@smartness-support
```

## C. Slack bot token for everyone (managed settings)

The feature-request script reads `SLACK_BOT_TOKEN` from the environment first, then from `~/.config/smartpms/slack.env` as a fallback. To spare each agent that file, an admin sets the token once in the **server-managed settings** (claude.ai admin console → Claude Code → Managed settings), next to anything already there (e.g. plan B):

```json
{
  "env": {
    "SLACK_BOT_TOKEN": "xoxb-…"
  }
}
```

- Type the real token **only** in the admin console. Never commit it to this repo, paste it in a chat, or put it in a ticket.
- Every agent can read the value on their own machine (same exposure as the per-agent file today). If someone leaves the team or the token leaks: rotate it in Slack, then update this one value.
- Clients get the new value at their next app start. Check on one machine with `[ -n "$SLACK_BOT_TOKEN" ] && echo ok` (prints ok, never the token).
- Agents not covered by the managed settings keep using the file (see the plugin README, setup step 4).

## Releasing a change

```bash
cd "/Users/wbgne/Projects/MCP Brainrot/plugins"
git add -A && git commit -m "team-rules: <cosa cambia>" && git push
```

Clients pick it up at the next start of the app (A: after the catalog sync; B: after the marketplace auto-update). Before pushing, validate:

```bash
"/Users/wbgne/Library/Application Support/Claude/claude-code/2.1.295/9d6405864fdc/claude.app/Contents/MacOS/claude" plugin validate .
```

(The only expected warning is "No version specified" — that is intentional.)
