"""
LAB01S02 - Validação de consistência das RQ05 e RQ06 (1000 repositórios).

Issue #18. Após a paginação (Issue #15), este script valida individualmente a
consistência dos campos das minhas RQs sobre os 1.000 repositórios coletados,
lendo o CSV gerado pelo script unificado do grupo (data/repositories_1000.csv):

    RQ05 - linguagem primária (variável CATEGÓRICA): distribuição de frequência,
           valores ausentes e cruzamento com o TIOBE Index (ago/2026) como fonte
           de "linguagens mais populares" — mesma referência adotada no S01.
    RQ06 - percentual de issues fechadas (variável NUMÉRICA): estatísticas
           descritivas, distribuição, valores ausentes/inválidos e outliers (IQR).

Gera:
    - data/validation_rq05_rq06_1000.json (dados brutos da validação);
    - Relatorios/VALIDACAO_RQ05_RQ06_S02.md (relatório com hipóteses e análise).
"""

import csv
import json
import statistics
from datetime import datetime, timezone
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "data" / "repositories_1000.csv"
VALIDATION_FILE = BASE_DIR / "data" / "validation_rq05_rq06_1000.json"
REPORT_DIR = BASE_DIR / "Relatorios"
REPORT_FILE = REPORT_DIR / "VALIDACAO_RQ05_RQ06_S02.md"

# TIOBE Index - agosto/2026 (top 20). Fonte fixa do laboratório para RQ05.
# https://www.tiobe.com/tiobe-index/
TIOBE_TOP_20 = {
    "Python": 1, "C": 2, "C++": 3, "Java": 4, "C#": 5, "JavaScript": 6,
    "Visual Basic": 7, "SQL": 8, "R": 9, "Rust": 10, "Delphi/Object Pascal": 11,
    "Scratch": 12, "PHP": 13, "Go": 14, "Fortran": 15, "Ruby": 16, "Swift": 17,
    "Perl": 18, "COBOL": 19, "Assembly language": 20,
}


# ============================================================
# CARREGAR DADOS (CSV)
# ============================================================

def load_repositories():
    """Lê o CSV do script unificado e devolve a lista de repositórios.

    Converte os campos usados pelas RQ05/RQ06 para os tipos corretos e trata
    células vazias como valores ausentes (None): `primary_language` vazio =
    repositório sem linguagem; `closed_issues_percentage` vazio = repositório
    sem issues (percentual indefinido).
    """
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"Arquivo não encontrado:\n{CSV_FILE}")

    repositories = []
    with open(CSV_FILE, "r", encoding="utf-8", newline="") as file:
        for row in csv.DictReader(file):
            language = (row.get("primary_language") or "").strip()
            percentage = (row.get("closed_issues_percentage") or "").strip()
            repositories.append({
                "position": int(row["position"]),
                "name_with_owner": row["name_with_owner"],
                "primary_language": language or None,          # RQ05
                "total_issues": int(row["total_issues"]),      # RQ06
                "closed_issues": int(row["closed_issues"]),
                "closed_issues_percentage": float(percentage) if percentage else None,
            })
    return repositories


# ============================================================
# ESTATÍSTICAS DESCRITIVAS (numérico - RQ06)
# ============================================================

