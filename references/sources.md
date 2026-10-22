# Skill Sources Reference

Known places to search for agent skills. Prefer GitHub first; use the marketplace
sites below when GitHub results are thin. When a site has no API, use WebFetch
on its search/browse page or WebSearch with the site name.

## GitHub Topics (highest yield)

| Topic | Notes |
|---|---|
| `claude-skills` | Skills using the standard SKILL.md format; largest collection |
| `agent-skills` | Generic agent skills, mixed formats |
| `claude-code` | Claude Code ecosystem incl. skills, slash commands, hooks |
| `skills` | Broad; filter results manually |

Search strategies that work well:

- `<keywords> topic:claude-skills` — direct match in the skills ecosystem
- `<keywords> SKILL.md in:path filename:SKILL.md` via code search (requires auth)
- `"awesome" <domain>` — find curated awesome-lists, then mine their links
- `skill <keywords> created:>=2025-01-01` — only recent repos

## Notable GitHub Repos

| Repo | What it is |
|---|---|
| `anthropics/skills` | Official Anthropic skills (document, pptx, xlsx, artifacts, etc.) |
| `anthropics/claude-code` | Docs + examples covering the SKILL.md format |
| awesome-lists | Search `awesome claude skills` on GitHub; several curated lists exist |

## Web Marketplaces and Directories

These change frequently; verify reachability with WebFetch before relying on them:

- skills marketplace sites indexed by searching the web for
  `claude skills marketplace` or `agent skills directory`
- Community hubs: r/ClaudeAI (Reddit) threads, Simon Willison's blog posts on skills
- Chinese ecosystem: search WorkBuddy / 技能市场 related directories via WebSearch

## Format Compatibility Notes

- Standard format: folder containing `SKILL.md` with YAML frontmatter
  (`name`, `description`) plus optional `scripts/`, `references/`, `assets/`.
  Skills in this format (Claude Code skills, Anthropic skills) work in WorkBuddy.
- Non-standard formats (plain prompt files, Cursor rules, etc.): mention them
  as "adaptation needed" and note what conversion would be required.
