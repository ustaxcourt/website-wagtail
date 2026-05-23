# Connecting the Figma MCP to Claude Code

This document explains how to connect the Figma Model Context Protocol (MCP) server to Claude Code so that Claude can read Figma design files directly during a conversation.

---

## What is an MCP?

MCP (Model Context Protocol) is an open standard that lets Claude Code talk to external tools and data sources — databases, APIs, design files, etc. — through a local server process. When a Figma MCP is configured, Claude can call `mcp__figma__get_figma_data` to pull layout, colors, typography, spacing, and component data straight from a Figma file without you having to copy-paste anything.

---

## Prerequisites

| Requirement | Notes |
|---|---|
| [Claude Code](https://claude.ai/code) installed | CLI or desktop app |
| [Node.js](https://nodejs.org/) ≥ 18 and `npx` available | `npx --version` to check |
| A Figma account with access to the target file | Free or paid |
| A Figma personal access token | See step 1 below |

---

## Step 1 — Create a Figma Personal Access Token

1. Log in to [figma.com](https://www.figma.com).
2. Click your profile avatar (top-left) → **Settings**.
3. Scroll to the **Security** section → **Personal access tokens**.
4. Click **Generate new token**, give it a name (e.g. `Claude Code MCP`), and copy the token — it starts with `figd_`.

> Keep this token private. It grants read access to all files your Figma account can see.

---

## Step 2 — Add the MCP Server to Claude Code Settings

Claude Code stores MCP configuration in `~/.claude/settings.json`. Add the following block under the `mcpServers` key:

```json
{
  "mcpServers": {
    "figma": {
      "command": "/opt/homebrew/bin/npx",
      "args": [
        "-y",
        "figma-developer-mcp",
        "--figma-api-key",
        "YOUR_FIGMA_TOKEN_HERE",
        "--stdio"
      ]
    }
  }
}
```

**Replace `YOUR_FIGMA_TOKEN_HERE`** with the token from step 1.

> **`command` path note:** The example above uses the Homebrew `npx` path (`/opt/homebrew/bin/npx`) which is common on Apple Silicon Macs. Run `which npx` in your terminal to find the correct path on your machine. Common alternatives:
> - Intel Mac / Linux: `/usr/local/bin/npx`
> - nvm: `/Users/<you>/.nvm/versions/node/<version>/bin/npx`

If `~/.claude/settings.json` does not exist yet, create it with the full structure:

```json
{
  "mcpServers": {
    "figma": {
      "command": "/opt/homebrew/bin/npx",
      "args": [
        "-y",
        "figma-developer-mcp",
        "--figma-api-key",
        "YOUR_FIGMA_TOKEN_HERE",
        "--stdio"
      ]
    }
  }
}
```

---

## Step 3 — Restart Claude Code

Close and reopen the Claude Code app or restart the CLI session. The MCP server starts automatically on the next launch.

To confirm it is running, ask Claude:

> "What Figma MCP tools do you have available?"

Claude should list `mcp__figma__get_figma_data` and `mcp__figma__download_figma_images`.

---

## Step 4 — Find Your Figma File Key and Node ID

Open the Figma file in your browser. The URL looks like:

```
https://www.figma.com/design/MpYvDySIPULl7f1RQBvb3y/US-Tax-Court-Website-Redesign?node-id=13913-8013
```

| URL segment | Value | What to give Claude |
|---|---|---|
| `/design/<key>/` | `MpYvDySIPULl7f1RQBvb3y` | **File key** |
| `node-id=13913-8013` | `13913-8013` | **Node ID** (use `-` not `%3A`) |

To get a node ID for a specific frame or component, right-click it in Figma → **Copy link** and pull the `node-id` parameter from the copied URL.

---

## Step 5 — Use It in a Conversation

Give Claude the file key and node ID and ask it to compare against your implementation:

> "The Figma file key is `MpYvDySIPULl7f1RQBvb3y` and the judge page node is `13913-8013`. Check the design and flag any visual differences from the current template."

Claude will call the Figma MCP, parse the design tree, and report specific discrepancies in colors, typography, spacing, and layout — then implement the fixes directly.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| `mcp__figma__get_figma_data` not available | Restart Claude Code; check `settings.json` syntax with `python3 -m json.tool ~/.claude/settings.json` |
| `npx: command not found` | Use the full path to `npx` — run `which npx` to find it |
| `401 Unauthorized` from Figma | Token is invalid or expired — regenerate in Figma Settings |
| `403 Forbidden` | Your Figma account does not have access to that file |
| Output truncated / saved to file | The node contains too much data — pass a more specific `nodeId` (a single frame rather than a whole page) |

---

## Security Notes

- The Figma token is stored in plaintext in `~/.claude/settings.json`. Make sure that file is not checked into version control (`~/.claude/` is typically outside any repo, but double-check).
- The token provides read access to all Figma files visible to your account. Treat it like a password.
- To revoke access at any time, return to Figma → Settings → Personal access tokens and delete the token.
