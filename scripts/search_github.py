#!/usr/bin/env python3
"""Search GitHub for agent skills matching a functional requirement.

Uses the GitHub REST Search API (repositories endpoint). Works without
authentication (rate limit: ~10 requests/minute); set the GITHUB_TOKEN
environment variable to raise limits to 30 requests/minute.

Usage:
  python search_github.py --query "pdf table extraction" [--topic claude-skills]
                          [--min-stars 5] [--limit 10]
                          [--fetch-readme owner/repo] [--json]

Examples:
  python search_github.py --query "excel report generation skill"
  python search_github.py --topic claude-skills --min-stars 10 --limit 15
  python search_github.py --fetch-readme anthropics/skills
"""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API_BASE = "https://api.github.com"
USER_AGENT = "skill-finder/1.0"


def _request(url: str) -> dict:
    """Perform a GET request against the GitHub API and return parsed JSON."""
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 403:
            # Rate limit or abuse detection; report remaining reset time.
            reset = exc.headers.get("X-RateLimit-Reset", "")
            msg = "GitHub API rate limit hit"
            if reset:
                wait = max(0, int(reset) - int(time.time()))
                msg += f" (resets in ~{wait}s); retry later or set GITHUB_TOKEN"
            raise SystemExit(f"ERROR: {msg}")
        if exc.code == 422:
            raise SystemExit("ERROR: query was invalid or too complex; simplify keywords")
        raise SystemExit(f"ERROR: GitHub API returned HTTP {exc.code} for {url}")
    except urllib.error.URLError as exc:
        raise SystemExit(f"ERROR: network problem reaching GitHub: {exc.reason}")


def search_repositories(query: str, min_stars: int, limit: int) -> list:
    """Search GitHub repositories; return normalized result dicts.

    Note: the stars qualifier must come BEFORE topic: in the query string,
    otherwise GitHub returns zero results (verified quirk of the Search API).
    """
    if min_stars > 0:
        q = f"stars:>={min_stars} {query.strip()}"
    else:
        q = query.strip()
    params = urllib.parse.urlencode(
        {"q": q, "sort": "best-match", "order": "desc", "per_page": min(limit, 50)}
    )
    data = _request(f"{API_BASE}/search/repositories?{params}")
    results = []
    for item in data.get("items", []):
        results.append(
            {
                "full_name": item["full_name"],
                "url": item["html_url"],
                "description": (item.get("description") or "").strip(),
                "stars": item["stargazers_count"],
                "updated_at": item.get("pushed_at", "")[:10],
                "topics": item.get("topics", []),
                "language": item.get("language"),
            }
        )
    return results


def fetch_readme(repo: str) -> str:
    """Fetch the README (or SKILL.md if present) of a repo as plain text."""
    params = urllib.parse.urlencode({"ref": ""})
    data = _request(f"{API_BASE}/repos/{repo}/readme")
    content = base64.b64decode(data.get("content", "")).decode("utf-8", errors="replace")
    # Prefer SKILL.md content when the README merely links to it.
    if "SKILL.md" in content and len(content) < 3000:
        skill_url = f"{API_BASE}/repos/{repo}/contents/SKILL.md"
        try:
            skill = _request(skill_url)
            skill_text = base64.b64decode(skill.get("content", "")).decode(
                "utf-8", errors="replace"
            )
            if skill_text.strip():
                return f"===== SKILL.md ({repo}) =====\n{skill_text}"
        except SystemExit:
            pass
    return f"===== README ({repo}) =====\n{content}"


def _print_results(results: list, as_json: bool) -> None:
    if as_json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    if not results:
        print("No matching repositories found. Try broader or English keywords.")
        return
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['full_name']}  ★{r['stars']}  (pushed {r['updated_at']})")
        print(f"   {r['url']}")
        if r["description"]:
            print(f"   {r['description'][:160]}")
        if r["topics"]:
            print(f"   topics: {', '.join(r['topics'][:8])}")
        print()


def _query_variants(query: str) -> list:
    """Build progressively simpler queries for automatic fallback.

    GitHub's unqualified search requires every term to match, so long
    natural-language queries almost always return zero results. When the
    original query fails, retry with shorter, higher-signal variants
    (verified behaviour: 1-2 word queries work, 5+ word queries do not).
    """
    words = [w for w in query.split() if w.lower() not in {"skill", "skills", "the", "for", "a"}]
    # Bias each variant toward skill repositories so the fallback does not
    # drift into generic libraries that merely share the domain words.
    variants = []
    if len(words) >= 2:
        variants.append(f"{words[0]} {words[1]} skill")
    if words:
        variants.append(f"{words[0]} skill")
        variants.append(" ".join(words[:2]))
        variants.append(words[0])
    variants.append("skill")  # last resort: broad ecosystem sweep
    seen, unique = set(), []
    for v in variants:
        if v and v not in seen:
            seen.add(v)
            unique.append(v)
    return unique


def main() -> None:
    parser = argparse.ArgumentParser(description="Search GitHub for matching skills")
    parser.add_argument("--query", help="search keywords, e.g. 'pdf table extraction'")
    parser.add_argument("--topic", default=None, help="GitHub topic, e.g. claude-skills")
    parser.add_argument("--min-stars", type=int, default=0)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--fetch-readme", metavar="OWNER/REPO", help="fetch repo README/SKILL.md")
    parser.add_argument("--json", action="store_true", help="output raw JSON")
    args = parser.parse_args()

    if args.fetch_readme:
        print(fetch_readme(args.fetch_readme))
        return

    if not args.query and not args.topic:
        parser.error("either --query or --topic is required (or use --fetch-readme)")

    parts = []
    if args.query:
        parts.append(args.query)
    if args.topic:
        parts.append(f"topic:{args.topic}")

    primary = " ".join(parts)
    results = search_repositories(primary, args.min_stars, args.limit)
    if results:
        _print_results(results, args.json)
        return

    # Automatic fallback: the original query found nothing, retry simplified.
    if args.query:
        if not args.json:
            print(f"No results for: {primary}\nRetrying with simplified queries...\n")
        for variant in _query_variants(args.query):
            v_parts = [variant] + (["topic:" + args.topic] if args.topic else [])
            results = search_repositories(" ".join(v_parts), args.min_stars, args.limit)
            if results:
                if not args.json:
                    print(f"Results via simplified query: {variant}\n")
                _print_results(results, args.json)
                return

    _print_results([], args.json)


if __name__ == "__main__":
    main()
