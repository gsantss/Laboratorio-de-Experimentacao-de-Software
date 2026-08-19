import json
import statistics

from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

JSON_FILE = BASE_DIR / "data" / "repositories_1000.json"

VALIDATION_FILE = BASE_DIR / "data" / "validation_rq01_rq02_1000.json"

REPORT_DIR = BASE_DIR / "Relatorios"

REPORT_FILE = REPORT_DIR / "VALIDACAO_RQ01_RQ02_S02.md"


# ============================================================
# CARREGAR DADOS
# ============================================================

def load_repositories():
    if not JSON_FILE.exists():
        raise FileNotFoundError(f"Arquivo não encontrado:\n{JSON_FILE}")

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    return data["repositories"]


# ============================================================
# ESTATÍSTICAS DESCRITIVAS
# ============================================================

def calculate_statistics(values):
    if not values:
        return {
            "count": 0, "mean": None, "median": None, "minimum": None,
            "maximum": None, "standard_deviation": None, "q1": None,
            "q3": None, "iqr": None,
        }

    quartiles = statistics.quantiles(sorted(values), n=4, method="inclusive")
    q1, q3 = quartiles[0], quartiles[2]

    return {
        "count": len(values),
        "mean": round(statistics.mean(values), 2),
        "median": statistics.median(values),
        "minimum": min(values),
        "maximum": max(values),
        "standard_deviation": round(statistics.pstdev(values), 2),
        "q1": q1,
        "q3": q3,
        "iqr": q3 - q1,
    }


# ============================================================
# DETECÇÃO DE OUTLIERS - IQR
# ============================================================

def detect_outliers(repositories, field):
    values = [r[field] for r in repositories if r.get(field) is not None]

    if not values:
        return {"lower_limit": None, "upper_limit": None, "count": 0, "repositories": []}

    quartiles = statistics.quantiles(values, n=4, method="inclusive")
    q1, q3 = quartiles[0], quartiles[2]
    iqr = q3 - q1
    lower_limit = q1 - 1.5 * iqr
    upper_limit = q3 + 1.5 * iqr

    outliers = [
        {"position": r["position"], "repository": r["name_with_owner"], "value": r[field]}
        for r in repositories
        if r.get(field) is not None and (r[field] < lower_limit or r[field] > upper_limit)
    ]

    return {
        "lower_limit": round(lower_limit, 2),
        "upper_limit": round(upper_limit, 2),
        "count": len(outliers),
        "repositories": outliers,
    }


# ============================================================
# DISTRIBUIÇÃO RQ01 - IDADE
# ============================================================

def rq01_distribution(repositories):
    distribution = {
        "0-2 anos": 0, "2-5 anos": 0, "5-10 anos": 0,
        "10-15 anos": 0, "mais de 15 anos": 0,
    }

    for repo in repositories:
        age = repo.get("age_years")
        if age is None:
            continue
        if age <= 2:
            distribution["0-2 anos"] += 1
        elif age <= 5:
            distribution["2-5 anos"] += 1
        elif age <= 10:
            distribution["5-10 anos"] += 1
        elif age <= 15:
            distribution["10-15 anos"] += 1
        else:
            distribution["mais de 15 anos"] += 1

    return distribution


# ============================================================
# DISTRIBUIÇÃO RQ02 - PRS ACEITAS
# ============================================================

def rq02_distribution(repositories):
    distribution = {
        "0 PRs": 0, "1-50 PRs": 0, "51-200 PRs": 0,
        "201-1000 PRs": 0, "1001-5000 PRs": 0, "mais de 5000 PRs": 0,
    }

    for repo in repositories:
        prs = repo.get("accepted_pull_requests")
        if prs is None:
            continue
        if prs == 0:
            distribution["0 PRs"] += 1
        elif prs <= 50:
            distribution["1-50 PRs"] += 1
        elif prs <= 200:
            distribution["51-200 PRs"] += 1
        elif prs <= 1000:
            distribution["201-1000 PRs"] += 1
        elif prs <= 5000:
            distribution["1001-5000 PRs"] += 1
        else:
            distribution["mais de 5000 PRs"] += 1

    return distribution


# ============================================================
# VALORES AUSENTES
# ============================================================

def validate_missing_values(repositories):
    missing_created_at = [r["name_with_owner"] for r in repositories if r.get("created_at") is None]
    missing_age = [r["name_with_owner"] for r in repositories if r.get("age_years") is None]
    missing_prs = [r["name_with_owner"] for r in repositories if r.get("accepted_pull_requests") is None]

    return {
        "rq01_missing_created_at": {"count": len(missing_created_at), "repositories": missing_created_at},
        "rq01_missing_age": {"count": len(missing_age), "repositories": missing_age},
        "rq02_missing_accepted_prs": {"count": len(missing_prs), "repositories": missing_prs},
    }


