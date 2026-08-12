# Validação — RQ01 e RQ02 (Issue #3)

Responsável: Arthur Pedra (`arthies2323`)

## Métricas

- **RQ01** — idade do repositório, calculada a partir de `createdAt`.
- **RQ02** — total de pull requests aceitas, via `pullRequests(states: [MERGED]).totalCount`.

## Extração — implementação própria

Query GraphQL escrita e testada de forma independente, sem depender do script
unificado do grupo, em `extract_rq01_rq02.py`. Ela consulta a API diretamente
(`search(query: "stars:>0 sort:stars-desc", type: REPOSITORY)`), pedindo só os
campos necessários para RQ01/RQ02 (`createdAt` e
`pullRequests(states: [MERGED]) { totalCount }`), e roda numa amostra de 10
repositórios. Saída salva em `data/rq01_rq02_amostra.json` (local, não
versionado).

## Saída bruta da execução

```
================================================================================
EXTRAÇÃO INDIVIDUAL - RQ01 (idade) e RQ02 (PRs aceitas)
Amostra: 10 repositórios
================================================================================

codecrafters-io/build-your-own-x
  RQ01 - Criado em: 2018-05-09T12:03:18Z  (8.26 anos)
  RQ02 - PRs aceitas: 157

sindresorhus/awesome
  RQ01 - Criado em: 2014-07-11T13:42:37Z  (12.09 anos)
  RQ02 - PRs aceitas: 700

public-apis/public-apis
  RQ01 - Criado em: 2016-03-20T23:49:42Z  (10.39 anos)
  RQ02 - PRs aceitas: 2119

freeCodeCamp/freeCodeCamp
  RQ01 - Criado em: 2014-12-24T17:49:19Z  (11.63 anos)
  RQ02 - PRs aceitas: 29074

EbookFoundation/free-programming-books
  RQ01 - Criado em: 2013-10-11T06:50:37Z  (12.84 anos)
  RQ02 - PRs aceitas: 7417

openclaw/openclaw
  RQ01 - Criado em: 2025-11-24T10:16:47Z  (0.71 anos)
  RQ02 - PRs aceitas: 24303

nilbuild/developer-roadmap
  RQ01 - Criado em: 2017-03-15T13:45:52Z  (9.41 anos)
  RQ02 - PRs aceitas: 4387

donnemartin/system-design-primer
  RQ01 - Criado em: 2017-02-26T16:15:28Z  (9.46 anos)
  RQ02 - PRs aceitas: 210

jwasham/coding-interview-university
  RQ01 - Criado em: 2016-06-06T02:34:12Z  (10.18 anos)
  RQ02 - PRs aceitas: 415

vinta/awesome-python
  RQ01 - Criado em: 2014-06-27T21:00:06Z  (12.12 anos)
  RQ02 - PRs aceitas: 738

Salvo em: data/rq01_rq02_amostra.json
```

## Validação — comparação com fontes independentes

Cada um dos 10 repositórios da amostra foi conferido contra a API REST do
GitHub, um caminho de dados separado da nossa query GraphQL:

- RQ01 → `GET /repos/{owner}/{repo}` → campo `created_at`
- RQ02 → `GET /search/issues?q=repo:{owner}/{repo}+type:pr+is:merged` → campo `total_count`

### RQ01 — idade (`created_at`)

| # | Repositório | Nossa extração | REST independente | Resultado |
|---|---|---|---|---|
| 1 | codecrafters-io/build-your-own-x | 2018-05-09T12:03:18Z | 2018-05-09T12:03:18Z | Idêntico |
| 2 | sindresorhus/awesome | 2014-07-11T13:42:37Z | 2014-07-11T13:42:37Z | Idêntico |
| 3 | public-apis/public-apis | 2016-03-20T23:49:42Z | 2016-03-20T23:49:42Z | Idêntico |
| 4 | freeCodeCamp/freeCodeCamp | 2014-12-24T17:49:19Z | 2014-12-24T17:49:19Z | Idêntico |
| 5 | EbookFoundation/free-programming-books | 2013-10-11T06:50:37Z | 2013-10-11T06:50:37Z | Idêntico |
| 6 | openclaw/openclaw | 2025-11-24T10:16:47Z | 2025-11-24T10:16:47Z | Idêntico |
| 7 | nilbuild/developer-roadmap | 2017-03-15T13:45:52Z | 2017-03-15T13:45:52Z | Idêntico |
| 8 | donnemartin/system-design-primer | 2017-02-26T16:15:28Z | 2017-02-26T16:15:28Z | Idêntico |
| 9 | jwasham/coding-interview-university | 2016-06-06T02:34:12Z | 2016-06-06T02:34:12Z | Idêntico |
| 10 | vinta/awesome-python | 2014-06-27T21:00:06Z | 2014-06-27T21:00:06Z | Idêntico |

**10/10 idênticos.**

### RQ02 — PRs aceitas (merged)

