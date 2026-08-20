# LAB01S02 — Relatório de Validação das RQ05 e RQ06

> **Laboratório de Experimentação de Software**  
> Mineração de repositórios populares do GitHub

---

## 1. Resumo executivo

Este relatório apresenta a validação das métricas associadas às questões de pesquisa **RQ05** e **RQ06** para um conjunto de **1000 repositórios populares do GitHub**.

A análise possui caráter **descritivo e de validação dos dados**, verificando distribuição, valores ausentes, valores inválidos e possíveis outliers.

| Questão | Métrica | Observações válidas | Resultado principal |
|---|---|---:|---:|
| **RQ05** | Linguagem primária (categórica) | 913 | Python lidera (228 repos) |
| **RQ06** | % de issues fechadas | 957 | mediana 87.57% |

---

## 2. Questões de pesquisa

### RQ05 — Sistemas populares são escritos nas linguagens mais populares?

**Métrica utilizada:** linguagem primária de cada repositório (`primary_language`).

**Fonte de referência para "linguagens mais populares":** **TIOBE Index — agosto/2026** (https://www.tiobe.com/tiobe-index/), mantida fixa em todo o laboratório (mesma referência do S01).

### RQ06 — Sistemas populares possuem alto percentual de issues fechadas?

**Métrica utilizada:** razão entre issues fechadas e total de issues, expressa em percentual (`closed_issues_percentage`).

> Repositórios com **0 issues** têm percentual indefinido e são tratados como valores ausentes na RQ06.

---

## 3. Hipóteses informais

**H05 — RQ05:** espera-se que os repositórios populares sejam escritos majoritariamente em linguagens de alto ranking de popularidade, com predominância das linguagens mais usadas no ecossistema open-source (ex.: Python, JavaScript/TypeScript).

**H06 — RQ06:** espera-se um percentual mediano **alto** de issues fechadas, já que projetos populares tendem a ter manutenção ativa e triagem contínua do backlog.

> As hipóteses acima são informais. Nesta etapa, os resultados são apresentados de forma descritiva e ainda não constituem conclusões definitivas.

---

## 4. Metodologia

Foram considerados **1000 repositórios**, obtidos pela paginação do script único do grupo (Issue #15) e lidos a partir do arquivo `data/repositories_1000.csv`.

Para a validação foram realizadas as seguintes verificações:

1. análise de valores ausentes;
2. identificação de valores estruturalmente inválidos;
3. análise da distribuição dos dados;
4. detecção de outliers pelo método IQR (aplicável apenas à RQ06, numérica).

> **Nota metodológica:** a RQ05 é uma variável **categórica** (nome da linguagem). Média, desvio padrão e outliers por IQR não se aplicam a categorias; por isso a RQ05 é validada por **distribuição de frequência**, contagem de valores ausentes e cruzamento com o ranking TIOBE. A RQ06 é **numérica** e recebe o tratamento estatístico completo.

---

## 5. RQ05 — Análise da linguagem primária

### 5.1 Distribuição de frequência (top 15)

| Linguagem | Repositórios | Percentual | TIOBE |
|---|---:|---:|---:|
| Python | 228 | 22,80% | #1 |
| TypeScript | 174 | 17,40% | — |
| JavaScript | 111 | 11,10% | #6 |
| Go | 76 | 7,60% | #14 |
| Rust | 57 | 5,70% | #10 |
| C++ | 41 | 4,10% | #3 |
| Java | 41 | 4,10% | #4 |
| Jupyter Notebook | 24 | 2,40% | — |
| C | 21 | 2,10% | #2 |
| Shell | 20 | 2,00% | — |
| Ruby | 13 | 1,30% | #16 |
| HTML | 11 | 1,10% | — |
| Swift | 10 | 1,00% | #17 |
| Kotlin | 9 | 0,90% | — |
| C# | 8 | 0,80% | #5 |
| *(sem linguagem)* | 87 | 8,70% | — |

Linguagens distintas: **43** (sendo **12** presentes em um único repositório).

### 5.2 Cruzamento com o TIOBE Index (ago/2026)

Dos **913** repositórios com linguagem definida, **610** (66,81%) usam uma linguagem presente no **top 20 do TIOBE**, enquanto **303** (33,19%) usam linguagens fora dele.

### 5.3 Qualidade dos dados

- Repositórios **sem linguagem primária**: **87** (8,70%) — em geral coleções (*awesome*) e repositórios de documentação/Markdown, o que é esperado e não indica erro de coleta.

### 5.4 Interpretação preliminar

A linguagem mais frequente é **Python** (228 repositórios, 22,80%). A maioria dos repositórios com linguagem usa uma das linguagens de topo do TIOBE, o que oferece suporte preliminar à hipótese H05, ainda que linguagens muito populares no GitHub (como TypeScript) possam não figurar no topo do TIOBE — divergência a ser discutida na etapa de análise.

---

## 6. RQ06 — Análise do percentual de issues fechadas

### 6.1 Estatísticas descritivas

| Medida | Resultado |
|---|---:|
| Observações válidas | 957 |
| Média | 80.26% |
| Mediana | 87.57% |
| Mínimo | 7.69% |
| Máximo | 100% |
| Desvio padrão | 21.04 |
| Q1 | 70.49% |
| Q3 | 96.81% |
| IQR | 26.32 |

### 6.2 Distribuição

| Faixa de issues fechadas | Repositórios | Percentual |
|---|---:|---:|
| 0-20% | 12 | 1,25% |
| 20-40% | 57 | 5,96% |
| 40-60% | 94 | 9,82% |
| 60-80% | 179 | 18,70% |
| 80-100% | 615 | 64,26% |

> Percentuais calculados sobre as observações válidas (957 repositórios com pelo menos uma issue).

### 6.3 Qualidade dos dados

- Repositórios sem issues (percentual indefinido): **43** (4,30%)
- Percentuais fora do intervalo [0, 100] (inválidos): **0**
- Issues fechadas maiores que o total (inválidos): **0**
- Potenciais outliers (IQR): **40** (4,18%)

Limites utilizados pelo IQR: **31.01%** até **136.29%**.

#### Exemplos de valores extremos (menores percentuais)

| Posição | Repositório | % fechadas |
|---:|---|---:|
| 250 | `ComposioHQ/awesome-claude-skills` | 7.69 |
| 714 | `floodsung/Deep-Learning-Papers-Reading-Roadmap` | 8.62 |
| 775 | `anthropics/prompt-eng-interactive-tutorial` | 9.52 |
| 537 | `elder-plinius/CL4R1T4S` | 10.13 |
| 916 | `anthropics/financial-services` | 10.23 |
| 506 | `type-challenges/type-challenges` | 10.97 |
| 46 | `anthropics/skills` | 13.46 |
| 294 | `kelseyhightower/nocode` | 14.84 |
| 625 | `zbezj/HEU_KMS_Activator` | 15.61 |
| 959 | `anthropics/claude-plugins-official` | 16.09 |

> Exibindo os 10 menores valores entre 40 potenciais outliers.

### 6.4 Interpretação preliminar

A mediana observada foi de **87.57%**, enquanto a média foi de **80.26%**. A mediana superior à média sugere uma distribuição assimétrica à esquerda: a maioria dos projetos fecha a grande parte de suas issues, e uma minoria com percentual baixo puxa a média para baixo. Nesta sprint, o resultado é usado principalmente para verificar a consistência da coleta; a conclusão definitiva da RQ06 será feita na etapa de análise.

---

## 7. Resumo da qualidade dos dados

| Verificação | RQ05 | RQ06 |
|---|---:|---:|
| Observações válidas | 913 | 957 |
| Valores ausentes | 87 | 43 |
| Valores inválidos | 0 | 0 |
| Potenciais outliers | N/A (categórica) | 40 |

---

## 8. Ameaças à validade

- os dados do GitHub são dinâmicos e podem mudar após o momento da coleta;
- a ausência de linguagem primária ocorre em repositórios de conteúdo/documentação e não representa falha de coleta;
- o percentual de issues fechadas não distingue issues legítimas de spam ou duplicatas fechadas em massa;
- o ranking TIOBE mede popularidade por volume de buscas na web e pode divergir da popularidade específica do ecossistema open-source do GitHub;
- a popularidade foi operacionalizada pela quantidade de estrelas, conforme o critério de seleção adotado pelo laboratório.

---

## 9. Conclusão da validação

A validação foi realizada sobre **1000 repositórios**, contemplando as métricas necessárias para RQ05 e RQ06.

Para a **RQ05**, a linguagem mais frequente foi **Python** e **66,81%** dos repositórios com linguagem usam uma linguagem do top 20 do TIOBE. Para a **RQ06**, a mediana do percentual de issues fechadas foi de **87.57%**.

Os resultados desta etapa fornecem evidências sobre a consistência das métricas coletadas e constituem a base para as análises e conclusões das etapas seguintes do laboratório.

---

*Relatório gerado automaticamente em 2026-08-20 02:27:37 UTC.*