def calculate_statistics(values):
    """Calcula média, mediana, mínimo, máximo, desvio padrão e quartis."""
    if not values:
        return {"count": 0, "mean": None, "median": None, "minimum": None,
                "maximum": None, "standard_deviation": None, "q1": None,
                "q3": None, "iqr": None}

    quartiles = statistics.quantiles(sorted(values), n=4, method="inclusive")
    q1, q3 = quartiles[0], quartiles[2]
    return {
        "count": len(values),
        "mean": round(statistics.mean(values), 2),
        "median": round(statistics.median(values), 2),
        "minimum": min(values),
        "maximum": max(values),
        "standard_deviation": round(statistics.pstdev(values), 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(q3 - q1, 2),
    }


# ============================================================
# DETECÇÃO DE OUTLIERS - IQR (numérico - RQ06)
# ============================================================

def detect_outliers(repositories, field):
    """Identifica outliers pelo método do intervalo interquartil (IQR).

    São considerados outliers os valores abaixo de Q1 - 1,5*IQR ou acima de
    Q3 + 1,5*IQR. Só se aplica a variáveis numéricas (RQ06).
    """
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
    outliers.sort(key=lambda o: o["value"])
    return {
        "lower_limit": round(lower_limit, 2),
        "upper_limit": round(upper_limit, 2),
        "count": len(outliers),
        "repositories": outliers,
    }


# ============================================================
# RQ05 - LINGUAGEM PRIMÁRIA (categórica)
# ============================================================

def rq05_analysis(repositories):
    """Analisa a distribuição categórica das linguagens primárias.

    Retorna a contagem por linguagem (ordenada), a quantidade de repositórios
    sem linguagem, o número de linguagens distintas, as linguagens raras (que
    aparecem uma única vez) e o cruzamento com o top 20 do TIOBE.
    """
    total = len(repositories)
    with_language = [r for r in repositories if r["primary_language"] is not None]
    missing = total - len(with_language)

    counts = {}
    for repo in with_language:
        lang = repo["primary_language"]
        counts[lang] = counts.get(lang, 0) + 1
    distribution = dict(sorted(counts.items(), key=lambda kv: kv[1], reverse=True))

    rare = {lang: n for lang, n in distribution.items() if n == 1}

    in_tiobe = sum(n for lang, n in distribution.items() if lang in TIOBE_TOP_20)

    return {
        "total_repositories": total,
        "with_language": len(with_language),
        "missing_language": missing,
        "distinct_languages": len(distribution),
        "distribution": distribution,
        "rare_languages_count": len(rare),
        "in_tiobe_top20": in_tiobe,
        "out_tiobe_top20": len(with_language) - in_tiobe,
    }


# ============================================================
# RQ06 - PERCENTUAL DE ISSUES FECHADAS (numérica)
# ============================================================

def rq06_distribution(repositories):
    """Agrupa o percentual de issues fechadas em faixas de 20 pontos."""
    distribution = {
        "0-20%": 0, "20-40%": 0, "40-60%": 0, "60-80%": 0, "80-100%": 0,
    }
    for repo in repositories:
        pct = repo["closed_issues_percentage"]
        if pct is None:
            continue
        if pct <= 20:
            distribution["0-20%"] += 1
        elif pct <= 40:
            distribution["20-40%"] += 1
        elif pct <= 60:
            distribution["40-60%"] += 1
        elif pct <= 80:
            distribution["60-80%"] += 1
        else:
            distribution["80-100%"] += 1
    return distribution


# ============================================================
# VALORES AUSENTES E INVÁLIDOS
# ============================================================

def validate_quality(repositories):
    """Verifica valores ausentes e estruturalmente inválidos das RQ05/RQ06."""
    missing_language = [r["name_with_owner"] for r in repositories if r["primary_language"] is None]

    # RQ06: percentual indefinido = repositório com 0 issues.
    no_issues = [r["name_with_owner"] for r in repositories if r["total_issues"] == 0]

    # Inválidos: percentual fora de [0, 100] ou fechadas > totais.
    invalid_percentage = [
        {"repository": r["name_with_owner"], "value": r["closed_issues_percentage"]}
        for r in repositories
        if r["closed_issues_percentage"] is not None
        and not (0 <= r["closed_issues_percentage"] <= 100)
    ]
    invalid_closed = [
        {"repository": r["name_with_owner"],
         "closed": r["closed_issues"], "total": r["total_issues"]}
        for r in repositories
        if r["closed_issues"] > r["total_issues"]
    ]

    return {
        "rq05_missing_language": {"count": len(missing_language), "repositories": missing_language},
        "rq06_no_issues": {"count": len(no_issues), "repositories": no_issues},
        "rq06_invalid_percentage": invalid_percentage,
        "rq06_closed_greater_than_total": invalid_closed,
    }


# ============================================================
# GERAR RELATÓRIO MARKDOWN
# ============================================================

def fmt(value):
    """Formata número: inteiro sem casas, float com 2 casas, None como N/A."""
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return str(int(value)) if value.is_integer() else f"{value:.2f}"
    return str(value)


def pct(part, total):
    """Percentual formatado no padrão brasileiro (vírgula), ex.: 28,60%."""
    if not total:
        return "0,00%"
    return f"{part / total * 100:.2f}".replace(".", ",") + "%"


def generate_report(repositories, rq05, rq06_stats, rq06_dist, rq06_outliers, quality):
    """Monta o relatório markdown seguindo o modelo dos demais RQs do S02."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    total = len(repositories)
    valid_pct = rq06_stats["count"]
    L = []

    L.append("# LAB01S02 — Relatório de Validação das RQ05 e RQ06")
    L.append("")
    L.append("> **Laboratório de Experimentação de Software**  ")
    L.append("> Mineração de repositórios populares do GitHub")
    L.append("")
    L.append("---")
    L.append("")

    # 1. Resumo executivo
    L.append("## 1. Resumo executivo")
    L.append("")
    L.append(f"Este relatório apresenta a validação das métricas associadas às questões "
             f"de pesquisa **RQ05** e **RQ06** para um conjunto de **{total} repositórios "
             f"populares do GitHub**.")
    L.append("")
    L.append("A análise possui caráter **descritivo e de validação dos dados**, verificando "
             "distribuição, valores ausentes, valores inválidos e possíveis outliers.")
    L.append("")
    top_lang = next(iter(rq05["distribution"]))
    top_lang_n = rq05["distribution"][top_lang]
    L.append("| Questão | Métrica | Observações válidas | Resultado principal |")
    L.append("|---|---|---:|---:|")
    L.append(f"| **RQ05** | Linguagem primária (categórica) | {rq05['with_language']} | "
             f"{top_lang} lidera ({top_lang_n} repos) |")
    L.append(f"| **RQ06** | % de issues fechadas | {valid_pct} | "
             f"mediana {fmt(rq06_stats['median'])}% |")
    L.append("")
    L.append("---")
    L.append("")

    # 2. Questões de pesquisa
    L.append("## 2. Questões de pesquisa")
    L.append("")
    L.append("### RQ05 — Sistemas populares são escritos nas linguagens mais populares?")
    L.append("")
    L.append("**Métrica utilizada:** linguagem primária de cada repositório (`primary_language`).")
    L.append("")
    L.append("**Fonte de referência para \"linguagens mais populares\":** **TIOBE Index — "
             "agosto/2026** (https://www.tiobe.com/tiobe-index/), mantida fixa em todo o "
             "laboratório (mesma referência do S01).")
    L.append("")
    L.append("### RQ06 — Sistemas populares possuem alto percentual de issues fechadas?")
    L.append("")
    L.append("**Métrica utilizada:** razão entre issues fechadas e total de issues, expressa "
             "em percentual (`closed_issues_percentage`).")
    L.append("")
    L.append("> Repositórios com **0 issues** têm percentual indefinido e são tratados como "
             "valores ausentes na RQ06.")
    L.append("")
    L.append("---")
    L.append("")

    # 3. Hipóteses informais
    L.append("## 3. Hipóteses informais")
    L.append("")
    L.append("**H05 — RQ05:** espera-se que os repositórios populares sejam escritos majoritariamente "
             "em linguagens de alto ranking de popularidade, com predominância das linguagens mais "
             "usadas no ecossistema open-source (ex.: Python, JavaScript/TypeScript).")
    L.append("")
    L.append("**H06 — RQ06:** espera-se um percentual mediano **alto** de issues fechadas, já que "
             "projetos populares tendem a ter manutenção ativa e triagem contínua do backlog.")
    L.append("")
    L.append("> As hipóteses acima são informais. Nesta etapa, os resultados são apresentados de "
             "forma descritiva e ainda não constituem conclusões definitivas.")
    L.append("")
    L.append("---")
    L.append("")

    # 4. Metodologia
    L.append("## 4. Metodologia")
    L.append("")
    L.append(f"Foram considerados **{total} repositórios**, obtidos pela paginação do script único "
             "do grupo (Issue #15) e lidos a partir do arquivo `data/repositories_1000.csv`.")
    L.append("")
    L.append("Para a validação foram realizadas as seguintes verificações:")
    L.append("")
    L.append("1. análise de valores ausentes;")
    L.append("2. identificação de valores estruturalmente inválidos;")
    L.append("3. análise da distribuição dos dados;")
    L.append("4. detecção de outliers pelo método IQR (aplicável apenas à RQ06, numérica).")
    L.append("")
    L.append("> **Nota metodológica:** a RQ05 é uma variável **categórica** (nome da linguagem). "
             "Média, desvio padrão e outliers por IQR não se aplicam a categorias; por isso a RQ05 "
             "é validada por **distribuição de frequência**, contagem de valores ausentes e "
             "cruzamento com o ranking TIOBE. A RQ06 é **numérica** e recebe o tratamento "
             "estatístico completo.")
    L.append("")
    L.append("---")
    L.append("")

    # 5. RQ05
    L.append("## 5. RQ05 — Análise da linguagem primária")
    L.append("")
    L.append("### 5.1 Distribuição de frequência (top 15)")
    L.append("")
    L.append("| Linguagem | Repositórios | Percentual | TIOBE |")
    L.append("|---|---:|---:|---:|")
    for lang, n in list(rq05["distribution"].items())[:15]:
        rank = TIOBE_TOP_20.get(lang)
        mark = f"#{rank}" if rank else "—"
        L.append(f"| {lang} | {n} | {pct(n, total)} | {mark} |")
    L.append(f"| *(sem linguagem)* | {rq05['missing_language']} | "
             f"{pct(rq05['missing_language'], total)} | — |")
    L.append("")
    L.append(f"Linguagens distintas: **{rq05['distinct_languages']}** "
             f"(sendo **{rq05['rare_languages_count']}** presentes em um único repositório).")
    L.append("")
    L.append("### 5.2 Cruzamento com o TIOBE Index (ago/2026)")
    L.append("")
    L.append(f"Dos **{rq05['with_language']}** repositórios com linguagem definida, "
             f"**{rq05['in_tiobe_top20']}** ({pct(rq05['in_tiobe_top20'], rq05['with_language'])}) "
             f"usam uma linguagem presente no **top 20 do TIOBE**, enquanto "
             f"**{rq05['out_tiobe_top20']}** ({pct(rq05['out_tiobe_top20'], rq05['with_language'])}) "
             f"usam linguagens fora dele.")
    L.append("")
    L.append("### 5.3 Qualidade dos dados")
    L.append("")
    L.append(f"- Repositórios **sem linguagem primária**: **{rq05['missing_language']}** "
             f"({pct(rq05['missing_language'], total)}) — em geral coleções (*awesome*) e "
             "repositórios de documentação/Markdown, o que é esperado e não indica erro de coleta.")
    L.append("")
    L.append("### 5.4 Interpretação preliminar")
    L.append("")
    L.append(f"A linguagem mais frequente é **{top_lang}** ({top_lang_n} repositórios, "
             f"{pct(top_lang_n, total)}). A maioria dos repositórios com linguagem usa uma das "
             "linguagens de topo do TIOBE, o que oferece suporte preliminar à hipótese H05, ainda "
             "que linguagens muito populares no GitHub (como TypeScript) possam não figurar no topo "
             "do TIOBE — divergência a ser discutida na etapa de análise.")
    L.append("")
    L.append("---")
    L.append("")

    # 6. RQ06
    L.append("## 6. RQ06 — Análise do percentual de issues fechadas")
    L.append("")
    L.append("### 6.1 Estatísticas descritivas")
    L.append("")
    L.append("| Medida | Resultado |")
    L.append("|---|---:|")
    L.append(f"| Observações válidas | {rq06_stats['count']} |")
    L.append(f"| Média | {fmt(rq06_stats['mean'])}% |")
    L.append(f"| Mediana | {fmt(rq06_stats['median'])}% |")
    L.append(f"| Mínimo | {fmt(rq06_stats['minimum'])}% |")
    L.append(f"| Máximo | {fmt(rq06_stats['maximum'])}% |")
    L.append(f"| Desvio padrão | {fmt(rq06_stats['standard_deviation'])} |")
    L.append(f"| Q1 | {fmt(rq06_stats['q1'])}% |")
    L.append(f"| Q3 | {fmt(rq06_stats['q3'])}% |")
    L.append(f"| IQR | {fmt(rq06_stats['iqr'])} |")
    L.append("")
    L.append("### 6.2 Distribuição")
    L.append("")
    L.append("| Faixa de issues fechadas | Repositórios | Percentual |")
    L.append("|---|---:|---:|")
    for faixa, qtd in rq06_dist.items():
        L.append(f"| {faixa} | {qtd} | {pct(qtd, valid_pct)} |")
    L.append("")
    L.append("> Percentuais calculados sobre as observações válidas "
             f"({valid_pct} repositórios com pelo menos uma issue).")
    L.append("")
    L.append("### 6.3 Qualidade dos dados")
    L.append("")
    L.append(f"- Repositórios sem issues (percentual indefinido): "
             f"**{quality['rq06_no_issues']['count']}** ({pct(quality['rq06_no_issues']['count'], total)})")
    L.append(f"- Percentuais fora do intervalo [0, 100] (inválidos): "
             f"**{len(quality['rq06_invalid_percentage'])}**")
    L.append(f"- Issues fechadas maiores que o total (inválidos): "
             f"**{len(quality['rq06_closed_greater_than_total'])}**")
    L.append(f"- Potenciais outliers (IQR): **{rq06_outliers['count']}** "
             f"({pct(rq06_outliers['count'], valid_pct)})")
    L.append("")
    L.append(f"Limites utilizados pelo IQR: **{fmt(rq06_outliers['lower_limit'])}%** até "
             f"**{fmt(rq06_outliers['upper_limit'])}%**.")
    L.append("")
    if rq06_outliers["repositories"]:
        L.append("#### Exemplos de valores extremos (menores percentuais)")
        L.append("")
        L.append("| Posição | Repositório | % fechadas |")
        L.append("|---:|---|---:|")
        for o in rq06_outliers["repositories"][:10]:
            L.append(f"| {o['position']} | `{o['repository']}` | {fmt(o['value'])} |")
        if rq06_outliers["count"] > 10:
            L.append("")
            L.append(f"> Exibindo os 10 menores valores entre {rq06_outliers['count']} "
                     "potenciais outliers.")
        L.append("")
    L.append("### 6.4 Interpretação preliminar")
    L.append("")
    L.append(f"A mediana observada foi de **{fmt(rq06_stats['median'])}%**, enquanto a média foi "
             f"de **{fmt(rq06_stats['mean'])}%**. A mediana superior à média sugere uma distribuição "
             "assimétrica à esquerda: a maioria dos projetos fecha a grande parte de suas issues, e "
             "uma minoria com percentual baixo puxa a média para baixo. Nesta sprint, o resultado é "
             "usado principalmente para verificar a consistência da coleta; a conclusão definitiva "
             "da RQ06 será feita na etapa de análise.")
    L.append("")
    L.append("---")
    L.append("")

    # 7. Resumo da qualidade dos dados
    L.append("## 7. Resumo da qualidade dos dados")
    L.append("")
    L.append("| Verificação | RQ05 | RQ06 |")
    L.append("|---|---:|---:|")
    L.append(f"| Observações válidas | {rq05['with_language']} | {valid_pct} |")
    L.append(f"| Valores ausentes | {rq05['missing_language']} | {quality['rq06_no_issues']['count']} |")
    L.append(f"| Valores inválidos | 0 | "
             f"{len(quality['rq06_invalid_percentage']) + len(quality['rq06_closed_greater_than_total'])} |")
    L.append(f"| Potenciais outliers | N/A (categórica) | {rq06_outliers['count']} |")
    L.append("")
    L.append("---")
    L.append("")

    # 8. Ameaças à validade
    L.append("## 8. Ameaças à validade")
    L.append("")
    L.append("- os dados do GitHub são dinâmicos e podem mudar após o momento da coleta;")
    L.append("- a ausência de linguagem primária ocorre em repositórios de conteúdo/documentação e "
             "não representa falha de coleta;")
    L.append("- o percentual de issues fechadas não distingue issues legítimas de spam ou duplicatas "
             "fechadas em massa;")
    L.append("- o ranking TIOBE mede popularidade por volume de buscas na web e pode divergir da "
             "popularidade específica do ecossistema open-source do GitHub;")
    L.append("- a popularidade foi operacionalizada pela quantidade de estrelas, conforme o critério "
             "de seleção adotado pelo laboratório.")
    L.append("")
    L.append("---")
    L.append("")

    # 9. Conclusão
    L.append("## 9. Conclusão da validação")
    L.append("")
    L.append(f"A validação foi realizada sobre **{total} repositórios**, contemplando as métricas "
             "necessárias para RQ05 e RQ06.")
    L.append("")
    L.append(f"Para a **RQ05**, a linguagem mais frequente foi **{top_lang}** e "
             f"**{pct(rq05['in_tiobe_top20'], rq05['with_language'])}** dos repositórios com linguagem "
             "usam uma linguagem do top 20 do TIOBE. Para a **RQ06**, a mediana do percentual de "
             f"issues fechadas foi de **{fmt(rq06_stats['median'])}%**.")
    L.append("")
    L.append("Os resultados desta etapa fornecem evidências sobre a consistência das métricas "
             "coletadas e constituem a base para as análises e conclusões das etapas seguintes do "
             "laboratório.")
    L.append("")
    L.append("---")
    L.append("")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    L.append(f"*Relatório gerado automaticamente em {now}.*")

    REPORT_FILE.write_text("\n".join(L), encoding="utf-8")


# ============================================================
# SALVAR JSON DE VALIDAÇÃO
# ============================================================

def save_validation_json(rq05, rq06_stats, rq06_dist, rq06_outliers, quality):
    """Salva os dados brutos da validação em JSON (auditoria)."""
    VALIDATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "rq05_analysis": rq05,
        "rq06_statistics": rq06_stats,
        "rq06_distribution": rq06_dist,
        "rq06_outliers": rq06_outliers,
        "quality": quality,
    }
    with open(VALIDATION_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 80)
    print("LAB01S02 - VALIDAÇÃO RQ05 E RQ06 (1000 REPOSITÓRIOS)")
    print("=" * 80)

    repositories = load_repositories()
    print(f"\nRepositórios carregados: {len(repositories)}")

    rq05 = rq05_analysis(repositories)
    percentages = [r["closed_issues_percentage"] for r in repositories
                   if r["closed_issues_percentage"] is not None]
    rq06_stats = calculate_statistics(percentages)
    rq06_dist = rq06_distribution(repositories)
    rq06_outliers = detect_outliers(repositories, "closed_issues_percentage")
    quality = validate_quality(repositories)

    print("\n--- RQ05 (linguagem primária) ---")
    print(f"Linguagens distintas: {rq05['distinct_languages']}")
    print(f"Sem linguagem: {rq05['missing_language']}")
    print(f"No TIOBE top 20: {rq05['in_tiobe_top20']}/{rq05['with_language']}")
    print("Top 5:", list(rq05["distribution"].items())[:5])

    print("\n--- RQ06 (% issues fechadas) ---")
    print(json.dumps(rq06_stats, indent=2, ensure_ascii=False))
    print(f"Sem issues (ausentes): {quality['rq06_no_issues']['count']}")
    print(f"Outliers: {rq06_outliers['count']}")

    save_validation_json(rq05, rq06_stats, rq06_dist, rq06_outliers, quality)
    generate_report(repositories, rq05, rq06_stats, rq06_dist, rq06_outliers, quality)

    print(f"\nRelatório salvo em: {REPORT_FILE}")
    print(f"JSON salvo em: {VALIDATION_FILE}")


if __name__ == "__main__":
    main()