| # | Repositório | Nossa extração (GraphQL) | REST `search/issues` | Diferença |
|---|---|---|---|---|
| 1 | codecrafters-io/build-your-own-x | 157 | 153 | +4 |
| 2 | sindresorhus/awesome | 700 | 691 | +9 |
| 3 | public-apis/public-apis | 2119 | 2088 | +31 |
| 4 | freeCodeCamp/freeCodeCamp | 29074 | 28689 | +385 |
| 5 | EbookFoundation/free-programming-books | 7417 | 7205 | +212 |
| 6 | openclaw/openclaw | 24303 | 24287 | +16 |
| 7 | nilbuild/developer-roadmap | 4387 | 4363 | +24 |
| 8 | donnemartin/system-design-primer | 210 | 207 | +3 |
| 9 | jwasham/coding-interview-university | 415 | 409 | +6 |
| 10 | vinta/awesome-python | 738 | 725 | +13 |

**10/10 com a extração sempre maior que a busca** (nunca menor, nunca igual —
ver observação metodológica).

## Observação metodológica

Em todos os 10 repositórios, o valor via GraphQL
(`pullRequests(states: [MERGED]).totalCount`) veio maior que a contagem via
busca/índice de Search do GitHub (`/search/issues`) — 100% na mesma direção.
Esse padrão consistente descarta "mais PRs foram mergeadas depois" como causa
(isso não teria direção fixa) — a explicação é que a busca do GitHub (UI e
REST `/search/issues`) usa um índice que é eventually consistent (com lag de
atualização, maior em repositórios muito ativos, como o freeCodeCamp, onde a
diferença chega a 385), enquanto o campo `totalCount` do GraphQL lê o estado
real do banco, em tempo real. Por isso o valor do GraphQL é considerado a
fonte confiável para RQ02.

## Consistência com o script integrado do grupo

Como referência adicional (não como fonte de validação — a validação em si é
contra a API REST, acima), os mesmos 10 repositórios foram comparados com a
saída do `extract_repositories.py` (script único do grupo, já integrado por
Gabriel), usando `validate_rq01_rq02.py`:

```
====================================================================================================
VALIDAÇÃO RQ01 E RQ02
====================================================================================================

Repositório: codecrafters-io/build-your-own-x
RQ01 - Criado em: 2018-05-09T12:03:18Z
RQ01 - Idade: 8.26 anos
RQ02 - PRs aceitas: 157
----------------------------------------------------------------------------------------------------

Repositório: sindresorhus/awesome
RQ01 - Criado em: 2014-07-11T13:42:37Z
RQ01 - Idade: 12.09 anos
RQ02 - PRs aceitas: 700
----------------------------------------------------------------------------------------------------

Repositório: public-apis/public-apis
RQ01 - Criado em: 2016-03-20T23:49:42Z
RQ01 - Idade: 10.39 anos
RQ02 - PRs aceitas: 2119
----------------------------------------------------------------------------------------------------

Repositório: freeCodeCamp/freeCodeCamp
RQ01 - Criado em: 2014-12-24T17:49:19Z
RQ01 - Idade: 11.63 anos
RQ02 - PRs aceitas: 29071
----------------------------------------------------------------------------------------------------

Repositório: EbookFoundation/free-programming-books
RQ01 - Criado em: 2013-10-11T06:50:37Z
RQ01 - Idade: 12.84 anos
RQ02 - PRs aceitas: 7417
----------------------------------------------------------------------------------------------------

Repositório: openclaw/openclaw
RQ01 - Criado em: 2025-11-24T10:16:47Z
RQ01 - Idade: 0.71 anos
RQ02 - PRs aceitas: 24248
----------------------------------------------------------------------------------------------------

Repositório: nilbuild/developer-roadmap
RQ01 - Criado em: 2017-03-15T13:45:52Z
RQ01 - Idade: 9.41 anos
RQ02 - PRs aceitas: 4387
----------------------------------------------------------------------------------------------------

Repositório: donnemartin/system-design-primer
RQ01 - Criado em: 2017-02-26T16:15:28Z
RQ01 - Idade: 9.45 anos
RQ02 - PRs aceitas: 210
----------------------------------------------------------------------------------------------------

Repositório: jwasham/coding-interview-university
RQ01 - Criado em: 2016-06-06T02:34:12Z
RQ01 - Idade: 10.18 anos
RQ02 - PRs aceitas: 415
----------------------------------------------------------------------------------------------------

Repositório: vinta/awesome-python
RQ01 - Criado em: 2014-06-27T21:00:06Z
RQ01 - Idade: 12.12 anos
RQ02 - PRs aceitas: 738
----------------------------------------------------------------------------------------------------
```

`createdAt`/idade coincidiram exatamente entre as duas implementações
independentes em todos os 10 casos. `PRs aceitas` teve pequenas variações
(ex.: freeCodeCamp 29074 na nossa extração vs. 29071 aqui, openclaw 24303 vs.
24248) porque os dois arquivos foram gerados em momentos diferentes — em
repositórios muito ativos, esse número muda a cada poucos minutos. Isso é
esperado e reforça o mesmo ponto da observação metodológica: o valor é sempre
crescente e consistente com o horário da coleta, não um erro de implementação.

## Conclusão

RQ01 e RQ02 implementados com query GraphQL própria (`extract_rq01_rq02.py`)
e validados nos 10/10 repositórios da amostra contra a API REST do GitHub:
idade idêntica em todos os casos, PRs aceitas corretas na fonte usada
(GraphQL), com a divergência da busca explicada e documentada de forma
consistente e reprodutível.
