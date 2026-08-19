# LAB01S02 — Relatório de Validação das RQ03 e RQ04

> **Laboratório de Experimentação de Software**  
> Mineração de repositórios populares do GitHub

---

## 1. Resumo executivo

Este relatório apresenta a validação das métricas associadas às questões de pesquisa **RQ03** e **RQ04** para um conjunto de **1000 repositórios populares do GitHub**.

A análise possui caráter **descritivo e de validação dos dados**, verificando distribuição, valores ausentes, valores inválidos e possíveis outliers.

| Questão | Métrica | Observações válidas | Mediana |
|---|---|---:|---:|
| **RQ03** | Total de releases | 1000 | 39 releases |
| **RQ04** | Dias desde a última atualização | 1000 | 0 dias |

---

## 2. Questões de pesquisa

### RQ03 — Sistemas populares lançam releases com frequência?

**Métrica utilizada:** quantidade total de releases registradas no repositório.

### RQ04 — Sistemas populares são atualizados com frequência?

**Métrica utilizada:** quantidade de dias transcorridos desde a última atualização registrada no repositório.

> Na RQ04, valores menores representam uma atualização > mais recente.

---

## 3. Hipóteses informais

**H03 — RQ03:** espera-se que projetos populares apresentem quantidade significativa de releases, considerando que projetos amplamente utilizados tendem a possuir ciclos recorrentes de evolução e entrega.

**H04 — RQ04:** espera-se que projetos populares tenham sido atualizados recentemente, apresentando um número relativamente baixo de dias desde sua última atualização.

> As hipóteses acima são informais. Nesta etapa, > os resultados são apresentados de forma descritiva > e ainda não constituem conclusões definitivas.

---

## 4. Metodologia

Foram considerados **1000 repositórios** obtidos por meio da API GraphQL do GitHub.

Para a validação das métricas RQ03 e RQ04 foram realizadas quatro verificações principais:

1. análise de valores ausentes;
2. identificação de valores estruturalmente inválidos;
3. análise da distribuição dos dados;
4. identificação de possíveis outliers.

Os outliers foram identificados utilizando o método do **Intervalo Interquartil (IQR)**. Foram considerados potenciais outliers os valores abaixo de `Q1 - 1,5 × IQR` ou acima de `Q3 + 1,5 × IQR`.

Além disso, foram calculadas medidas descritivas como **média, mediana, mínimo, máximo, quartis e desvio padrão**.

---

## 5. RQ03 — Análise do total de releases

### 5.1 Estatísticas descritivas

| Medida | Resultado |
|---|---:|
| Observações válidas | 1000 |
| Média | 126.61 releases |
| Mediana | 39 releases |
| Mínimo | 0 releases |
| Máximo | 1000 releases |
| Desvio padrão | 212.73 |
| Q1 | 0 |
| Q3 | 147 |
| IQR | 147 |

### 5.2 Distribuição

| Faixa de releases | Repositórios | Percentual |
|---|---:|---:|
| 0 releases | 286 | 28,60% |
| 1-10 releases | 76 | 7,60% |
| 11-50 releases | 177 | 17,70% |
| 51-100 releases | 118 | 11,80% |
| 101-500 releases | 274 | 27,40% |
| mais de 500 releases | 69 | 6,90% |

### 5.3 Qualidade dos dados

- Valores ausentes: **0** (0,00%)
- Valores negativos inválidos: **0**
- Potenciais outliers: **93** (9,30%)

Limites utilizados pelo IQR: **-220.50** até **367.50** releases.

#### Exemplos de valores extremos

| Posição | Repositório | Releases |
|---:|---|---:|
| 60 | `langchain-ai/langchain` | 1000 |
| 64 | `vercel/next.js` | 1000 |
| 81 | `ggml-org/llama.cpp` | 1000 |
| 83 | `electron/electron` | 1000 |
| 147 | `storybookjs/storybook` | 1000 |
| 151 | `home-assistant/core` | 1000 |
| 162 | `zed-industries/zed` | 1000 |
| 190 | `lobehub/lobehub` | 1000 |
| 272 | `ruvnet/ruflo` | 1000 |
| 331 | `withastro/astro` | 1000 |

> Exibindo os 10 maiores valores entre 93 potenciais outliers.

### 5.4 Interpretação preliminar

A mediana observada foi de **39 releases**, enquanto a média foi de **126.61 releases**.

