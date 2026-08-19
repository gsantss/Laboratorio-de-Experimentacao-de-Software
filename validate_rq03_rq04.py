import json
import statistics

from pathlib import Path
from datetime import datetime, timezone


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

JSON_FILE = (
    BASE_DIR
    / "data"
    / "repositories_1000.json"
)

VALIDATION_FILE = (
    BASE_DIR
    / "data"
    / "validation_rq03_rq04_1000.json"
)

REPORT_DIR = (
    BASE_DIR
    / "Relatorios"
)

REPORT_FILE = (
    REPORT_DIR
    / "VALIDACAO_RQ03_RQ04_S02.md"
)


# ============================================================
# CARREGAR DADOS
# ============================================================

def load_repositories():

    if not JSON_FILE.exists():

        raise FileNotFoundError(
            f"Arquivo não encontrado:\n"
            f"{JSON_FILE}"
        )

    with open(
        JSON_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    repositories = data[
        "repositories"
    ]

    return repositories


# ============================================================
# ESTATÍSTICAS DESCRITIVAS
# ============================================================

def calculate_statistics(values):

    if not values:

        return {
            "count": 0,
            "mean": None,
            "median": None,
            "minimum": None,
            "maximum": None,
            "standard_deviation": None,
            "q1": None,
            "q3": None,
            "iqr": None
        }

    ordered = sorted(values)

    quartiles = statistics.quantiles(
        ordered,
        n=4,
        method="inclusive"
    )

    q1 = quartiles[0]
    q3 = quartiles[2]

    iqr = q3 - q1

    return {

        "count":
            len(values),

        "mean":
            round(
                statistics.mean(values),
                2
            ),

        "median":
            statistics.median(values),

        "minimum":
            min(values),

        "maximum":
            max(values),

        "standard_deviation":
            round(
                statistics.pstdev(values),
                2
            ),

        "q1":
            q1,

        "q3":
            q3,

        "iqr":
            iqr
    }


# ============================================================
# DETECÇÃO DE OUTLIERS - IQR
# ============================================================

def detect_outliers(
    repositories,
    field
):

    values = [
        repo[field]
        for repo in repositories
        if repo.get(field) is not None
    ]

    if not values:

        return {
            "lower_limit": None,
            "upper_limit": None,
            "count": 0,
            "repositories": []
        }

    quartiles = statistics.quantiles(
        values,
        n=4,
        method="inclusive"
    )

    q1 = quartiles[0]
    q3 = quartiles[2]

    iqr = q3 - q1

    lower_limit = (
        q1 - 1.5 * iqr
    )

    upper_limit = (
        q3 + 1.5 * iqr
    )

    outliers = []

    for repo in repositories:

        value = repo.get(field)

        if value is None:
            continue

        if (
            value < lower_limit
            or
            value > upper_limit
        ):

            outliers.append({
                "position":
                    repo["position"],

                "repository":
                    repo["name_with_owner"],

                "value":
                    value
            })

    return {

        "lower_limit":
            round(
                lower_limit,
                2
            ),

        "upper_limit":
            round(
                upper_limit,
                2
            ),

        "count":
            len(outliers),

        "repositories":
            outliers
    }


# ============================================================
# DISTRIBUIÇÃO RQ03
# ============================================================

def rq03_distribution(
    repositories
):

    distribution = {

        "0 releases":
            0,

        "1-10 releases":
            0,

        "11-50 releases":
            0,

        "51-100 releases":
            0,

        "101-500 releases":
            0,

        "mais de 500 releases":
            0
    }

    for repo in repositories:

        releases = repo.get(
            "releases"
        )

        if releases is None:
            continue

        if releases == 0:

            distribution[
                "0 releases"
            ] += 1

        elif releases <= 10:

            distribution[
                "1-10 releases"
            ] += 1

        elif releases <= 50:

            distribution[
                "11-50 releases"
            ] += 1

        elif releases <= 100:

            distribution[
                "51-100 releases"
            ] += 1

        elif releases <= 500:

            distribution[
                "101-500 releases"
            ] += 1

        else:

            distribution[
                "mais de 500 releases"
            ] += 1

    return distribution


# ============================================================
# DISTRIBUIÇÃO RQ04
# ============================================================

def rq04_distribution(
    repositories
):

    distribution = {

        "0 dias":
            0,

        "1-7 dias":
            0,

        "8-30 dias":
            0,

        "31-90 dias":
            0,

        "91-365 dias":
            0,

        "mais de 365 dias":
            0
    }

    for repo in repositories:

        days = repo.get(
            "days_since_last_update"
        )

        if days is None:
            continue

        if days <= 0:

            distribution[
                "0 dias"
            ] += 1

        elif days <= 7:

            distribution[
                "1-7 dias"
            ] += 1

        elif days <= 30:

            distribution[
                "8-30 dias"
            ] += 1

        elif days <= 90:

            distribution[
                "31-90 dias"
            ] += 1

        elif days <= 365:

            distribution[
                "91-365 dias"
            ] += 1

        else:

            distribution[
                "mais de 365 dias"
            ] += 1

    return distribution


# ============================================================
# VALORES AUSENTES
# ============================================================

def validate_missing_values(
    repositories
):

    missing_releases = [
        repo["name_with_owner"]
        for repo in repositories
        if repo.get("releases") is None
    ]

    missing_updated_at = [
        repo["name_with_owner"]
        for repo in repositories
        if repo.get("updated_at") is None
    ]

    missing_days = [
        repo["name_with_owner"]
        for repo in repositories
        if repo.get(
            "days_since_last_update"
        ) is None
    ]

    return {

        "rq03_missing_releases": {
            "count":
                len(missing_releases),

            "repositories":
                missing_releases
        },

        "rq04_missing_updated_at": {
            "count":
                len(missing_updated_at),

            "repositories":
                missing_updated_at
        },

        "rq04_missing_days": {
            "count":
                len(missing_days),

            "repositories":
                missing_days
        }
    }


# ============================================================
# VALORES INVÁLIDOS
# ============================================================

def validate_invalid_values(
    repositories
):

    invalid_releases = []

    invalid_days = []

    for repo in repositories:

        releases = repo.get(
            "releases"
        )

        days = repo.get(
            "days_since_last_update"
        )

        if (
            releases is not None
            and releases < 0
        ):

            invalid_releases.append({
                "repository":
                    repo["name_with_owner"],

                "value":
                    releases
            })

        if (
            days is not None
            and days < 0
        ):

            invalid_days.append({
                "repository":
                    repo["name_with_owner"],

                "value":
                    days
            })

    return {

        "rq03_negative_releases":
            invalid_releases,

        "rq04_negative_days":
            invalid_days
    }


# ============================================================
# GERAR RELATÓRIO MARKDOWN
# ============================================================

def generate_report(
    repositories,
    rq03_stats,
    rq04_stats,
    missing,
    invalid,
    rq03_outliers,
    rq04_outliers,
    rq03_dist,
    rq04_dist
):

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    def format_number(value):

        if value is None:
            return "N/A"

        if isinstance(value, float):

            if value.is_integer():
                return str(int(value))

            return f"{value:.2f}"

        return str(value)


    def percentage(
        value,
        total
    ):

        if total == 0:
            return "0,00%"

        result = (
            value
            /
            total
            *
            100
        )

        return (
            f"{result:.2f}%"
            .replace(".", ",")
        )


    total_repositories = len(
        repositories
    )

    rq03_missing = (
        missing[
            "rq03_missing_releases"
        ][
            "count"
        ]
    )

    rq04_missing_dates = (
        missing[
            "rq04_missing_updated_at"
        ][
            "count"
        ]
    )

    rq04_missing_days = (
        missing[
            "rq04_missing_days"
        ][
            "count"
        ]
    )

    rq03_invalid = len(
        invalid[
            "rq03_negative_releases"
        ]
    )

    rq04_invalid = len(
        invalid[
            "rq04_negative_days"
        ]
    )

    lines = []

    # ========================================================
    # CABEÇALHO
    # ========================================================

    lines.append(
        "# LAB01S02 — Relatório de Validação das RQ03 e RQ04"
    )

    lines.append("")

    lines.append(
        "> **Laboratório de Experimentação de Software**  "
    )

    lines.append(
        "> Mineração de repositórios populares do GitHub"
    )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # RESUMO EXECUTIVO
    # ========================================================

    lines.append(
        "## 1. Resumo executivo"
    )

    lines.append("")

    lines.append(
        f"Este relatório apresenta a validação das métricas "
        f"associadas às questões de pesquisa **RQ03** e "
        f"**RQ04** para um conjunto de **{total_repositories} "
        f"repositórios populares do GitHub**."
    )

    lines.append("")

    lines.append(
        "A análise possui caráter **descritivo e de validação "
        "dos dados**, verificando distribuição, valores "
        "ausentes, valores inválidos e possíveis outliers."
    )

    lines.append("")

    lines.append(
        "| Questão | Métrica | Observações válidas | Mediana |"
    )

    lines.append(
        "|---|---|---:|---:|"
    )

    lines.append(
        f"| **RQ03** | Total de releases "
        f"| {rq03_stats['count']} "
        f"| {format_number(rq03_stats['median'])} releases |"
    )

    lines.append(
        f"| **RQ04** | Dias desde a última atualização "
        f"| {rq04_stats['count']} "
        f"| {format_number(rq04_stats['median'])} dias |"
    )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # QUESTÕES DE PESQUISA
    # ========================================================

    lines.append(
        "## 2. Questões de pesquisa"
    )

    lines.append("")

    lines.append(
        "### RQ03 — Sistemas populares lançam releases com frequência?"
    )

    lines.append("")

    lines.append(
        "**Métrica utilizada:** quantidade total de releases "
        "registradas no repositório."
    )

    lines.append("")

    lines.append(
        "### RQ04 — Sistemas populares são atualizados com frequência?"
    )

    lines.append("")

    lines.append(
        "**Métrica utilizada:** quantidade de dias transcorridos "
        "desde a última atualização registrada no repositório."
    )

    lines.append("")

    lines.append(
        "> Na RQ04, valores menores representam uma atualização "
        "> mais recente."
    )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # HIPÓTESES
    # ========================================================

    lines.append(
        "## 3. Hipóteses informais"
    )

    lines.append("")

    lines.append(
        "**H03 — RQ03:** espera-se que projetos populares "
        "apresentem quantidade significativa de releases, "
        "considerando que projetos amplamente utilizados "
        "tendem a possuir ciclos recorrentes de evolução "
        "e entrega."
    )

    lines.append("")

    lines.append(
        "**H04 — RQ04:** espera-se que projetos populares "
        "tenham sido atualizados recentemente, apresentando "
        "um número relativamente baixo de dias desde sua "
        "última atualização."
    )

    lines.append("")

    lines.append(
        "> As hipóteses acima são informais. Nesta etapa, "
        "> os resultados são apresentados de forma descritiva "
        "> e ainda não constituem conclusões definitivas."
    )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # METODOLOGIA
    # ========================================================

    lines.append(
        "## 4. Metodologia"
    )

    lines.append("")

    lines.append(
        f"Foram considerados **{total_repositories} repositórios** "
        "obtidos por meio da API GraphQL do GitHub."
    )

    lines.append("")

    lines.append(
        "Para a validação das métricas RQ03 e RQ04 foram "
        "realizadas quatro verificações principais:"
    )

    lines.append("")

    lines.append(
        "1. análise de valores ausentes;"
    )

    lines.append(
        "2. identificação de valores estruturalmente inválidos;"
    )

    lines.append(
        "3. análise da distribuição dos dados;"
    )

    lines.append(
        "4. identificação de possíveis outliers."
    )

    lines.append("")

    lines.append(
        "Os outliers foram identificados utilizando o método "
        "do **Intervalo Interquartil (IQR)**. Foram considerados "
        "potenciais outliers os valores abaixo de "
        "`Q1 - 1,5 × IQR` ou acima de `Q3 + 1,5 × IQR`."
    )

    lines.append("")

    lines.append(
        "Além disso, foram calculadas medidas descritivas como "
        "**média, mediana, mínimo, máximo, quartis e desvio padrão**."
    )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # RQ03
    # ========================================================

    lines.append(
        "## 5. RQ03 — Análise do total de releases"
    )

    lines.append("")

    lines.append(
        "### 5.1 Estatísticas descritivas"
    )

    lines.append("")

    lines.append(
        "| Medida | Resultado |"
    )

    lines.append(
        "|---|---:|"
    )

    lines.append(
        f"| Observações válidas "
        f"| {format_number(rq03_stats['count'])} |"
    )

    lines.append(
        f"| Média "
        f"| {format_number(rq03_stats['mean'])} releases |"
    )

    lines.append(
        f"| Mediana "
        f"| {format_number(rq03_stats['median'])} releases |"
    )

    lines.append(
        f"| Mínimo "
        f"| {format_number(rq03_stats['minimum'])} releases |"
    )

    lines.append(
        f"| Máximo "
        f"| {format_number(rq03_stats['maximum'])} releases |"
    )

    lines.append(
        f"| Desvio padrão "
        f"| {format_number(rq03_stats['standard_deviation'])} |"
    )

    lines.append(
        f"| Q1 "
        f"| {format_number(rq03_stats['q1'])} |"
    )

    lines.append(
        f"| Q3 "
        f"| {format_number(rq03_stats['q3'])} |"
    )

    lines.append(
        f"| IQR "
        f"| {format_number(rq03_stats['iqr'])} |"
    )

    lines.append("")


    # ========================================================
    # RQ03 DISTRIBUIÇÃO
    # ========================================================

    lines.append(
        "### 5.2 Distribuição"
    )

    lines.append("")

    lines.append(
        "| Faixa de releases | Repositórios | Percentual |"
    )

    lines.append(
        "|---|---:|---:|"
    )

    for category, count in (
        rq03_dist.items()
    ):

        lines.append(
            f"| {category} "
            f"| {count} "
            f"| {percentage(count, total_repositories)} |"
        )

    lines.append("")


    # ========================================================
    # RQ03 QUALIDADE
    # ========================================================

    lines.append(
        "### 5.3 Qualidade dos dados"
    )

    lines.append("")

    lines.append(
        f"- Valores ausentes: **{rq03_missing}** "
        f"({percentage(rq03_missing, total_repositories)})"
    )

    lines.append(
        f"- Valores negativos inválidos: **{rq03_invalid}**"
    )

    lines.append(
        f"- Potenciais outliers: **{rq03_outliers['count']}** "
        f"({percentage(rq03_outliers['count'], total_repositories)})"
    )

    lines.append("")

    lines.append(
        f"Limites utilizados pelo IQR: "
        f"**{format_number(rq03_outliers['lower_limit'])}** "
        f"até **{format_number(rq03_outliers['upper_limit'])}** releases."
    )

    lines.append("")


    if rq03_outliers[
        "repositories"
    ]:

        lines.append(
            "#### Exemplos de valores extremos"
        )

        lines.append("")

        lines.append(
            "| Posição | Repositório | Releases |"
        )

        lines.append(
            "|---:|---|---:|"
        )

        sorted_rq03_outliers = sorted(
            rq03_outliers[
                "repositories"
            ],
            key=lambda item: item[
                "value"
            ],
            reverse=True
        )

        for item in (
            sorted_rq03_outliers[:10]
        ):

            lines.append(
                f"| {item['position']} "
                f"| `{item['repository']}` "
                f"| {item['value']} |"
            )

        if rq03_outliers["count"] > 10:

            lines.append("")

            lines.append(
                f"> Exibindo os 10 maiores valores entre "
                f"{rq03_outliers['count']} potenciais outliers."
            )

        lines.append("")


    lines.append(
        "### 5.4 Interpretação preliminar"
    )

    lines.append("")

    lines.append(
        f"A mediana observada foi de "
        f"**{format_number(rq03_stats['median'])} releases**, "
        f"enquanto a média foi de "
        f"**{format_number(rq03_stats['mean'])} releases**."
    )

    lines.append("")

    lines.append(
        "A comparação entre média, mediana, dispersão e "
        "outliers auxilia na identificação de uma possível "
        "assimetria da distribuição. Repositórios com números "
        "muito elevados de releases podem aumentar a média e "
        "torná-la menos representativa do comportamento típico."
    )

    lines.append("")

    lines.append(
        "Nesta sprint, esses resultados são utilizados "
        "principalmente para verificar a consistência da coleta. "
        "A conclusão definitiva da RQ03 será realizada na etapa "
        "de análise do laboratório."
    )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # RQ04
    # ========================================================

    lines.append(
        "## 6. RQ04 — Análise do tempo desde a última atualização"
    )

    lines.append("")

    lines.append(
        "### 6.1 Estatísticas descritivas"
    )

    lines.append("")

    lines.append(
        "| Medida | Resultado |"
    )

    lines.append(
        "|---|---:|"
    )

    lines.append(
        f"| Observações válidas "
        f"| {format_number(rq04_stats['count'])} |"
    )

    lines.append(
        f"| Média "
        f"| {format_number(rq04_stats['mean'])} dias |"
    )

    lines.append(
        f"| Mediana "
        f"| {format_number(rq04_stats['median'])} dias |"
    )

    lines.append(
        f"| Mínimo "
        f"| {format_number(rq04_stats['minimum'])} dias |"
    )

    lines.append(
        f"| Máximo "
        f"| {format_number(rq04_stats['maximum'])} dias |"
    )

    lines.append(
        f"| Desvio padrão "
        f"| {format_number(rq04_stats['standard_deviation'])} dias |"
    )

    lines.append(
        f"| Q1 "
        f"| {format_number(rq04_stats['q1'])} dias |"
    )

    lines.append(
        f"| Q3 "
        f"| {format_number(rq04_stats['q3'])} dias |"
    )

    lines.append(
        f"| IQR "
        f"| {format_number(rq04_stats['iqr'])} dias |"
    )

    lines.append("")


    # ========================================================
    # RQ04 DISTRIBUIÇÃO
    # ========================================================

    lines.append(
        "### 6.2 Distribuição"
    )

    lines.append("")

    lines.append(
        "| Tempo desde a atualização | Repositórios | Percentual |"
    )

    lines.append(
        "|---|---:|---:|"
    )

    for category, count in (
        rq04_dist.items()
    ):

        lines.append(
            f"| {category} "
            f"| {count} "
            f"| {percentage(count, total_repositories)} |"
        )

    lines.append("")


    # ========================================================
    # RQ04 QUALIDADE
    # ========================================================

    lines.append(
        "### 6.3 Qualidade dos dados"
    )

    lines.append("")

    lines.append(
        f"- Datas `updatedAt` ausentes: "
        f"**{rq04_missing_dates}** "
        f"({percentage(rq04_missing_dates, total_repositories)})"
    )

    lines.append(
        f"- Valores calculados em dias ausentes: "
        f"**{rq04_missing_days}** "
        f"({percentage(rq04_missing_days, total_repositories)})"
    )

    lines.append(
        f"- Valores negativos: **{rq04_invalid}**"
    )

    lines.append(
        f"- Potenciais outliers: **{rq04_outliers['count']}** "
        f"({percentage(rq04_outliers['count'], total_repositories)})"
    )

    lines.append("")

    lines.append(
        f"Limites utilizados pelo IQR: "
        f"**{format_number(rq04_outliers['lower_limit'])}** "
        f"até **{format_number(rq04_outliers['upper_limit'])} dias**."
    )

    lines.append("")


    if rq04_outliers[
        "repositories"
    ]:

        lines.append(
            "#### Repositórios há mais tempo sem atualização"
        )

        lines.append("")

        lines.append(
            "| Posição | Repositório | Dias |"
        )

        lines.append(
            "|---:|---|---:|"
        )

        sorted_rq04_outliers = sorted(
            rq04_outliers[
                "repositories"
            ],
            key=lambda item: item[
                "value"
            ],
            reverse=True
        )

        for item in (
            sorted_rq04_outliers[:10]
        ):

            lines.append(
                f"| {item['position']} "
                f"| `{item['repository']}` "
                f"| {item['value']} |"
            )

        if rq04_outliers["count"] > 10:

            lines.append("")

            lines.append(
                f"> Exibindo os 10 maiores valores entre "
                f"{rq04_outliers['count']} potenciais outliers."
            )

        lines.append("")


    lines.append(
        "### 6.4 Interpretação preliminar"
    )

    lines.append("")

    lines.append(
        f"A mediana de tempo desde a última atualização foi "
        f"de **{format_number(rq04_stats['median'])} dias**, "
        f"enquanto a média foi de "
        f"**{format_number(rq04_stats['mean'])} dias**."
    )

    lines.append("")

    lines.append(
        "Como valores menores representam atualizações mais "
        "recentes, a distribuição permite observar a concentração "
        "de projetos que permanecem ativos e também identificar "
        "repositórios que apresentam períodos muito maiores sem "
        "atualização."
    )

    lines.append("")

    lines.append(
        "Assim como na RQ03, esta etapa não estabelece ainda "
        "um limiar para classificar formalmente um projeto como "
        "\"frequentemente atualizado\". Os resultados são "
        "descritivos e servirão de base para a análise posterior."
    )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # RESUMO DA QUALIDADE
    # ========================================================

    lines.append(
        "## 7. Resumo da qualidade dos dados"
    )

    lines.append("")

    lines.append(
        "| Verificação | RQ03 | RQ04 |"
    )

    lines.append(
        "|---|---:|---:|"
    )

    lines.append(
        f"| Valores válidos "
        f"| {rq03_stats['count']} "
        f"| {rq04_stats['count']} |"
    )

    lines.append(
        f"| Valores ausentes "
        f"| {rq03_missing} "
        f"| {rq04_missing_days} |"
    )

    lines.append(
        f"| Valores inválidos "
        f"| {rq03_invalid} "
        f"| {rq04_invalid} |"
    )

    lines.append(
        f"| Potenciais outliers "
        f"| {rq03_outliers['count']} "
        f"| {rq04_outliers['count']} |"
    )

    lines.append("")

    if (
        rq03_missing == 0
        and
        rq04_missing_dates == 0
        and
        rq04_missing_days == 0
        and
        rq03_invalid == 0
        and
        rq04_invalid == 0
    ):

        lines.append(
            "> **Resultado da validação:** não foram identificados "
            "> valores ausentes ou estruturalmente inválidos nas "
            "> métricas analisadas."
        )

    else:

        lines.append(
            "> **Resultado da validação:** foram encontradas "
            "> ocorrências que devem ser verificadas antes da "
            "> análise final."
        )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # AMEAÇAS À VALIDADE
    # ========================================================

    lines.append(
        "## 8. Ameaças à validade"
    )

    lines.append("")

    lines.append(
        "Alguns fatores devem ser considerados durante a "
        "interpretação dos resultados:"
    )

    lines.append("")

    lines.append(
        "- os dados do GitHub são dinâmicos e podem mudar "
        "após o momento da coleta;"
    )

    lines.append(
        "- a quantidade total de releases não considera "
        "diretamente o intervalo temporal entre elas;"
    )

    lines.append(
        "- a data de atualização representa a informação "
        "fornecida pelo GitHub para o repositório e deve ser "
        "interpretada conforme a definição utilizada na coleta;"
    )

    lines.append(
        "- valores extremos podem representar projetos "
        "legítimos e não necessariamente erros;"
    )

    lines.append(
        "- a popularidade foi operacionalizada pela quantidade "
        "de estrelas, conforme o critério de seleção adotado "
        "pelo laboratório."
    )

    lines.append("")

    lines.append("---")

    lines.append("")


    # ========================================================
    # CONCLUSÃO
    # ========================================================

    lines.append(
        "## 9. Conclusão da validação"
    )

    lines.append("")

    lines.append(
        f"A validação foi realizada sobre "
        f"**{total_repositories} repositórios**, contemplando "
        "as métricas necessárias para RQ03 e RQ04."
    )

    lines.append("")

    lines.append(
        "Foram analisadas estatísticas descritivas, distribuição, "
        "valores ausentes, valores inválidos e possíveis outliers."
    )

    lines.append("")

    lines.append(
        f"Para a **RQ03**, a mediana observada foi de "
        f"**{format_number(rq03_stats['median'])} releases**. "
        f"Para a **RQ04**, a mediana foi de "
        f"**{format_number(rq04_stats['median'])} dias desde "
        f"a última atualização**."
    )

    lines.append("")

    lines.append(
        "Os resultados desta etapa fornecem evidências sobre a "
        "consistência das métricas coletadas e constituem a base "
        "para as análises e conclusões das etapas seguintes do "
        "laboratório."
    )

    lines.append("")

    lines.append("---")

    lines.append("")

    lines.append(
        f"*Relatório gerado automaticamente em "
        f"{datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}.*"
    )


    with open(
        REPORT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        file.write(
            "\n".join(lines)
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 100)
    print("VALIDAÇÃO RQ03 E RQ04 - LAB01S02")
    print("=" * 100)

    repositories = (
        load_repositories()
    )

    print()
    print(
        f"Repositórios carregados: "
        f"{len(repositories)}"
    )


    # ========================================================
    # RQ03
    # ========================================================

    rq03_values = [
        repo["releases"]
        for repo in repositories
        if repo.get("releases") is not None
    ]


    # ========================================================
    # RQ04
    # ========================================================

    rq04_values = [
        repo["days_since_last_update"]
        for repo in repositories
        if repo.get(
            "days_since_last_update"
        ) is not None
    ]


    rq03_stats = (
        calculate_statistics(
            rq03_values
        )
    )

    rq04_stats = (
        calculate_statistics(
            rq04_values
        )
    )


    missing = (
        validate_missing_values(
            repositories
        )
    )

    invalid = (
        validate_invalid_values(
            repositories
        )
    )


    rq03_outliers = (
        detect_outliers(
            repositories,
            "releases"
        )
    )

    rq04_outliers = (
        detect_outliers(
            repositories,
            "days_since_last_update"
        )
    )


    rq03_dist = (
        rq03_distribution(
            repositories
        )
    )

    rq04_dist = (
        rq04_distribution(
            repositories
        )
    )


    # ========================================================
    # RESULTADO JSON
    # ========================================================

    VALIDATION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    validation = {

        "metadata": {

            "validated_at":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "repository_count":
                len(repositories),

            "research_questions": [
                "RQ03",
                "RQ04"
            ]
        },

        "rq03": {

            "metric":
                "total_releases",

            "statistics":
                rq03_stats,

            "distribution":
                rq03_dist,

            "missing_values":
                missing[
                    "rq03_missing_releases"
                ],

            "invalid_values":
                invalid[
                    "rq03_negative_releases"
                ],

            "outliers":
                rq03_outliers
        },

        "rq04": {

            "metric":
                "days_since_last_update",

            "statistics":
                rq04_stats,

            "distribution":
                rq04_dist,

            "missing_updated_at":
                missing[
                    "rq04_missing_updated_at"
                ],

            "missing_days":
                missing[
                    "rq04_missing_days"
                ],

            "invalid_values":
                invalid[
                    "rq04_negative_days"
                ],

            "outliers":
                rq04_outliers
        }
    }


    with open(
        VALIDATION_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            validation,
            file,
            indent=4,
            ensure_ascii=False
        )


    # ========================================================
    # RELATÓRIO MARKDOWN
    # ========================================================

    generate_report(
        repositories=
            repositories,

        rq03_stats=
            rq03_stats,

        rq04_stats=
            rq04_stats,

        missing=
            missing,

        invalid=
            invalid,

        rq03_outliers=
            rq03_outliers,

        rq04_outliers=
            rq04_outliers,

        rq03_dist=
            rq03_dist,

        rq04_dist=
            rq04_dist
    )


    # ========================================================
    # FINALIZAÇÃO
    # ========================================================

    print()
    print("=" * 100)
    print("VALIDAÇÃO FINALIZADA")
    print("=" * 100)

    print()

    print(
        f"JSON de validação:\n"
        f"{VALIDATION_FILE}"
    )

    print()

    print(
        f"Relatório Markdown:\n"
        f"{REPORT_FILE}"
    )

    print()


if __name__ == "__main__":
    main()
