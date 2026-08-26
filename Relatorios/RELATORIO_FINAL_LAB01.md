# Relatório Final — LAB01: Características de Repositórios Populares

> **Disciplina:** Laboratório de Experimentação de Software — Engenharia de Software (6º período)

> **Professor:** Danilo Maia

> **Integrantes:** Gabriel Santos · Pedro Porto · Arthur Santana

> **Repositório:** https://github.com/gsantss/Laboratorio-de-Experimentacao-de-Software

> **GitHub Projects (board):** `<preencher com a URL do Project v2 do grupo>`

---

## Resumo

Este trabalho investiga as principais características de sistemas populares
open-source hospedados no GitHub. A partir de uma coleta automatizada dos
**1.000 repositórios com maior número de estrelas**, realizada por meio de um
script próprio que consome a **API GraphQL do GitHub**, o estudo responde a sete
questões de pesquisa (RQ01–RQ07) relativas à **maturidade** dos projetos, ao
volume de **contribuição externa** (pull requests aceitas), à frequência de
**releases** e de **atualização**, às **linguagens de programação** empregadas e
ao **percentual de issues fechadas**, além de cruzar contribuição, releases e
atualização **por linguagem**.

Os resultados mostram que os repositórios populares tendem a ser **maduros**
(idade mediana de **7,75 anos**), a receber **contribuição externa relevante**
(mediana de **768 PRs aceitas**) e a manter um **alto percentual de issues
fechadas** (mediana de **87,57%**). Já as hipóteses sobre releases, frequência de
atualização e linguagens exigem qualificação, discutida ao longo do relatório. O
documento também descreve a **configuração do processo** de trabalho do grupo no
GitHub Projects (colunas do Kanban e política de WIP).

---

## (i) Introdução e hipóteses informais

A popularidade de um projeto open-source — aqui operacionalizada pelo número de
**estrelas** — é frequentemente associada a maturidade, atividade e boa
manutenção. Antes da análise dos dados, o grupo formulou as seguintes **hipóteses
informais** para cada questão de pesquisa:

| # | Questão de pesquisa | Hipótese informal |
|---|---|---|
| **H01** | RQ01 — São maduros/antigos? | A maioria será madura/antiga, pois acumular estrelas exige tempo. |
| **H02** | RQ02 — Recebem muita contribuição externa? | Mediana alta de PRs aceitas, pois visibilidade atrai colaboradores. |
| **H03** | RQ03 — Lançam releases com frequência? | Quantidade significativa de releases, dado o ciclo recorrente de entrega. |
| **H04** | RQ04 — São atualizados com frequência? | Atualização recente (poucos dias desde a última atualização). |
| **H05** | RQ05 — Usam as linguagens mais populares? | Predomínio de linguagens de alto ranking de popularidade (Python, JS/TS). |
| **H06** | RQ06 — Alto percentual de issues fechadas? | Percentual mediano alto, dada a manutenção ativa. |
| **H07** | RQ07 — Linguagens populares são mais ativas? | Linguagens populares recebem mais PRs, releases e atualizações. |

---

## (ii) Metodologia de coleta

- **Fonte de dados:** API GraphQL do GitHub, consumida por **script próprio do
  grupo** (`scripts/extract_repositories.py`), sem bibliotecas de terceiros de
  acesso à API, conforme exigência do laboratório.
- **Seleção da amostra:** consulta `stars:>0 sort:stars-desc`, coletando os
  **1.000 repositórios** com mais estrelas via **paginação** (lotes de 10).
- **Critério de popularidade:** número de estrelas (`stargazerCount`).
- **Métricas coletadas por repositório:** data de criação (idade), total de PRs
  aceitas (`MERGED`), total de releases, data da última atualização, linguagem
  primária, total de issues e issues fechadas.
- **Armazenamento:** exportação para `data/repositories_1000.json` e
  `data/repositories_1000.csv`.
