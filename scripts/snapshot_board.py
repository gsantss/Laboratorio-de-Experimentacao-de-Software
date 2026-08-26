import os
import csv
import json
import sys
import urllib.request
import urllib.error

from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# Snapshot de fechamento de sprint (Parte 2, regra 6)
#
# Exporta os itens do GitHub Projects (v2) do grupo e o status
# atual de cada um para um arquivo CSV. Rodar ao final de cada
# sprint (Lab01S01, S02, S03...) para acumular a série histórica
# usada nos Labs 04 e 05.
# ============================================================

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

PROJECT_OWNER = "gsantss"
PROJECT_NUMBER = 2

# Trocar a cada sprint antes de rodar.
SPRINT_LABEL = "Lab01S02"

BASE_DIR = Path(__file__).resolve().parent

OUTPUT_FILE = BASE_DIR / "data" / f"snapshot_board_{SPRINT_LABEL}.csv"


QUERY = """
query($login: String!, $number: Int!, $after: String) {
  user(login: $login) {
    projectV2(number: $number) {
      title
      items(first: 50, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          content {
            ... on Issue {
              number
              title
              state
              repository { nameWithOwner }
              assignees(first: 5) { nodes { login } }
            }
            ... on PullRequest {
              number
              title
              state
              repository { nameWithOwner }
              assignees(first: 5) { nodes { login } }
            }
          }
          status: fieldValueByName(name: "Status") {
            ... on ProjectV2ItemFieldSingleSelectValue {
              name
            }
          }
        }
      }
    }
  }
}
"""


def get_github_token():
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("ERRO: defina a variável de ambiente GITHUB_TOKEN.")
        sys.exit(1)
    return token


def run_query(token, after=None):
    variables = {
        "login": PROJECT_OWNER,
        "number": PROJECT_NUMBER,
        "after": after,
    }

    payload = json.dumps({"query": QUERY, "variables": variables}).encode("utf-8")

    request = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "LAB01-SNAPSHOT-BOARD",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def fetch_all_items(token):
    items = []
    cursor = None

    while True:
        result = run_query(token, cursor)

        if "errors" in result:
            print(json.dumps(result["errors"], indent=2, ensure_ascii=False))
            raise RuntimeError("A API GraphQL retornou erros.")

        project = result["data"]["user"]["projectV2"]
        page = project["items"]

        items.extend(page["nodes"])

        if not page["pageInfo"]["hasNextPage"]:
            break

        cursor = page["pageInfo"]["endCursor"]

    return project["title"], items


def process_item(item, snapshot_date):
    content = item.get("content") or {}

    assignees = ",".join(
        a["login"] for a in content.get("assignees", {}).get("nodes", [])
    ) or "SEM_ASSIGNEE"

    return {
        "snapshot_date": snapshot_date,
        "sprint": SPRINT_LABEL,
        "number": content.get("number", ""),
        "title": content.get("title", ""),
        "repository": content.get("repository", {}).get("nameWithOwner", ""),
        "state": content.get("state", ""),
        "status_column": (item.get("status") or {}).get("name", "SEM_STATUS"),
        "assignees": assignees,
    }


def save_csv(rows):
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "snapshot_date", "sprint", "number", "title",
        "repository", "state", "status_column", "assignees",
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main():
    print("=" * 80)
    print(f"SNAPSHOT DO BOARD - {SPRINT_LABEL}")
    print("=" * 80)

    token = get_github_token()

    snapshot_date = datetime.now(timezone.utc).isoformat()

    project_title, items = fetch_all_items(token)

    print(f"\nProject: {project_title}")
    print(f"Itens encontrados: {len(items)}\n")

    rows = [process_item(item, snapshot_date) for item in items]

    for row in rows:
        print(
            f"#{row['number']:<4} [{row['status_column']:<12}] "
            f"{row['title']:<55} ({row['assignees']})"
        )

    save_csv(rows)

    print(f"\nSalvo em: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
