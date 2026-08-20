# Relatório LAB01S02 — Características de repositórios populares (RQ01–RQ06)

> **Laboratório de Experimentação de Software**
> Mineração dos 1.000 repositórios mais populares do GitHub
> **Primeira versão do relatório** (Sprint Lab01S02) — hipóteses informais e validação dos dados.

---

## 1. Introdução e hipóteses informais

Este relatório consolida, em um único documento, as **hipóteses informais** e a
**validação de consistência** das métricas das questões de pesquisa **RQ01 a RQ06**,
realizadas individualmente por cada integrante do grupo e reunidas aqui conforme o
enunciado da Sprint Lab01S02.

Como se trata da primeira versão, o foco é **descritivo e de validação dos dados**
(distribuição, valores ausentes, valores inválidos e outliers). A análise definitiva
e a visualização das sete RQs — incluindo a RQ07 — serão feitas na Sprint Lab01S03.

As hipóteses informais formuladas pelo grupo são:

| # | Questão de pesquisa | Hipótese informal |
|---|---|---|
| **H01** | RQ01 — Sistemas populares são maduros/antigos? | Espera-se que a maioria seja madura/antiga, pois acumular muitas estrelas exige tempo. |
| **H02** | RQ02 — Recebem muita contribuição externa? | Espera-se mediana alta de PRs aceitas, pois visibilidade atrai colaboradores. |
| **H03** | RQ03 — Lançam releases com frequência? | Espera-se quantidade significativa de releases, dado o ciclo recorrente de evolução. |
| **H04** | RQ04 — São atualizados com frequência? | Espera-se atualização recente (poucos dias desde a última atualização). |
| **H05** | RQ05 — Usam as linguagens mais populares? | Espera-se predomínio de linguagens de alto ranking de popularidade (ex.: Python, JS/TS). |
| **H06** | RQ06 — Alto percentual de issues fechadas? | Espera-se percentual mediano alto, dada a manutenção ativa dos projetos. |

---

## 2. Metodologia de coleta

- **Fonte:** API GraphQL do GitHub, consumida por **script próprio do grupo**
  (`extract_repositories.py`), sem bibliotecas de terceiros de acesso à API.