A comparação entre média, mediana, dispersão e outliers auxilia na identificação de uma possível assimetria da distribuição. Repositórios com números muito elevados de releases podem aumentar a média e torná-la menos representativa do comportamento típico.

Nesta sprint, esses resultados são utilizados principalmente para verificar a consistência da coleta. A conclusão definitiva da RQ03 será realizada na etapa de análise do laboratório.

---

## 6. RQ04 — Análise do tempo desde a última atualização

### 6.1 Estatísticas descritivas

| Medida | Resultado |
|---|---:|
| Observações válidas | 1000 |
| Média | -0.09 dias |
| Mediana | 0 dias |
| Mínimo | -1 dias |
| Máximo | 2 dias |
| Desvio padrão | 0.35 dias |
| Q1 | 0 dias |
| Q3 | 0 dias |
| IQR | 0 dias |

### 6.2 Distribuição

| Tempo desde a atualização | Repositórios | Percentual |
|---|---:|---:|
| 0 dias | 984 | 98,40% |
| 1-7 dias | 16 | 1,60% |
| 8-30 dias | 0 | 0,00% |
| 31-90 dias | 0 | 0,00% |
| 91-365 dias | 0 | 0,00% |
| mais de 365 dias | 0 | 0,00% |

### 6.3 Qualidade dos dados

- Datas `updatedAt` ausentes: **0** (0,00%)
- Valores calculados em dias ausentes: **0** (0,00%)
- Valores negativos: **105**
- Potenciais outliers: **121** (12,10%)

Limites utilizados pelo IQR: **0** até **0 dias**.

#### Repositórios há mais tempo sem atualização

| Posição | Repositório | Dias |
|---:|---|---:|
| 667 | `bailicangdu/vue2-elm` | 2 |
| 887 | `nativefier/nativefier` | 2 |
| 271 | `base/node` | 1 |
| 377 | `angular/angular.js` | 1 |
| 423 | `ElemeFE/element` | 1 |
| 717 | `lm-sys/FastChat` | 1 |
| 748 | `naptha/tesseract.js` | 1 |
| 791 | `LAION-AI/Open-Assistant` | 1 |
| 827 | `inkonchain/docs` | 1 |
| 830 | `inkonchain/node` | 1 |

> Exibindo os 10 maiores valores entre 121 potenciais outliers.

### 6.4 Interpretação preliminar

A mediana de tempo desde a última atualização foi de **0 dias**, enquanto a média foi de **-0.09 dias**.

Como valores menores representam atualizações mais recentes, a distribuição permite observar a concentração de projetos que permanecem ativos e também identificar repositórios que apresentam períodos muito maiores sem atualização.

Assim como na RQ03, esta etapa não estabelece ainda um limiar para classificar formalmente um projeto como "frequentemente atualizado". Os resultados são descritivos e servirão de base para a análise posterior.

---

## 7. Resumo da qualidade dos dados

| Verificação | RQ03 | RQ04 |
|---|---:|---:|
| Valores válidos | 1000 | 1000 |
| Valores ausentes | 0 | 0 |
| Valores inválidos | 0 | 105 |
| Potenciais outliers | 93 | 121 |

> **Resultado da validação:** foram encontradas > ocorrências que devem ser verificadas antes da > análise final.

---

## 8. Ameaças à validade

Alguns fatores devem ser considerados durante a interpretação dos resultados:

- os dados do GitHub são dinâmicos e podem mudar após o momento da coleta;
- a quantidade total de releases não considera diretamente o intervalo temporal entre elas;
- a data de atualização representa a informação fornecida pelo GitHub para o repositório e deve ser interpretada conforme a definição utilizada na coleta;
- valores extremos podem representar projetos legítimos e não necessariamente erros;
- a popularidade foi operacionalizada pela quantidade de estrelas, conforme o critério de seleção adotado pelo laboratório.

---

## 9. Conclusão da validação

A validação foi realizada sobre **1000 repositórios**, contemplando as métricas necessárias para RQ03 e RQ04.

Foram analisadas estatísticas descritivas, distribuição, valores ausentes, valores inválidos e possíveis outliers.

Para a **RQ03**, a mediana observada foi de **39 releases**. Para a **RQ04**, a mediana foi de **0 dias desde a última atualização**.

Os resultados desta etapa fornecem evidências sobre a consistência das métricas coletadas e constituem a base para as análises e conclusões das etapas seguintes do laboratório.

---

*Relatório gerado automaticamente em 2026-08-19 14:48:54 UTC.*