# Permissions Guide

Inspired by CJ Silverio's approach to agent permissions: pre-approve what you use constantly, deny the catastrophic, ask for everything else.

## Recommended ~/.claude/settings.json

```json
{
  "permissions": {
    "allow": [
      "Bash(cat:*)",
      "Bash(ls:*)",
      "Bash(python3:*)",
      "Bash(git:*)",
      "Bash(gh:*)",
      "Bash(jq:*)",
      "Read(*)",
      "Glob(*)",
      "Grep(*)"
    ],
    "deny": [
      "Bash(rm -rf:*)"
    ]
  }
}
```

## Philosophy

- **Allow**: Build tools, search tools, read tools, git operations — the things Claude Code uses every 30 seconds
- **Deny**: Destructive patterns that could damage your environment
- **Ask (default)**: Everything else — write operations, external API calls, etc.

## Per-Repo Overrides

You can add a `.claude/settings.json` in any repo to extend or restrict permissions for that project. The repo settings merge with your global settings.

## MCP Server Permissions

If you use MCP servers (Jira, Notion, GitHub, Slack), pre-approve read operations and require approval for writes. This matches the "read freely, write carefully" principle.
