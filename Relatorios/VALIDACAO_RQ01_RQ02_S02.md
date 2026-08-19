# LAB01S02 — Relatório de Validação das RQ01 e RQ02

> **Laboratório de Experimentação de Software**  
> Mineração de repositórios populares do GitHub

---

## 1. Resumo executivo

Este relatório apresenta a validação das métricas associadas às questões de pesquisa **RQ01** e **RQ02** para um conjunto de **1000 repositórios populares do GitHub**.

A análise possui caráter **descritivo e de validação dos dados**, verificando distribuição, valores ausentes, valores inválidos e possíveis outliers.

| Questão | Métrica | Observações válidas | Mediana |
|---|---|---:|---:|
| **RQ01** | Idade do repositório (anos) | 1000 | 7.75 anos |
| **RQ02** | Total de pull requests aceitas | 1000 | 768 PRs |

---

## 2. Questões de pesquisa

### RQ01 — Sistemas populares são maduros/antigos?

**Métrica utilizada:** idade do repositório, calculada a partir da data de criação (`created_at`).

### RQ02 — Sistemas populares recebem muita contribuição externa?

**Métrica utilizada:** total de pull requests aceitas (`states: [MERGED]`).

---

## 3. Hipóteses informais

**H01 — RQ01:** espera-se que a maioria dos repositórios populares seja madura/antiga, já que acumular um número alto de estrelas geralmente exige tempo — visibilidade e descoberta orgânica não acontecem da noite pro dia.

**H02 — RQ02:** espera-se um número mediano alto de PRs aceitas, já que mais visibilidade tende a atrair mais colaboradores externos em projetos open-source.

> As hipóteses acima foram formuladas na Sprint 1 (amostra de 10), antes da análise nos 1.000 repositórios completos.

---

## 4. Metodologia

Foram considerados **1000 repositórios**, obtidos pela paginação do script único do grupo (`extract_repositories.py`, Issue #15).

Verificações realizadas:

1. análise de valores ausentes;
2. identificação de valores estruturalmente inválidos;
3. análise da distribuição dos dados;
4. detecção de outliers pelo método IQR (intervalo interquartil).

---

## 5. Resultados — RQ01 (idade)

### 5.1 Estatísticas descritivas

| Métrica | Valor |
|---|---:|
| Observações válidas | 1000 |
| Média | 7.67 anos |
| Mediana | 7.75 anos |
| Mínimo | 0.02 anos |
| Máximo | 18.35 anos |
| Desvio padrão | 4.53 |
| Q1 | 3.52 anos |
| Q3 | 11.35 anos |
| IQR | 7.83 |

### 5.2 Distribuição

| Faixa | Quantidade |
|---|---:|
| 0-2 anos | 138 |
| 2-5 anos | 185 |
| 5-10 anos | 331 |
| 10-15 anos | 297 |
| mais de 15 anos | 49 |

### 5.3 Outliers (IQR)

Limites: [-8.23, 23.10] anos. Total de outliers: **0**.


### 5.4 Valores ausentes e inválidos

- `created_at` ausente: **0**
- `age_years` ausente: **0**
- `age_days` negativo (inválido): **0**

---

## 6. Resultados — RQ02 (PRs aceitas)

### 6.1 Estatísticas descritivas

| Métrica | Valor |
|---|---:|
| Observações válidas | 1000 |
| Média | 4236.92 PRs |
| Mediana | 768 PRs |
| Mínimo | 0 PRs |
| Máximo | 103352 PRs |
| Desvio padrão | 10662.39 |
| Q1 | 175 PRs |
| Q3 | 3415.75 PRs |
| IQR | 3240.75 |

### 6.2 Distribuição

| Faixa | Quantidade |
|---|---:|
| 0 PRs | 20 |
| 1-50 PRs | 110 |
| 51-200 PRs | 144 |
| 201-1000 PRs | 276 |
| 1001-5000 PRs | 264 |
| mais de 5000 PRs | 186 |

### 6.3 Outliers (IQR)

Limites: [-4686.12, 8276.88] PRs. Total de outliers: **124**.

| Repositório | PRs aceitas |
|---|---:|
| freeCodeCamp/freeCodeCamp | 29115 |
| openclaw/openclaw | 26337 |
| react/react | 13034 |
| NousResearch/hermes-agent | 11245 |
| n8n-io/n8n | 20174 |
| tensorflow/tensorflow | 48928 |
| microsoft/vscode | 52145 |
| flutter/flutter | 49656 |
| twbs/bootstrap | 9481 |
| huggingface/transformers | 20218 |
| langgenius/dify | 13431 |
| langchain-ai/langchain | 17268 |
| vercel/next.js | 28228 |
| ggml-org/llama.cpp | 9754 |
| kubernetes/kubernetes | 65650 |
| ... e mais 109 | |

### 6.4 Valores ausentes e inválidos

- `accepted_pull_requests` ausente: **0**
- `accepted_pull_requests` negativo (inválido): **0**

---

## 7. Discussão — hipótese vs. resultado

**RQ01:** a idade mediana observada foi de **7.75 anos**, o que confirma a hipótese H01 de que sistemas populares tendem a ser maduros.

**RQ02:** a mediana de PRs aceitas foi de **768**, confirmando a hipótese H02 de contribuição externa relevante — embora a distribuição seja bastante assimétrica (poucos repositórios concentram a maior parte das contribuições, ver outliers acima).

---

## 8. Conclusão

Dados de RQ01 e RQ02 validados nos 1000 repositórios: 0 valores ausentes no total, 0 valores inválidos, e outliers identificados e listados acima (esperados dado o caráter de cauda longa — poucos repositórios extremamente populares concentram valores muito acima da mediana).
