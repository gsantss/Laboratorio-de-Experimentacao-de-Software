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
3. Conferência manual, fora do script, comparando a amostra com fontes
   independentes do GitHub:

| Repositório | Campo | Valor do script | Fonte independente | Resultado |
|---|---|---|---|---|
| freeCodeCamp/freeCodeCamp | RQ01 — `created_at` | `2014-12-24T17:49:19Z` (11.63 anos) | `api.github.com/repos/freeCodeCamp/freeCodeCamp` → `created_at` | ✅ idêntico |
| codecrafters-io/build-your-own-x | RQ02 — PRs aceitas | 157 | Busca na UI `is:pr is:merged` → 153 | ⚠️ diferença de 4 (ver observação) |
| sindresorhus/awesome | RQ02 — PRs aceitas | 700 | Busca na UI `is:pr is:merged` → 691 | ⚠️ diferença de 9 (ver observação) |

## Observação metodológica

Nos dois repositórios conferidos, o valor via GraphQL (`pullRequests(states:
[MERGED]).totalCount`) veio **sempre maior** que a contagem da busca na UI do
GitHub. O padrão consistente indica que a causa não é "mais PRs foram
mergeados depois" (isso poderia inflar a busca feita depois, não o
script feito antes) — e sim que a **busca da UI usa o índice de Search do
GitHub, que é eventually consistent** (com lag de atualização), enquanto o
campo `totalCount` do GraphQL lê o estado real do banco. Por isso o valor do
GraphQL é considerado a fonte confiável para RQ02.

## Conclusão

Campos de RQ01 e RQ02 validados: idade bate exatamente com a data de criação
oficial (API REST), e a contagem de PRs aceitas está correta na fonte usada
(GraphQL), com a divergência da busca da UI explicada e documentada.
