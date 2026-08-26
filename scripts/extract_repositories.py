import os
import csv
import json
import sys
import time
import urllib.request
import urllib.error

from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# CONFIGURAÇÕES
# ============================================================

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

TOTAL_REPOSITORIES = 1000

# Quantidade por requisição.
# Mantemos baixo para evitar uma query muito pesada.
BATCH_SIZE = 10

MAX_RETRIES = 3

RETRY_WAIT_SECONDS = 5


BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "data"

OUTPUT_FILE = (
    OUTPUT_DIR /
    "repositories_1000.json"
)

CSV_OUTPUT_FILE = (
    OUTPUT_DIR /
    "repositories_1000.csv"
)


# ============================================================
# QUERY GRAPHQL
# ============================================================

QUERY = """
query TopRepositories(
    $first: Int!,
    $after: String
) {

  search(
    query: "stars:>0 sort:stars-desc"
    type: REPOSITORY
    first: $first
    after: $after
  ) {

    repositoryCount

    pageInfo {
      hasNextPage
      endCursor
    }

    nodes {

      ... on Repository {

        # Identificação
        name
        nameWithOwner
        url

        # Popularidade
        stargazerCount

        # ====================================================
        # RQ01
        # Sistemas populares são maduros/antigos?
        # ====================================================

        createdAt

        # ====================================================
        # RQ02
        # Sistemas populares recebem muita contribuição externa?
        # ====================================================

        pullRequests(
          first: 1
          states: [MERGED]
        ) {
          totalCount
        }

        # ====================================================
        # RQ03
        # Sistemas populares lançam releases com frequência?
        # ====================================================

        releases(
          first: 1
        ) {
          totalCount
        }

        # ====================================================
        # RQ04
        # Sistemas populares são atualizados com frequência?
        # ====================================================

        updatedAt

        # ====================================================
        # RQ05
        # Linguagem principal
        # ====================================================

        primaryLanguage {
          name
        }

        # ====================================================
        # RQ06
        # Percentual de issues fechadas
        # ====================================================

        issues(
          first: 1
        ) {
          totalCount
        }

        closedIssues: issues(
          first: 1
          states: [CLOSED]
        ) {
          totalCount
        }
      }
    }
  }

  rateLimit {
    cost
    remaining
    resetAt
  }
}
"""


# ============================================================
# TOKEN
# ============================================================

def get_github_token():

    token = os.getenv("GITHUB_TOKEN")

    if not token:

        print()
        print("ERRO:")
        print(
            "A variável de ambiente "
            "GITHUB_TOKEN não foi configurada."
        )

        print()
        print("No PowerShell:")
        print(
            '$env:GITHUB_TOKEN="SEU_TOKEN"'
        )

        sys.exit(1)

    return token


# ============================================================
# CHAMADA GRAPHQL
# ============================================================

def execute_graphql(
    token,
    first,
    after=None
):

    variables = {
        "first": first,
        "after": after
    }

    payload = json.dumps({
        "query": QUERY,
        "variables": variables
    }).encode("utf-8")

    request = urllib.request.Request(
        GITHUB_GRAPHQL_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization":
                f"Bearer {token}",

            "Content-Type":
                "application/json",

            "User-Agent":
                "LAB01-Experimentacao-Software"
        }
    )

    # --------------------------------------------------------
    # Retry
    # --------------------------------------------------------

    for attempt in range(
        1,
        MAX_RETRIES + 1
    ):

        try:

            with urllib.request.urlopen(
                request,
                timeout=60
            ) as response:

                result = json.load(
                    response
                )

                return result

        except urllib.error.HTTPError as error:

            body = (
                error
                .read()
                .decode(
                    "utf-8",
                    errors="replace"
                )
            )

            print()
            print(
                f"Erro HTTP "
                f"{error.code}"
            )

            print(body)

            # 502 / 503 / 504 podem ser transitórios
            if (
                error.code
                in [502, 503, 504]
                and
                attempt < MAX_RETRIES
            ):

                print(
                    f"Tentativa "
                    f"{attempt}/"
                    f"{MAX_RETRIES}"
                )

                print(
                    f"Aguardando "
                    f"{RETRY_WAIT_SECONDS}s..."
                )

                time.sleep(
                    RETRY_WAIT_SECONDS
                )

                continue

            raise

        except urllib.error.URLError as error:

            print()
            print(
                "Erro de conexão:"
            )

            print(error)

            if attempt < MAX_RETRIES:

                time.sleep(
                    RETRY_WAIT_SECONDS
                )

                continue

            raise


# ============================================================
# VALIDAR RESPOSTA
# ============================================================