- **Amostra:** os **1.000 repositórios** com maior número de estrelas, obtidos por
  **paginação** (Issue #15).
- **Critério de popularidade:** número de estrelas (`stargazerCount`).
- **Armazenamento:** dados exportados para `data/repositories_1000.csv`.
- **Referência de "linguagens mais populares" (RQ05):** **TIOBE Index — agosto/2026**
  (https://www.tiobe.com/tiobe-index/), mantida fixa em todo o laboratório.
- **Validação:** para cada RQ foram verificados valores ausentes, valores
  estruturalmente inválidos, distribuição e outliers pelo método do **Intervalo
  Interquartil (IQR)** — este último aplicável apenas às métricas numéricas (RQ05 é
  categórica).

Cada dupla/integrante documentou sua validação em relatório próprio, referenciado ao
final deste documento.

---

## 3. Resultados por RQ

Valores obtidos sobre os **1.000 repositórios**. As medianas são a medida central de
referência (mais robusta a outliers que a média).

| RQ | Métrica | Obs. válidas | Mediana | Média |
|---|---|---:|---:|---:|
| **RQ01** | Idade do repositório (anos) | 1000 | **7.75** | 7.67 |
| **RQ02** | Pull requests aceitas | 1000 | **768** | 4236.92 |
| **RQ03** | Total de releases | 1000 | **39** | 126.61 |
| **RQ04** | Dias desde a última atualização | 1000 | **0** | -0.09 |
| **RQ05** | Linguagem primária (categórica) | 913 | **Python** (228 repos) | — |
| **RQ06** | % de issues fechadas | 957 | **87.57%** | 80.26% |

### RQ01 — Idade
Mediana de **7.75 anos** (mín. 0.02, máx. 18.35). A distribuição concentra-se nas
faixas de **5–10 anos (331 repos)** e **10–15 anos (297)**; apenas 138 têm até 2 anos.
Sem valores ausentes ou inválidos; nenhum outlier pelo IQR.

### RQ02 — Pull requests aceitas
Mediana de **768 PRs**, mas média muito maior (**4.236,92**) e máximo de **103.352**,
indicando distribuição de **cauda longa** — poucos projetos concentram a maior parte
das contribuições. **124 outliers** identificados (esperados), 0 ausentes/inválidos.

### RQ03 — Releases
Mediana de **39 releases** (média 126,61). Chama atenção que **286 repositórios
(28,6%) têm 0 releases** — muitos projetos populares distribuem sem usar o mecanismo
de releases do GitHub. **93 outliers**, 0 ausentes.

### RQ04 — Dias desde a última atualização
Mediana de **0 dias** (98,4% atualizados no dia da coleta). ⚠️ **Ressalva metodológica:**
o campo `updatedAt` muda a cada atividade mínima (inclusive receber estrela), então a
métrica **satura em 0** e discrimina pouco. Para a análise final recomenda-se usar
`pushedAt` (último push de código), que diferencia melhor a atividade real.

### RQ05 — Linguagem primária
**Python** lidera com **228 repos (22,8%)**, seguido de **TypeScript (174)** e
**JavaScript (111)**; há **43 linguagens distintas** e **87 repos sem linguagem (8,7%)**
(coleções *awesome*/documentação). Cruzando com o TIOBE, **610 de 913 (66,8%)** dos
repositórios com linguagem usam uma linguagem do **top 20**. Divergência relevante:
**TypeScript é a 2ª mais comum no GitHub, mas não está no top 20 do TIOBE**.

### RQ06 — Percentual de issues fechadas
Mediana de **87.57%** (média 80,26%); **64,26%** dos repositórios válidos fecham entre
80% e 100% das issues. **43 repos sem issues** (percentual indefinido, tratados como
ausentes) e **40 outliers** de baixo percentual — em geral coleções/tutoriais, onde as
issues funcionam como fórum. Nenhum valor inválido.

---

## 4. Discussão — hipótese vs. resultado

| Hipótese | Resultado observado | Veredito preliminar |
|---|---|---|
| **H01** | Idade mediana de 7.75 anos | **Confirmada** |
| **H02** | Mediana de 768 PRs aceitas | **Confirmada** (distribuição assimétrica) |
| **H03** | Mediana de 39 releases, mas 28,6% com 0 | **Parcialmente confirmada** |
| **H04** | Mediana de 0 dias, porém métrica satura | **Confirmada com ressalva** (ver `pushedAt`) |
| **H05** | Python = #1 TIOBE; 66,8% no top 20; TS fora | **Parcialmente confirmada** |
| **H06** | Mediana de 87.57% de issues fechadas | **Confirmada** |

De forma geral, os repositórios populares tendem a ser **maduros (H01)**, a receber
**contribuição externa relevante (H02)** e a manter **alto percentual de issues
fechadas (H06)**. As hipóteses sobre **releases (H03)**, **frequência de atualização
(H04)** e **linguagens (H05)** exigem qualificação: parte relevante dos projetos não
usa releases, a métrica de atualização atual satura, e a popularidade "no GitHub" não
coincide totalmente com a popularidade "geral" medida pelo TIOBE.

---

## 5. Resumo consolidado da qualidade dos dados

| Verificação | RQ01 | RQ02 | RQ03 | RQ04 | RQ05 | RQ06 |
|---|---:|---:|---:|---:|---:|---:|
| Observações válidas | 1000 | 1000 | 1000 | 1000 | 913 | 957 |
| Valores ausentes | 0 | 0 | 0 | 0 | 87 | 43 |
| Valores inválidos | 0 | 0 | 0 | 105* | 0 | 0 |
| Potenciais outliers (IQR) | 0 | 124 | 93 | 121 | N/A | 40 |

\* Os valores negativos da RQ04 (≈ -1 dia) são artefato de repositórios com push nos
segundos entre a captura do horário e a requisição do lote; na prática significam
"atualizado agora".

Os valores ausentes das RQ05 e RQ06 são **esperados** (repositórios sem linguagem e
sem issues, respectivamente) e não representam falha de coleta.

---

## 6. Ameaças à validade

- os dados do GitHub são dinâmicos e podem mudar após o momento da coleta;
- `updatedAt` (RQ04) reflete qualquer atividade, não apenas push de código;
- o total de releases (RQ03) não é usado por todos os projetos populares;
- o ranking TIOBE (RQ05) mede buscas na web e pode divergir do ecossistema GitHub;
- o percentual de issues fechadas (RQ06) não distingue issues legítimas de spam/duplicatas;
- a popularidade foi operacionalizada exclusivamente pelo número de estrelas.

---

## 7. Considerações finais e próximos passos

Esta primeira versão consolida as hipóteses informais e confirma a **consistência das
métricas** coletadas para RQ01–RQ06 nos 1.000 repositórios. Os dados estão prontos para
a etapa de **análise e visualização (Lab01S03)**, que incluirá também a **RQ07** (RQ02,
RQ03 e RQ04 divididas por linguagem) e as conclusões definitivas de cada questão.

---

## Relatórios de origem (validações individuais)

- RQ01 e RQ02 — [`VALIDACAO_RQ01_RQ02_S02.md`](VALIDACAO_RQ01_RQ02_S02.md) (Issue #16)
- RQ03 e RQ04 — [`VALIDACAO_RQ03_RQ04_S02.md`](VALIDACAO_RQ03_RQ04_S02.md) (Issue #17)
- RQ05 e RQ06 — [`VALIDACAO_RQ05_RQ06_S02.md`](VALIDACAO_RQ05_RQ06_S02.md) (Issue #18)
