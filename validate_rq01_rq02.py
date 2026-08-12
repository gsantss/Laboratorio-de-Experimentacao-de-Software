import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent

JSON_FILE = (
    BASE_DIR
    / "data"
    / "repositories_100.json"
)


with open(
    JSON_FILE,
    "r",
    encoding="utf-8"
) as file:
    data = json.load(file)


repositories = data["repositories"]


print("=" * 100)
print("VALIDAÇÃO RQ01 E RQ02")
print("=" * 100)


# Amostra de 10 repositórios
sample = repositories[:10]


for repo in sample:

    print()
    print(
        f"Repositório: "
        f"{repo['name_with_owner']}"
    )

    print(
        f"RQ01 - Criado em: "
        f"{repo['created_at']}"
    )

    print(
        f"RQ01 - Idade: "
        f"{repo['age_years']} anos"
    )

    print(
        f"RQ02 - PRs aceitas: "
        f"{repo['accepted_pull_requests']}"
    )

    print("-" * 100)
