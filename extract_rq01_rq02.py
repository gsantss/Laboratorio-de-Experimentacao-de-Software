import os
import json
import sys
import urllib.request
import urllib.error

from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# Extração individual — RQ01 (idade) e RQ02 (PRs aceitas)
# Issue #3 — Arthur Pedra
#
# Query GraphQL própria, escrita e testada de forma independente
# antes da integração ao script único do grupo (extract_repositories.py).
# ============================================================

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

SAMPLE_SIZE = 10

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_FILE = BASE_DIR / "data" / "rq01_rq02_amostra.json"


QUERY = """
query RQ01RQ02Sample($first: Int!) {

  search(
    query: "stars:>0 sort:stars-desc"
    type: REPOSITORY
    first: $first
  ) {

    nodes {

      ... on Repository {

        nameWithOwner

        # RQ01 - idade do repositório
        createdAt

        # RQ02 - total de pull requests aceitas (merged)
        pullRequests(states: [MERGED]) {
          totalCount
        }
      }
    }
  }

  rateLimit {
    cost
    remaining
  }
}
"""


def get_github_token():

    token = os.getenv("GITHUB_TOKEN")

    if not token:
        print("ERRO: defina a variável de ambiente GITHUB_TOKEN.")
        sys.exit(1)

    return token


def run_query(token, first):

    payload = json.dumps({
        "query": QUERY,
        "variables": {"first": first}
    }).encode("utf-8")

    request = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "LAB01-RQ01-RQ02"
        }
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def process(repo, collection_date):

    created_at = datetime.fromisoformat(
        repo["createdAt"].replace("Z", "+00:00")
    )

    age_days = (collection_date - created_at).days
    age_years = round(age_days / 365.25, 2)

    return {
        "name_with_owner": repo["nameWithOwner"],
        "created_at": repo["createdAt"],
        "age_days": age_days,
        "age_years": age_years,
        "accepted_pull_requests": repo["pullRequests"]["totalCount"],
    }


def main():

    token = get_github_token()

    result = run_query(token, SAMPLE_SIZE)

    if "errors" in result:
        print(json.dumps(result["errors"], indent=2, ensure_ascii=False))
        raise RuntimeError("A API GraphQL retornou erros.")

    nodes = result["data"]["search"]["nodes"]

    collection_date = datetime.now(timezone.utc)

    repositories = [process(repo, collection_date) for repo in nodes]

    print("=" * 80)
    print(f"EXTRAÇÃO INDIVIDUAL - RQ01 (idade) e RQ02 (PRs aceitas)")
    print(f"Amostra: {len(repositories)} repositórios")
    print("=" * 80)

    for repo in repositories:
        print()
        print(repo["name_with_owner"])
        print(f"  RQ01 - Criado em: {repo['created_at']}  ({repo['age_years']} anos)")
        print(f"  RQ02 - PRs aceitas: {repo['accepted_pull_requests']}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(
            {
                "collected_at": collection_date.isoformat(),
                "sample_size": len(repositories),
                "repositories": repositories,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(f"Salvo em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
