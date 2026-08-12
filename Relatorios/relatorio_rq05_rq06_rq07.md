# Relatório rápido — RQ05, RQ06 e RQ07 (integrante C)

**Lab01S01 — Características de repositórios populares**
Amostra: **100** repositórios mais populares do GitHub (ordenados por estrelas).
Coleta: `2026-08-12` via script próprio `extract_rq05_rq06_rq07.py` (API GraphQL).
Dados: `data/repositories_rq05_rq06_rq07.json`.

---

## RQ05 — Sistemas populares são escritos nas linguagens mais populares?

**Métrica:** linguagem primária (`primary_language`).
**Fonte de referência para "linguagens populares":** **TIOBE Index — agosto/2026**
(https://www.tiobe.com/tiobe-index/), mantida fixa em todo o laboratório. Top 5 do
TIOBE no período: 1º Python, 2º C, 3º C++, 4º Java, 5º C#.

**Resultado — distribuição da amostra cruzada com o ranking TIOBE:**

| Linguagem (amostra) | Repos | Posição no TIOBE top 20 |
|---|---|---|
| Python | 24 | #1 |
| TypeScript | 17 | — (fora do top 20) |
| *Sem linguagem* | 13 | — (não é linguagem) |
| JavaScript | 10 | #6 |
| Shell | 5 | — (fora do top 20) |
| C++ | 5 | #3 |
| Rust | 5 | #10 |
| Go | 4 | #14 |
| C | 3 | #2 |
| Markdown / HTML | 3 + 3 | — (não são linguagens de programação) |
| Java / C# / Swift | 1 cada | #4 / #5 / #17 |

**Números-chave:** dos **87** repositórios com linguagem definida, **54 (62,1%)**
usam uma linguagem que está no top 20 do TIOBE; **33** usam linguagens fora dele.

**Leitura:** **a hipótese se confirma parcialmente.** A linguagem mais frequente da
amostra é **Python**, que é exatamente o **#1 do TIOBE**, e a maioria (62%) dos repos
com linguagem usa alguma das mais populares do índice (Python, C, C++, JavaScript,
Rust, Go). Porém há uma **divergência importante**: **TypeScript é a 2ª linguagem mais
comum entre os repositórios populares (17 repos), mas nem aparece no top 20 do
TIOBE**. Isso ocorre porque o TIOBE mede popularidade por volume de buscas na web
(abrangendo domínios corporativo/legado — daí Visual Basic, SQL, R, Delphi e COBOL no
top 20), enquanto o ecossistema open-source do GitHub é fortemente puxado por
linguagens web/frontend (TypeScript, Shell, HTML) que o TIOBE subestima. Ou seja:
**popularidade "geral" (TIOBE) e popularidade "no GitHub" não são a mesma coisa.**
Destaque adicional: **13 dos 100** repositórios não têm linguagem primária (coleções
*awesome* / docs em Markdown), reforçando que parte da popularidade vem de conteúdo,
não de código.

---

## RQ06 — Sistemas populares possuem alto percentual de issues fechadas?

**Métrica:** razão `issues fechadas / total de issues` (`closed_issues_percentage`).

**Resultado:**
- Repositórios considerados: **89** (11 excluídos por terem 0 issues → razão indefinida).
- **Mediana: 92,72%**
- Média: 83,49%
- Mínimo: 13,33% | Máximo: 100,00%

**Leitura:** com mediana de **~93%**, **a hipótese se confirma** — sistemas populares
fecham a grande maioria de suas issues. A média (83%) é bem menor que a mediana, o
que indica uma cauda de poucos projetos com taxa baixa puxando a média para baixo;
por isso a **mediana é a medida mais representativa** aqui.

---

## RQ07 — Linguagens populares recebem mais contribuição, releases e atualizações?

**Métricas (mediana por linguagem):** PRs aceitas (RQ02), releases (RQ03) e dias
desde o último **push** de código (RQ04, via `pushedAt`). Baseline geral dos 100
repos: **mediana de 0 dias** desde o último push (**50 dos 100** tiveram push no dia
da coleta).

| Linguagem | Repos | Mediana PRs | Mediana Releases | Mediana dias s/ push |
|---|---|---|---|---|
| Python | 24 | 1.881,5 | 54 | 1 |
| TypeScript | 17 | 6.981,0 | 116 | 0 |
| *Sem linguagem* | 13 | 317,0 | 0 | 114 |
| JavaScript | 10 | 1.373,5 | 69 | 0 |
| Shell | 5 | 222,0 | 7 | 5 |
| C++ | 5 | 26.490,0 | 471 | 0 |
| Rust | 5 | 4.197,0 | 39 | 0 |
| Go | 4 | 3.685,5 | 120 | 0 |

**Leitura:**
- **Contribuição (PRs) e releases:** entre as linguagens mais frequentes,
  **TypeScript** lidera com folga (mediana de ~6.981 PRs e 116 releases), bem acima
  de Python e JavaScript. Ou seja, as linguagens populares realmente concentram mais
  contribuição externa e mais releases — **coerente com a hipótese**. Vale notar que
  linguagens de sistema com poucos repos, como **C++ (5 repos)**, têm medianas
  altíssimas (~26,5k PRs, 471 releases) por serem projetos gigantes (ex.: navegadores,
  compiladores) — mas o `n` pequeno pede cautela na comparação.
- **Atualização (RQ04 via `pushedAt`):** trocando `updatedAt` por `pushedAt`, a
  métrica passou a diferenciar de fato as linguagens. As linguagens de código ativo
  (**TypeScript, JavaScript, C++, Rust, Go**) têm mediana de **0 dias** — push no
  mesmo dia. Já os repositórios **"Sem linguagem"** (listas *awesome* / docs) têm
  mediana de **114 dias**, confirmando que recebem estrelas mas quase nenhum push de
  código. Ou seja: as linguagens populares são também as mais frequentemente
  atualizadas — **coerente com a hipótese**.

**Conclusão da RQ07:** nas três dimensões (PRs, releases e frequência de push), as
linguagens de programação mais populares tendem a apresentar maior atividade que os
repositórios sem linguagem definida — **hipótese confirmada**.

> Nota técnica: a coleta registrou um `min` de -1 dia em pouquíssimos casos — artefato
> de repositórios que receberam push nos segundos entre o início do script e a
> requisição do lote; na prática significa "atualizado agora" e não afeta as medianas.

---

## Resumo

| RQ | Resultado principal | Hipótese |
|---|---|---|
| RQ05 | 62% dos repos usam linguagem do top 20 TIOBE (Python = #1); mas TypeScript (2º na amostra) fica fora do TIOBE | Parcialmente confirmada |
| RQ06 | Mediana de **92,72%** de issues fechadas | Confirmada |
| RQ07 | TS lidera PRs/releases; linguagens de código com push no mesmo dia (mediana 0) vs. 114 dias dos repos sem linguagem | Confirmada |
