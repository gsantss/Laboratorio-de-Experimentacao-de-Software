"""
LAB01S01 - Extração das métricas RQ05, RQ06 e RQ07 (integrante C).

Coleta os 100 repositórios mais populares do GitHub (por estrelas) via API
GraphQL própria e salva apenas as minhas métricas em
data/repositories_rq05_rq06_rq07.json:

    RQ05 - linguagem primária (comparada ao TIOBE Index de ago/2026 como
           referência de "linguagens mais populares": https://www.tiobe.com/tiobe-index/).
    RQ06 - razão entre issues fechadas e total de issues.
    RQ07 - PRs aceitas, releases e dias desde o último push (por linguagem).
"""

import os
import sys
import json
import statistics
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

TOTAL = 100
BATCH = 10
OUTPUT = Path(__file__).resolve().parent / "data" / "repositories_rq05_rq06_rq07.json"

QUERY = """
query($first: Int!, $after: String) {
  search(query: "stars:>0 sort:stars-desc", type: REPOSITORY, first: $first, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes { ... on Repository {
      nameWithOwner url stargazerCount pushedAt
      primaryLanguage { name }                              # RQ05
      issues(first: 1) { totalCount }                       # RQ06
      closedIssues: issues(first: 1, states: [CLOSED]) { totalCount }
      pullRequests(first: 1, states: [MERGED]) { totalCount }   # RQ07 (RQ02)
      releases(first: 1) { totalCount }                         # RQ07 (RQ03)
    } }
  }
}
"""


def graphql(token, first, after):
    """Executa a query GraphQL e devolve o JSON já decodificado."""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"first": first, "after": after}}).encode(),
        method="POST",
        headers={"Authorization": f"Bearer {token}", "User-Agent": "lab01-rq05-06-07"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.load(resp)
    if "errors" in result:
        sys.exit(json.dumps(result["errors"], indent=2, ensure_ascii=False))
    return result["data"]["search"]


def parse(repo, now):
    """Extrai de um repositório apenas os campos das RQ05, RQ06 e RQ07."""
    total = repo["issues"]["totalCount"]
    closed = repo["closedIssues"]["totalCount"]
    pushed = datetime.fromisoformat(repo["pushedAt"].replace("Z", "+00:00"))
    return {
        "name_with_owner": repo["nameWithOwner"],
        "url": repo["url"],
        "stars": repo["stargazerCount"],
        "primary_language": (repo["primaryLanguage"] or {}).get("name"),   # RQ05
        "total_issues": total,                                             # RQ06
        "closed_issues": closed,
        "closed_issues_percentage": round(closed / total * 100, 2) if total else None,
        "accepted_pull_requests": repo["pullRequests"]["totalCount"],      # RQ07
        "releases": repo["releases"]["totalCount"],
        "days_since_last_push": (now - pushed).days,
    }


def summarize_rq07(repos):
    """Mediana de PRs, releases e dias desde o último push, por linguagem."""
    groups = {}
    for r in repos:
        groups.setdefault(r["primary_language"] or "Sem linguagem", []).append(r)
    summary = [{
        "language": lang,
        "repository_count": len(rs),
        "median_accepted_pull_requests": statistics.median(x["accepted_pull_requests"] for x in rs),
        "median_releases": statistics.median(x["releases"] for x in rs),
        "median_days_since_last_push": statistics.median(x["days_since_last_push"] for x in rs),
    } for lang, rs in groups.items()]
    return sorted(summary, key=lambda s: s["repository_count"], reverse=True)


def main():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        sys.exit('ERRO: defina o token com  $env:GITHUB_TOKEN = "SEU_TOKEN"')

    now = datetime.now(timezone.utc)
    repos, cursor = [], None
    while len(repos) < TOTAL:
        page = graphql(token, min(BATCH, TOTAL - len(repos)), cursor)
        repos += [parse(r, now) for r in page["nodes"] if r]
        print(f"coletados {len(repos)}/{TOTAL}")
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps({
        "metadata": {
            "collected_at": now.isoformat(),
            "repository_count": len(repos),
            "research_questions": ["RQ05", "RQ06", "RQ07"],
        },
        "rq07_summary_by_language": summarize_rq07(repos),
        "repositories": repos,
    }, indent=4, ensure_ascii=False), encoding="utf-8")
    print(f"OK -> {OUTPUT}")


if __name__ == "__main__":
    main()
