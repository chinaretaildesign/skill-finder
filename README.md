# skill-finder

A WorkBuddy / Claude Code skill that searches GitHub and other skill marketplaces for existing skills matching a stated functional requirement, so you can reuse instead of rebuild.

## What it does

Given a requirement like "I need a skill that extracts tables from PDF into Excel", it:

1. Extracts English search keywords from the request
2. Runs the GitHub Search API via `scripts/search_github.py`
3. Falls back to curated sources listed in `references/sources.md`
4. Verifies each candidate by reading its actual SKILL.md/README — not just the repo title
5. Returns a ranked shortlist with links, stars, maintenance status, and fit assessment
6. Asks before installing anything

## Usage

Trigger it naturally: "帮我找一个能做 XX 的 skill" / "find a skill for X" / "有没有现成的 skill 可以……".

Manual script use:

```bash
python scripts/search_github.py --query "pdf excel" --topic claude-skills --limit 5
python scripts/search_github.py --query "xlsx skill" --min-stars 10
python scripts/search_github.py --fetch-readme appautomaton/document-SKILLs
python scripts/search_github.py --json --limit 10 --query "pdf skill"
```

Options: `--query`, `--topic`, `--min-stars`, `--limit`, `--fetch-readme OWNER/REPO`, `--json`.

## Installation

User-level (available in all projects):

```bash
git clone https://github.com/<your-account>/skill-finder.git
cp -r skill-finder ~/.workbuddy/skills/skill-finder
```

Project-level (shared with teammates): copy it into `<workspace>/.workbuddy/skills/skill-finder`.

A session restart may be needed for the skill to be picked up.

## Requirements

- Python 3.8+ (standard library only, no dependencies)
- Optional: `GITHUB_TOKEN` environment variable to raise GitHub API rate limits from ~10 to 30 requests/minute

## Structure

```
skill-finder/
├── SKILL.md                    # skill definition and workflow
├── scripts/search_github.py    # GitHub Search API client with auto-fallback
└── references/sources.md       # known marketplaces and search strategies
```