- **Referência de "linguagens mais populares" (RQ05/RQ07):** **TIOBE Index —
  agosto/2026** (https://www.tiobe.com/tiobe-index/), mantida fixa em todo o
  laboratório.
- **Medida central:** adota-se a **mediana** como medida de referência, por ser
  robusta a outliers (as distribuições são de cauda longa). Para variáveis
  categóricas (linguagem), usa-se **contagem por categoria**.
- **Validação de consistência:** para cada bloco de RQs foram verificados valores
  ausentes, valores inválidos, distribuição e outliers pelo método do **Intervalo
  Interquartil (IQR)**, documentados nos relatórios de validação da Sprint S02.

---

## (iii) Resultados por RQ

Valores calculados sobre os **1.000 repositórios**.

### Panorama geral

| RQ | Métrica | Obs. válidas | Mediana | Média |
|---|---|---:|---:|---:|
| RQ01 | Idade (anos) | 1000 | **7,75** | 7,67 |
| RQ02 | PRs aceitas | 1000 | **768** | 4.236,92 |
| RQ03 | Releases | 1000 | **39** | 126,61 |
| RQ04 | Dias desde a última atualização | 1000 | **0** | -0,09 |
| RQ05 | Linguagem primária | 913 | **Python** (228 repos) | — |
| RQ06 | % de issues fechadas | 957 | **87,57%** | 80,26% |

### RQ01 — Maturidade (idade)
Idade mediana de **7,75 anos** (mín. 0,02; máx. 18,35; Q1 3,52; Q3 11,35).
Distribuição por faixa:

| Faixa | Repositórios |
|---|---:|
| 0–2 anos | 138 |
| 2–5 anos | 185 |
| 5–10 anos | 331 |
| 10–15 anos | 297 |
| mais de 15 anos | 49 |

A concentração em **5–15 anos (628 repositórios)** indica projetos maduros. Sem
valores ausentes/inválidos e sem outliers pelo IQR.

### RQ02 — Contribuição externa (PRs aceitas)
Mediana de **768 PRs**, mas média muito maior (**4.236,92**) e máximo de
**103.352**, revelando distribuição de **cauda longa** — poucos projetos
concentram a maior parte das contribuições.

| Faixa de PRs | Repositórios |
|---|---:|
| 0 | 20 |
| 1–50 | 110 |
| 51–200 | 144 |
| 201–1.000 | 276 |
| 1.001–5.000 | 264 |
| mais de 5.000 | 186 |

### RQ03 — Releases
Mediana de **39 releases** (média 126,61). Destaque: **286 repositórios (28,6%)
não têm nenhuma release** — muitos projetos populares distribuem sem usar o
mecanismo de releases do GitHub.

| Faixa de releases | Repositórios |
|---|---:|
| 0 | 286 |
| 1–10 | 76 |
| 11–50 | 177 |
| 51–100 | 118 |
| 101–500 | 274 |
| mais de 500 | 69 |

### RQ04 — Frequência de atualização
Mediana de **0 dias** (98,4% atualizados no dia da coleta). ⚠️ **Ressalva
metodológica:** o campo `updatedAt` muda a cada atividade mínima (inclusive
receber uma estrela), então a métrica **satura em 0** e discrimina pouco. Para a
análise de atividade real, recomenda-se o campo `pushedAt` (último push de
código).

### RQ05 — Linguagem primária
**Python** lidera com **228 repositórios (22,8%)**, seguido de **TypeScript (174;
17,4%)** e **JavaScript (111; 11,1%)**. Há **43 linguagens distintas** e **87
repositórios (8,7%) sem linguagem** (coleções *awesome*/documentação).

| Linguagem | Repositórios | TIOBE |
|---|---:|---:|
| Python | 228 | #1 |
| TypeScript | 174 | — |
| JavaScript | 111 | #6 |
| Go | 76 | #14 |
| Rust | 57 | #10 |
| C++ | 41 | #3 |
| Java | 41 | #4 |
| C | 21 | #2 |
| *(sem linguagem)* | 87 | — |

Cruzando com o TIOBE, **610 de 913 (66,8%)** dos repositórios com linguagem usam
uma linguagem do **top 20**. Divergência relevante: **TypeScript é a 2ª mais comum
no GitHub, mas não figura no top 20 do TIOBE**.

### RQ06 — Percentual de issues fechadas
Mediana de **87,57%** (média 80,26%). **43 repositórios sem issues** (percentual
indefinido, excluídos).

| Faixa de issues fechadas | Repositórios |
|---|---:|
| 0–20% | 12 |
| 20–40% | 57 |
| 40–60% | 94 |
| 60–80% | 179 |
| 80–100% | 615 |

**64,3%** dos repositórios válidos fecham entre 80% e 100% das issues.

### RQ07 — Contribuição, releases e atualização por linguagem
Medianas por linguagem (para as mais frequentes):

| Linguagem | Repos | Mediana PRs | Mediana Releases | Mediana dias s/ atualizar |
|---|---:|---:|---:|---:|
| Python | 228 | 560 | 20 | 0 |
| TypeScript | 174 | 2.002 | 134 | 0 |
| JavaScript | 111 | 617 | 39 | 0 |
| Go | 76 | 1.703 | 141 | 0 |
| Rust | 57 | 2.495 | 90 | 0 |
| C++ | 41 | 1.156 | 46 | 0 |
| Java | 41 | 941 | 55 | 0 |
| *Sem linguagem* | 87 | 129 | 0 | 0 |

Observa-se que **TypeScript, Rust e Go** apresentam as maiores medianas de PRs e
releases, **acima de Python** — a linguagem mais frequente da amostra. A coluna de
dias sem atualizar satura em 0 (mesma limitação do `updatedAt` da RQ04).

---

## (iv) Discussão — hipótese vs. resultado

| Hipótese | Resultado observado | Veredito |
|---|---|---|
| **H01** | Idade mediana de 7,75 anos; 62,8% entre 5–15 anos | **Confirmada** |
| **H02** | Mediana de 768 PRs aceitas (cauda longa) | **Confirmada** |
| **H03** | Mediana de 39 releases, mas 28,6% com 0 | **Parcialmente confirmada** |
| **H04** | Mediana de 0 dias, porém métrica satura (`updatedAt`) | **Confirmada com ressalva** |
| **H05** | Python = #1 TIOBE; 66,8% no top 20; TypeScript fora | **Parcialmente confirmada** |
| **H06** | Mediana de 87,57% de issues fechadas | **Confirmada** |
| **H07** | TS/Rust/Go lideram PRs/releases, acima de Python | **Parcialmente confirmada** |

**Síntese.** Os dados sustentam fortemente que repositórios populares são
**maduros (H01)**, recebem **contribuição externa relevante (H02)** e mantêm
**alto percentual de issues fechadas (H06)**. As demais hipóteses (H03, H04, H05 e
H07) precisam de qualificação. A análise detalhada de cada uma segue abaixo.

### Análise por hipótese

#### H01 — RQ01 (maturidade) · **Confirmada**
A idade mediana é de **7,75 anos**, com **628 repositórios (62,8%) entre 5 e 15
anos** e apenas 138 com até 2 anos. **Por que foi confirmada:** a hipótese previa
que acumular estrelas exige tempo, e os dados mostram exatamente isso — projetos
muito jovens quase não alcançam o topo. A confirmação é robusta: 0 valores
ausentes/inválidos e 0 outliers pelo IQR.

#### H02 — RQ02 (contribuição externa) · **Confirmada**
A mediana é de **768 PRs aceitas**, com **72,6% dos repositórios acima de 200 PRs**.
**Por que foi confirmada:** o volume mediano é alto, coerente com a ideia de que
visibilidade atrai colaboradores. **Ressalva interpretativa:** a distribuição é de
cauda longa (média 4.236,92; máximo 103.352), então a **mediana** — e não a média —
é a medida que representa o comportamento típico; relatar a média isoladamente
superestimaria a contribuição.

#### H03 — RQ03 (releases) · **Parcialmente confirmada**
A mediana é de **39 releases**, mas **286 repositórios (28,6%) têm 0 releases**.
**Por que não foi totalmente confirmada:** uma parcela grande de projetos populares
simplesmente **não usa o mecanismo de Releases do GitHub** — distribui por gerenciadores
de pacotes (npm, PyPI), por tags Git, ou é coleção/documentação sem artefato versionado.
A mediana geral mascara essa divisão.
**Como concluir melhor / investigar:**
- separar a análise **por tipo de projeto** (biblioteca/aplicação vs. coleção/docs) —
  os repositórios "sem linguagem" concentram boa parte dos zeros;
- complementar a contagem de releases com as **tags Git** (`refs/tags`), que capturam
  versionamento fora do mecanismo de Releases;
- **normalizar pela idade** (releases por ano) para distinguir projeto ativo de projeto
  antigo com releases acumuladas.

#### H04 — RQ04 (atualização) · **Confirmada com ressalva (inconclusiva)**
A mediana é de **0 dias** (98,4% "atualizados no dia da coleta"). **Por que a ressalva:**
o campo `updatedAt` muda a cada evento mínimo no repositório (receber estrela, watch,
edição de metadados) e **não apenas com push de código**. A métrica **satura em 0** e não
discrimina projetos ativos de inativos — logo, não permite concluir com segurança.
**Como concluir melhor / investigar:**
- trocar `updatedAt` por **`pushedAt`** (data do último push de código) e recomputar a RQ;
- de forma ainda mais precisa, usar a data do último commit do branch padrão
  (`defaultBranchRef.target.committedDate`);
- analisar a **distribuição** dos dias desde o último push (não só a mediana), separando
  projetos ativos de arquivados/legados.

#### H05 — RQ05 (linguagens) · **Parcialmente confirmada**
**Python é #1** tanto na amostra (228 repos) quanto no TIOBE, e **66,8% dos repositórios
com linguagem** usam uma linguagem do top 20 do TIOBE. **Por que não foi totalmente
confirmada:** **TypeScript**, a 2ª linguagem mais comum no GitHub (174 repos), **não
figura no top 20 do TIOBE**, e linguagens web (Shell, HTML) aparecem muito no GitHub e
pouco no índice. O conceito de "popularidade" **diverge conforme a fonte**: o TIOBE mede
volume de buscas na web, incluindo domínios corporativo/legado.
**Como concluir melhor / investigar:**
- comparar com uma fonte de popularidade **específica de open-source/GitHub** (Octoverse,
  GitHut) além do TIOBE, e reportar as duas lado a lado;
- **ponderar por estrelas** (linguagem dos repositórios mais estrelados), não só a
  contagem simples de repositórios;
- tratar os **8,7% "sem linguagem"** explicitamente como categoria à parte.

#### H06 — RQ06 (issues fechadas) · **Confirmada**
A mediana é de **87,57%**, com **64,3% dos repositórios válidos fechando entre 80% e 100%**
das issues. **Por que foi confirmada:** o percentual mediano alto é coerente com projetos
de manutenção ativa e triagem contínua. **Ressalva menor:** a métrica não distingue issue
legítima de spam/duplicata fechada em massa, e 43 repositórios sem issues foram excluídos —
mas nada disso altera a conclusão.

#### H07 — RQ07 (linguagens populares mais ativas) · **Parcialmente confirmada**
A intuição era que a linguagem **mais frequente** concentraria mais atividade. Os dados
mostram o contrário: **TypeScript (2.002 PRs / 134 releases), Rust (2.495 / 90) e Go
(1.703 / 141)** superam **Python (560 / 20)**, a linguagem mais comum. **Por que não foi
totalmente confirmada:** "mais popular" **não implica** "mais contribuição" — a atividade
associa-se mais ao **tipo de ecossistema** (web, sistemas) do que à frequência da
linguagem. Além disso, a dimensão de **atualização** não pôde ser avaliada (satura, ver H04).
**Como concluir melhor / investigar:**
- refazer com **`pushedAt`** para incorporar de fato a 3ª dimensão (frequência de atualização);
- **controlar o tamanho dos grupos** — linguagens com poucos repositórios (ex.: Ruby,
  n=13, mediana de 6.263 PRs) produzem medianas instáveis; aplicar um teste estatístico
  (ex.: **Kruskal-Wallis**) para verificar se as diferenças por linguagem são significativas;
- **normalizar** PRs e releases pela idade do projeto antes de comparar linguagens.

---

## (v) Configuração do processo (GitHub Projects)

O grupo utilizou um **GitHub Projects (v2)** vinculado ao repositório para
gerenciar o trabalho ao longo do laboratório, com **cartões = Issues** reais
(rastreáveis pela API), cada uma **atribuída a um responsável** (Assignee).

### Colunas do board (campo Status)
Fluxo Kanban com as colunas mínimas exigidas:

`Backlog → To Do → Doing → Review → Done`

### Política de WIP (Work in Progress)
- **Limite da coluna `Doing` = 3.**
- **Justificativa:** o grupo é um **trio**; o limite de 3 permite, no máximo, uma
  tarefa em andamento por integrante ao mesmo tempo. Isso evita acúmulo de
  trabalho não finalizado, incentiva a conclusão antes do início de novas tarefas
  e mantém o fluxo alinhado ao desenvolvimento individual semanal previsto no
  enunciado.


### Rastreabilidade
Cada commit referencia o número da Issue correspondente (ex.: `#18 valida ...`),
vinculando automaticamente commit ↔ Issue. Ao final de cada sprint, um script
GraphQL (`scripts/snapshot_board.py`) exporta os itens do Project e seu status
para CSV (`data/snapshot_board_*.csv`), constituindo a série histórica dos
Labs 04 e 05.

---

## Anexo — Print do board e fluxo completo do Lab01

> `![Board do Lab01](../data/board_print_lab01.png)`

---

*Relatório final elaborado a partir dos dados em `data/repositories_1000.csv`
(1.000 repositórios) e dos relatórios de validação da Sprint Lab01S02.*
