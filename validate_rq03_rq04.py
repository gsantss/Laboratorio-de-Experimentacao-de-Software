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
print("VALIDAÇÃO RQ03 E RQ04")
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
        f"RQ03 - Releases: "
        f"{repo['releases']}"
    )

    print(
        f"RQ04 - Última atualização: "
        f"{repo['updated_at']}"
    )

    print(
        f"RQ04 - Dias desde atualização: "
        f"{repo['days_since_last_update']}"
    )

    print("-" * 100)