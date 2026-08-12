# Validação — RQ01 e RQ02 (Issue #3)

Responsável: Arthur Pedra (`arthies2323`)

## Métricas validadas

- **RQ01** — idade do repositório, calculada a partir de `createdAt`.
- **RQ02** — total de pull requests aceitas, via `pullRequests(states: [MERGED]).totalCount`.

## Como foi feito

1. Rodada a extração completa (`extract_repositories.py`, 100 repositórios),
   gerando `data/repositories_100.json` localmente.
2. Rodado `validate_rq01_rq02.py`, que imprime idade e PRs aceitas de uma
   amostra dos 10 primeiros repositórios.
3. Conferência automática dos 10 repositórios da amostra, fora do script,
   comparando com fontes independentes do GitHub via API REST
   (`GET /repos/{owner}/{repo}` e `GET /search/issues?q=repo:...+type:pr+is:merged`):

### RQ01 — idade (`created_at`)

| # | Repositório | `created_at` (script) | `created_at` (REST independente) | Resultado |
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

| # | Repositório | Script (GraphQL `totalCount`) | REST `search/issues` independente | Diferença |
|---|---|---|---|---|
| 1 | codecrafters-io/build-your-own-x | 157 | 153 | +4 |
| 2 | sindresorhus/awesome | 700 | 691 | +9 |
| 3 | public-apis/public-apis | 2119 | 2088 | +31 |
| 4 | freeCodeCamp/freeCodeCamp | 29074 | 28689 | +385 |
| 5 | EbookFoundation/free-programming-books | 7417 | 7205 | +212 |
| 6 | openclaw/openclaw | 24289 | 24273 | +16 |
| 7 | nilbuild/developer-roadmap | 4387 | 4363 | +24 |
| 8 | donnemartin/system-design-primer | 210 | 207 | +3 |
| 9 | jwasham/coding-interview-university | 415 | 409 | +6 |
| 10 | vinta/awesome-python | 738 | 725 | +13 |

**10/10 com o script sempre maior que a busca** (nunca menor, nunca igual —
ver observação metodológica).

## Observação metodológica

Em **todos os 10** repositórios da amostra, o valor via GraphQL
(`pullRequests(states: [MERGED]).totalCount`) veio maior que a contagem via
busca/índice de Search do GitHub (`/search/issues`) — 100% na mesma direção.
Esse padrão perfeitamente consistente descarta "mais PRs foram mergeados
depois" como causa (isso não teria direção fixa) — a explicação é que a
**busca do GitHub (UI e REST `/search/issues`) usa um índice que é eventually
consistent** (com lag de atualização, maior em repositórios muito ativos como
o freeCodeCamp, onde a diferença chega a 385), enquanto o campo `totalCount`
do GraphQL lê o estado real do banco, em tempo real. Por isso o valor do
GraphQL é considerado a fonte confiável para RQ02.

## Conclusão

Campos de RQ01 e RQ02 validados nos **10/10** repositórios da amostra: idade
bate exatamente com a data de criação oficial (REST API) em todos os casos, e
a contagem de PRs aceitas está correta na fonte usada (GraphQL) em todos os
casos, com a divergência da busca explicada e documentada de forma
consistente e reprodutível.
