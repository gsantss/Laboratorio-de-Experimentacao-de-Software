"""Gera os gráficos (PNG) usados no Relatório Final, a partir de data/repositories_1000.csv."""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "repositories_1000.csv"
OUT_DIR = BASE_DIR / "Relatorios" / "graficos"
OUT_DIR.mkdir(parents=True, exist_ok=True)

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.size": 11,
})

df = pd.read_csv(DATA_FILE)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT_DIR / name, dpi=140)
    plt.close(fig)
    print(f"salvo: {OUT_DIR / name}")


# RQ01 - idade
fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(df["age_years"].dropna(), bins=40, color="#4C72B0", edgecolor="white")
ax.set_title("RQ01 — Distribuição de idade dos repositórios")
ax.set_xlabel("Idade (anos)")
ax.set_ylabel("Quantidade de repositórios")
ax.axvline(df["age_years"].median(), color="#C44E52", linestyle="--", label=f"Mediana = {df['age_years'].median():.2f} anos")
ax.legend()
save(fig, "rq01_idade.png")

# RQ02 - PRs aceitas (log)
fig, ax = plt.subplots(figsize=(7, 4))
log_prs = np.log10(df["accepted_pull_requests"] + 1)
ax.hist(log_prs, bins=40, color="#55A868", edgecolor="white")
ax.set_title("RQ02 — Distribuição de PRs aceitas (escala logarítmica)")
ax.set_xlabel("PRs aceitas")
ax.set_ylabel("Quantidade de repositórios")
ax.set_xticks([0, 1, 2, 3, 4, 5])
ax.set_xticklabels(["0", "10", "100", "1k", "10k", "100k"])
ax.axvline(np.log10(df["accepted_pull_requests"].median() + 1), color="#C44E52", linestyle="--",
           label=f"Mediana = {df['accepted_pull_requests'].median():.0f} PRs")
ax.legend()
save(fig, "rq02_prs_aceitas.png")

# RQ03 - releases (faixas)
bins = [-1, 0, 10, 50, 100, 500, float("inf")]
labels = ["0", "1-10", "11-50", "51-100", "101-500", "mais de 500"]
faixas = pd.cut(df["releases"], bins=bins, labels=labels)
counts = faixas.value_counts().reindex(labels)
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(counts.index, counts.values, color="#8172B2")
ax.set_title("RQ03 — Distribuição de releases por faixa")
ax.set_xlabel("Faixa de releases")
ax.set_ylabel("Quantidade de repositórios")
for i, v in enumerate(counts.values):
    ax.text(i, v + 5, str(v), ha="center")
save(fig, "rq03_releases.png")

# RQ05 - linguagens (ranking, barras horizontais)
top_langs = df["primary_language"].value_counts().head(10).sort_values()
fig, ax = plt.subplots(figsize=(7, 5))
ax.barh(top_langs.index, top_langs.values, color="#CCB974")
ax.set_title("RQ05 — Top 10 linguagens primárias")
ax.set_xlabel("Quantidade de repositórios")
for i, v in enumerate(top_langs.values):
    ax.text(v + 2, i, str(v), va="center")
save(fig, "rq05_linguagens.png")

# RQ06 - % issues fechadas (faixas)
bins6 = [-1, 20, 40, 60, 80, 100]
labels6 = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]
faixas6 = pd.cut(df["closed_issues_percentage"], bins=bins6, labels=labels6)
counts6 = faixas6.value_counts().reindex(labels6)
fig, ax = plt.subplots(figsize=(7, 4))
ax.bar(counts6.index, counts6.values, color="#64B5CD")
ax.set_title("RQ06 — % de issues fechadas por faixa")
ax.set_xlabel("Faixa de % de issues fechadas")
ax.set_ylabel("Quantidade de repositórios")
for i, v in enumerate(counts6.values):
    ax.text(i, v + 5, str(v), ha="center")
save(fig, "rq06_issues_fechadas.png")

# RQ07 - PRs e releases por linguagem (top 7)
top7 = df["primary_language"].value_counts().head(7).index
grouped = df[df["primary_language"].isin(top7)].groupby("primary_language").agg(
    mediana_prs=("accepted_pull_requests", "median"),
    mediana_releases=("releases", "median"),
).reindex(top7)

fig, ax1 = plt.subplots(figsize=(8, 4.5))
x = np.arange(len(grouped))
width = 0.35
ax1.bar(x - width / 2, grouped["mediana_prs"], width, label="Mediana PRs aceitas", color="#4C72B0")
ax1.bar(x + width / 2, grouped["mediana_releases"], width, label="Mediana releases", color="#DD8452")
ax1.set_xticks(x)
ax1.set_xticklabels(grouped.index, rotation=20)
ax1.set_title("RQ07 — Mediana de PRs aceitas e releases por linguagem (top 7)")
ax1.set_ylabel("Valor mediano")
ax1.legend()
save(fig, "rq07_por_linguagem.png")

print("\nTodos os gráficos gerados em:", OUT_DIR)
