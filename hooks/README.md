# Hooks

Claude Code hooks are "set it and forget it" automations that run on specific events (pre-commit, post-tool-call, session start, etc.).

Hooks are where the real compound automation lives — skills require invocation, hooks just happen.

## How to Install a Hook

Add the hook configuration to your `~/.claude/settings.json` under the `hooks` key. See Claude Code docs for the full hook specification.

## Available Hooks

*Add hooks here as the library grows.*

## Ideas for Hooks

- **Pre-commit**: Validate YAML frontmatter on all skill files
- **Session start**: Load latest catalog and remind user of new skills
- **Post-tool-call**: Auto-format structured outputs
