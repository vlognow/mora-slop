# Onboarding — Department of Vibes

## 5-Minute Setup

1. **Clone the repo**
   ```bash
   git clone git@github.com:butchsonik/department-of-vibes.git
   ```

2. **Install skills**
   ```bash
   cd department-of-vibes && ./install.sh
   ```
   This symlinks all skills into `~/.claude/skills/`. They auto-load in every Claude Code session.

3. **Try a skill**
   Open Claude Code in any project and say:
   > "Generate a PRD for [your feature idea]"

   The `pm-prd-generator` skill will activate automatically.

4. **Browse the catalog**
   Open `catalog.yaml` to see all available skills, or ask Claude:
   > "What skills are available in department-of-vibes for [my task]?"

## Your First Contribution

1. Open Claude Code in this repo
2. Type `/new-skill`
3. Follow the guided workflow
4. Open a PR

Or see [CONTRIBUTING.md](../CONTRIBUTING.md) for the manual flow.

## Recommended Claude Code Settings

See [PERMISSIONS-GUIDE.md](PERMISSIONS-GUIDE.md) for a complete recommended setup.