# ============================================================
# VALORES INVÁLIDOS
# ============================================================

def validate_invalid_values(repositories):
    invalid_age = []
    invalid_prs = []

    for repo in repositories:
        age_days = repo.get("age_days")
        prs = repo.get("accepted_pull_requests")

        if age_days is not None and age_days < 0:
            invalid_age.append({"repository": repo["name_with_owner"], "value": age_days})

        if prs is not None and prs < 0:
            invalid_prs.append({"repository": repo["name_with_owner"], "value": prs})

    return {
        "rq01_negative_age_days": invalid_age,
        "rq02_negative_accepted_prs": invalid_prs,
    }


# ============================================================
# GERAR RELATÓRIO MARKDOWN
# ============================================================

def format_number(value):
    if value is None:
        return "N/A"
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return f"{value:.2f}"
    return str(value)


def generate_report(repositories, rq01_stats, rq02_stats, missing, invalid,
                     rq01_outliers, rq02_outliers, rq01_dist, rq02_dist):

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    total = len(repositories)
    lines = []

    lines.append("# LAB01S02 — Relatório de Validação das RQ01 e RQ02")
    lines.append("")
    lines.append("> **Laboratório de Experimentação de Software**  ")
    lines.append("> Mineração de repositórios populares do GitHub")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Resumo executivo
    lines.append("## 1. Resumo executivo")
    lines.append("")
    lines.append(
        f"Este relatório apresenta a validação das métricas associadas às "
        f"questões de pesquisa **RQ01** e **RQ02** para um conjunto de "
        f"**{total} repositórios populares do GitHub**."
    )
    lines.append("")
    lines.append(
        "A análise possui caráter **descritivo e de validação dos dados**, "
        "verificando distribuição, valores ausentes, valores inválidos e "
        "possíveis outliers."
    )
    lines.append("")
    lines.append("| Questão | Métrica | Observações válidas | Mediana |")
    lines.append("|---|---|---:|---:|")
    lines.append(
        f"| **RQ01** | Idade do repositório (anos) "
        f"| {rq01_stats['count']} | {format_number(rq01_stats['median'])} anos |"
    )
    lines.append(
        f"| **RQ02** | Total de pull requests aceitas "
        f"| {rq02_stats['count']} | {format_number(rq02_stats['median'])} PRs |"
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Questões de pesquisa
    lines.append("## 2. Questões de pesquisa")
    lines.append("")
    lines.append("### RQ01 — Sistemas populares são maduros/antigos?")
    lines.append("")
    lines.append("**Métrica utilizada:** idade do repositório, calculada a partir da data de criação (`created_at`).")
    lines.append("")
    lines.append("### RQ02 — Sistemas populares recebem muita contribuição externa?")
    lines.append("")
    lines.append("**Métrica utilizada:** total de pull requests aceitas (`states: [MERGED]`).")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Hipóteses
    lines.append("## 3. Hipóteses informais")
    lines.append("")
    lines.append(
        "**H01 — RQ01:** espera-se que a maioria dos repositórios populares "
        "seja madura/antiga, já que acumular um número alto de estrelas "
        "geralmente exige tempo — visibilidade e descoberta orgânica não "
        "acontecem da noite pro dia."
    )
    lines.append("")
    lines.append(
        "**H02 — RQ02:** espera-se um número mediano alto de PRs aceitas, "
        "já que mais visibilidade tende a atrair mais colaboradores externos "
        "em projetos open-source."
    )
    lines.append("")
    lines.append(
        "> As hipóteses acima foram formuladas na Sprint 1 (amostra de 10), "
        "antes da análise nos 1.000 repositórios completos."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Metodologia
    lines.append("## 4. Metodologia")
    lines.append("")
    lines.append(
        f"Foram considerados **{total} repositórios**, obtidos pela paginação "
        "do script único do grupo (`extract_repositories.py`, Issue #15)."
    )
    lines.append("")
    lines.append("Verificações realizadas:")
    lines.append("")
    lines.append("1. análise de valores ausentes;")
    lines.append("2. identificação de valores estruturalmente inválidos;")
    lines.append("3. análise da distribuição dos dados;")
    lines.append("4. detecção de outliers pelo método IQR (intervalo interquartil).")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Resultados - RQ01
    lines.append("## 5. Resultados — RQ01 (idade)")
    lines.append("")
    lines.append("### 5.1 Estatísticas descritivas")
    lines.append("")
    lines.append("| Métrica | Valor |")
    lines.append("|---|---:|")
    lines.append(f"| Observações válidas | {rq01_stats['count']} |")
    lines.append(f"| Média | {format_number(rq01_stats['mean'])} anos |")
    lines.append(f"| Mediana | {format_number(rq01_stats['median'])} anos |")
    lines.append(f"| Mínimo | {format_number(rq01_stats['minimum'])} anos |")
    lines.append(f"| Máximo | {format_number(rq01_stats['maximum'])} anos |")
    lines.append(f"| Desvio padrão | {format_number(rq01_stats['standard_deviation'])} |")
    lines.append(f"| Q1 | {format_number(rq01_stats['q1'])} anos |")
    lines.append(f"| Q3 | {format_number(rq01_stats['q3'])} anos |")
    lines.append(f"| IQR | {format_number(rq01_stats['iqr'])} |")
    lines.append("")
    lines.append("### 5.2 Distribuição")
    lines.append("")
    lines.append("| Faixa | Quantidade |")
    lines.append("|---|---:|")
    for faixa, qtd in rq01_dist.items():
        lines.append(f"| {faixa} | {qtd} |")
    lines.append("")
    lines.append("### 5.3 Outliers (IQR)")
    lines.append("")
    lines.append(
        f"Limites: [{format_number(rq01_outliers['lower_limit'])}, "
        f"{format_number(rq01_outliers['upper_limit'])}] anos. "
        f"Total de outliers: **{rq01_outliers['count']}**."
    )
    lines.append("")
    if rq01_outliers["repositories"]:
        lines.append("| Repositório | Idade (anos) |")
        lines.append("|---|---:|")
        for o in rq01_outliers["repositories"][:15]:
            lines.append(f"| {o['repository']} | {format_number(o['value'])} |")
        if rq01_outliers["count"] > 15:
            lines.append(f"| ... e mais {rq01_outliers['count'] - 15} | |")
    lines.append("")
    lines.append("### 5.4 Valores ausentes e inválidos")
    lines.append("")
    lines.append(f"- `created_at` ausente: **{missing['rq01_missing_created_at']['count']}**")
    lines.append(f"- `age_years` ausente: **{missing['rq01_missing_age']['count']}**")
    lines.append(f"- `age_days` negativo (inválido): **{len(invalid['rq01_negative_age_days'])}**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Resultados - RQ02
    lines.append("## 6. Resultados — RQ02 (PRs aceitas)")
    lines.append("")
    lines.append("### 6.1 Estatísticas descritivas")
    lines.append("")
    lines.append("| Métrica | Valor |")
    lines.append("|---|---:|")
    lines.append(f"| Observações válidas | {rq02_stats['count']} |")
    lines.append(f"| Média | {format_number(rq02_stats['mean'])} PRs |")
    lines.append(f"| Mediana | {format_number(rq02_stats['median'])} PRs |")
    lines.append(f"| Mínimo | {format_number(rq02_stats['minimum'])} PRs |")
    lines.append(f"| Máximo | {format_number(rq02_stats['maximum'])} PRs |")
    lines.append(f"| Desvio padrão | {format_number(rq02_stats['standard_deviation'])} |")
    lines.append(f"| Q1 | {format_number(rq02_stats['q1'])} PRs |")
    lines.append(f"| Q3 | {format_number(rq02_stats['q3'])} PRs |")
    lines.append(f"| IQR | {format_number(rq02_stats['iqr'])} |")
    lines.append("")
    lines.append("### 6.2 Distribuição")
    lines.append("")
    lines.append("| Faixa | Quantidade |")
    lines.append("|---|---:|")
    for faixa, qtd in rq02_dist.items():
        lines.append(f"| {faixa} | {qtd} |")
    lines.append("")
    lines.append("### 6.3 Outliers (IQR)")
    lines.append("")
    lines.append(
        f"Limites: [{format_number(rq02_outliers['lower_limit'])}, "
        f"{format_number(rq02_outliers['upper_limit'])}] PRs. "
        f"Total de outliers: **{rq02_outliers['count']}**."
    )
    lines.append("")
    if rq02_outliers["repositories"]:
        lines.append("| Repositório | PRs aceitas |")
        lines.append("|---|---:|")
        for o in rq02_outliers["repositories"][:15]:
            lines.append(f"| {o['repository']} | {format_number(o['value'])} |")
        if rq02_outliers["count"] > 15:
            lines.append(f"| ... e mais {rq02_outliers['count'] - 15} | |")
    lines.append("")
    lines.append("### 6.4 Valores ausentes e inválidos")
    lines.append("")
    lines.append(f"- `accepted_pull_requests` ausente: **{missing['rq02_missing_accepted_prs']['count']}**")
    lines.append(f"- `accepted_pull_requests` negativo (inválido): **{len(invalid['rq02_negative_accepted_prs'])}**")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Discussão
    lines.append("## 7. Discussão — hipótese vs. resultado")
    lines.append("")
    lines.append(
        f"**RQ01:** a idade mediana observada foi de "
        f"**{format_number(rq01_stats['median'])} anos**, o que "
        f"{'confirma' if rq01_stats['median'] and rq01_stats['median'] >= 5 else 'não confirma totalmente'} "
        f"a hipótese H01 de que sistemas populares tendem a ser maduros."
    )
    lines.append("")
    lines.append(
        f"**RQ02:** a mediana de PRs aceitas foi de "
        f"**{format_number(rq02_stats['median'])}**, "
        f"{'confirmando' if rq02_stats['median'] and rq02_stats['median'] > 0 else 'contrariando'} "
        f"a hipótese H02 de contribuição externa relevante — embora a "
        f"distribuição seja bastante assimétrica (poucos repositórios "
        f"concentram a maior parte das contribuições, ver outliers acima)."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("## 8. Conclusão")
    lines.append("")
    lines.append(
        f"Dados de RQ01 e RQ02 validados nos {total} repositórios: "
        f"{missing['rq01_missing_created_at']['count'] + missing['rq02_missing_accepted_prs']['count']} "
        f"valores ausentes no total, "
        f"{len(invalid['rq01_negative_age_days']) + len(invalid['rq02_negative_accepted_prs'])} "
        f"valores inválidos, e outliers identificados e listados acima "
        f"(esperados dado o caráter de cauda longa — poucos repositórios "
        f"extremamente populares concentram valores muito acima da mediana)."
    )
    lines.append("")

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")


# ============================================================
# SALVAR JSON DE VALIDAÇÃO
# ============================================================

def save_validation_json(rq01_stats, rq02_stats, missing, invalid, rq01_outliers, rq02_outliers, rq01_dist, rq02_dist):
    VALIDATION_FILE.parent.mkdir(parents=True, exist_ok=True)

    output = {
        "rq01_statistics": rq01_stats,
        "rq02_statistics": rq02_stats,
        "rq01_distribution": rq01_dist,
        "rq02_distribution": rq02_dist,
        "rq01_outliers": rq01_outliers,
        "rq02_outliers": rq02_outliers,
        "missing_values": missing,
        "invalid_values": invalid,
    }

    with open(VALIDATION_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 80)
    print("LAB01S02 - VALIDAÇÃO RQ01 E RQ02 (1000 REPOSITÓRIOS)")
    print("=" * 80)

    repositories = load_repositories()
    print(f"\nRepositórios carregados: {len(repositories)}")

    ages = [r["age_years"] for r in repositories if r.get("age_years") is not None]
    prs = [r["accepted_pull_requests"] for r in repositories if r.get("accepted_pull_requests") is not None]

    rq01_stats = calculate_statistics(ages)
    rq02_stats = calculate_statistics(prs)

    missing = validate_missing_values(repositories)
    invalid = validate_invalid_values(repositories)

    rq01_outliers = detect_outliers(repositories, "age_years")
    rq02_outliers = detect_outliers(repositories, "accepted_pull_requests")

    rq01_dist = rq01_distribution(repositories)
    rq02_dist = rq02_distribution(repositories)

    print("\n--- RQ01 (idade, anos) ---")
    print(json.dumps(rq01_stats, indent=2, ensure_ascii=False))
    print("\n--- RQ02 (PRs aceitas) ---")
    print(json.dumps(rq02_stats, indent=2, ensure_ascii=False))
    print(f"\nValores ausentes: {missing}")
    print(f"\nValores inválidos: {invalid}")
    print(f"\nOutliers RQ01: {rq01_outliers['count']}")
    print(f"Outliers RQ02: {rq02_outliers['count']}")

    save_validation_json(rq01_stats, rq02_stats, missing, invalid, rq01_outliers, rq02_outliers, rq01_dist, rq02_dist)
    generate_report(repositories, rq01_stats, rq02_stats, missing, invalid, rq01_outliers, rq02_outliers, rq01_dist, rq02_dist)

    print(f"\nRelatório salvo em: {REPORT_FILE}")
    print(f"JSON salvo em: {VALIDATION_FILE}")


if __name__ == "__main__":
    main()