def validate_response(result):

    if "errors" in result:

        print()
        print("=" * 80)
        print("ERRO GRAPHQL")
        print("=" * 80)

        print(
            json.dumps(
                result["errors"],
                indent=4,
                ensure_ascii=False
            )
        )

        raise RuntimeError(
            "A API GraphQL retornou erros."
        )

    if "data" not in result:

        raise RuntimeError(
            "Resposta da API sem campo 'data'."
        )


# ============================================================
# TRATAR REPOSITÓRIO
# ============================================================

def process_repository(
    repo,
    position,
    collection_date
):

    # --------------------------------------------------------
    # RQ01
    # Idade
    # --------------------------------------------------------

    created_at = datetime.fromisoformat(
        repo["createdAt"]
        .replace(
            "Z",
            "+00:00"
        )
    )

    age_days = (
        collection_date -
        created_at
    ).days

    age_years = round(
        age_days / 365.25,
        2
    )


    # --------------------------------------------------------
    # RQ04
    # Tempo desde última atualização
    # --------------------------------------------------------

    updated_at = datetime.fromisoformat(
        repo["updatedAt"]
        .replace(
            "Z",
            "+00:00"
        )
    )

    days_since_last_update = (
        collection_date -
        updated_at
    ).days


    # --------------------------------------------------------
    # RQ05
    # Linguagem
    # --------------------------------------------------------

    language = repo.get(
        "primaryLanguage"
    )

    if language:

        primary_language = (
            language["name"]
        )

    else:

        primary_language = None


    # --------------------------------------------------------
    # RQ06
    # Issues
    # --------------------------------------------------------

    total_issues = (
        repo["issues"]
        ["totalCount"]
    )

    closed_issues = (
        repo["closedIssues"]
        ["totalCount"]
    )


    if total_issues > 0:

        closed_issues_ratio = (
            closed_issues /
            total_issues
        )

        closed_issues_percentage = round(
            closed_issues_ratio * 100,
            2
        )

    else:

        closed_issues_ratio = None
        closed_issues_percentage = None


    # --------------------------------------------------------
    # Registro final
    # --------------------------------------------------------

    return {

        "position":
            position,

        "name":
            repo["name"],

        "name_with_owner":
            repo["nameWithOwner"],

        "url":
            repo["url"],

        "stars":
            repo["stargazerCount"],


        # RQ01
        "created_at":
            repo["createdAt"],

        "age_days":
            age_days,

        "age_years":
            age_years,


        # RQ02
        "accepted_pull_requests":
            repo[
                "pullRequests"
            ][
                "totalCount"
            ],


        # RQ03
        "releases":
            repo[
                "releases"
            ][
                "totalCount"
            ],


        # RQ04
        "updated_at":
            repo["updatedAt"],

        "days_since_last_update":
            days_since_last_update,


        # RQ05
        "primary_language":
            primary_language,


        # RQ06
        "total_issues":
            total_issues,

        "closed_issues":
            closed_issues,

        "closed_issues_ratio":
            closed_issues_ratio,

        "closed_issues_percentage":
            closed_issues_percentage
    }


# ============================================================
# EXTRAÇÃO
# ============================================================

def extract_repositories(token):

    repositories = []

    cursor = None

    collection_date = (
        datetime.now(
            timezone.utc
        )
    )

    batch_number = 1


    while (
        len(repositories)
        <
        TOTAL_REPOSITORIES
    ):

        remaining = (
            TOTAL_REPOSITORIES -
            len(repositories)
        )

        current_batch_size = min(
            BATCH_SIZE,
            remaining
        )


        print()
        print("=" * 80)

        print(
            f"LOTE {batch_number}"
        )

        print("=" * 80)

        print(
            f"Solicitando "
            f"{current_batch_size} "
            f"repositórios..."
        )


        result = execute_graphql(
            token=token,
            first=current_batch_size,
            after=cursor
        )


        validate_response(
            result
        )


        search_data = (
            result["data"]["search"]
        )

        nodes = (
            search_data["nodes"]
        )


        # ----------------------------------------------------
        # Processar itens
        # ----------------------------------------------------

        for repo in nodes:

            if repo is None:
                continue

            position = (
                len(repositories)
                + 1
            )


            processed = (
                process_repository(
                    repo,
                    position,
                    collection_date
                )
            )


            repositories.append(
                processed
            )


            print(
                f"["
                f"{position:03d}/"
                f"{TOTAL_REPOSITORIES}"
                f"] "
                f"{processed['name_with_owner']}"
            )


        # ----------------------------------------------------
        # Rate Limit
        # ----------------------------------------------------

        rate_limit = (
            result["data"]
            ["rateLimit"]
        )


        print()

        print(
            "Rate limit:"
        )

        print(
            f"  custo: "
            f"{rate_limit['cost']}"
        )

        print(
            f"  restante: "
            f"{rate_limit['remaining']}"
        )


        # ----------------------------------------------------
        # Paginação
        # ----------------------------------------------------

        page_info = (
            search_data["pageInfo"]
        )

        cursor = (
            page_info["endCursor"]
        )


        if not page_info[
            "hasNextPage"
        ]:

            break


        batch_number += 1


    return repositories


# ============================================================
# SALVAR JSON
# ============================================================

def save_json(repositories):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    output = {

        "metadata": {

            "collected_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "repository_count":
                len(repositories),

            "requested_count":
                TOTAL_REPOSITORIES,

            "batch_size":
                BATCH_SIZE,

            "search_query":
                "stars:>0 sort:stars-desc"
        },

        "repositories":
            repositories
    }


    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )


# ============================================================
# SALVAR CSV - LAB01S02
# ============================================================

def save_csv(repositories):

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not repositories:
        print(
            "ATENÇÃO: nenhum repositório "
            "disponível para exportação CSV."
        )
        return

    fieldnames = [
        "position",
        "name",
        "name_with_owner",
        "url",
        "stars",

        # RQ01
        "created_at",
        "age_days",
        "age_years",

        # RQ02
        "accepted_pull_requests",

        # RQ03
        "releases",

        # RQ04
        "updated_at",
        "days_since_last_update",

        # RQ05
        "primary_language",

        # RQ06
        "total_issues",
        "closed_issues",
        "closed_issues_ratio",
        "closed_issues_percentage"
    ]

    with open(
        CSV_OUTPUT_FILE,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(repositories)

    print()
    print(
        f"CSV gerado:\n"
        f"{CSV_OUTPUT_FILE}"
    )


# ============================================================
# VALIDAÇÃO
# ============================================================

def validate_results(
    repositories
):

    print()
    print("=" * 80)
    print("VALIDAÇÃO")
    print("=" * 80)


    print(
        f"Total coletado: "
        f"{len(repositories)}"
    )


    if (
        len(repositories)
        ==
        TOTAL_REPOSITORIES
    ):

        print(
            "OK - quantidade esperada."
        )

    else:

        print(
            "ATENÇÃO - quantidade diferente "
            "do esperado."
        )


    # --------------------------------------------------------
    # Campos ausentes
    # --------------------------------------------------------

    missing_language = sum(
        1
        for repo in repositories
        if repo[
            "primary_language"
        ] is None
    )


    print(
        f"Repos sem linguagem primária: "
        f"{missing_language}"
    )


    # --------------------------------------------------------
    # Ordenação por stars
    # --------------------------------------------------------

    ordered = all(

        repositories[i]["stars"]
        >=
        repositories[i + 1]["stars"]

        for i in range(
            len(repositories) - 1
        )
    )


    if ordered:

        print(
            "OK - resultados estão "
            "ordenados por estrelas."
        )

    else:

        print(
            "ATENÇÃO - ordem por estrelas "
            "não está consistente."
        )


# ============================================================
# AMOSTRA
# ============================================================

def print_sample(
    repositories,
    quantity=10
):

    print()
    print("=" * 80)
    print(
        f"AMOSTRA DOS PRIMEIROS "
        f"{quantity} REPOSITÓRIOS"
    )
    print("=" * 80)


    for repo in (
        repositories[:quantity]
    ):

        print()

        print(
            f"#{repo['position']} "
            f"{repo['name_with_owner']}"
        )

        print(
            f"Stars: "
            f"{repo['stars']}"
        )

        print(
            f"Idade: "
            f"{repo['age_years']} anos"
        )

        print(
            f"PRs aceitas: "
            f"{repo['accepted_pull_requests']}"
        )

        print(
            f"Releases: "
            f"{repo['releases']}"
        )

        print(
            "Dias desde última atualização: "
            f"{repo['days_since_last_update']}"
        )

        print(
            f"Linguagem: "
            f"{repo['primary_language']}"
        )

        print(
            "Issues fechadas: "
            f"{repo['closed_issues']}/"
            f"{repo['total_issues']}"
        )

        print(
            "Percentual de issues fechadas: "
            f"{repo['closed_issues_percentage']}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 80)

    print(
        "LAB01S02 - EXTRAÇÃO DOS "
        "1000 REPOSITÓRIOS MAIS POPULARES"
    )

    print("=" * 80)


    token = get_github_token()


    repositories = (
        extract_repositories(
            token
        )
    )


    validate_results(
        repositories
    )


    save_json(
        repositories
    )


    save_csv(
        repositories
    )


    print_sample(
        repositories,
        quantity=10
    )


    print()
    print("=" * 80)
    print("EXTRAÇÃO FINALIZADA")
    print("=" * 80)

    print(
        f"Arquivo:"
        f"\n{OUTPUT_FILE}"
    )

    print()


if __name__ == "__main__":
    main()