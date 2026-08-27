# Laboratório de Experimentação de Software

Projeto do laboratório para coleta e análise dos repositórios mais populares do GitHub.

## Execução rápida

1. Instale as dependências:

```bash
python -m pip install -r scripts/requirements.txt
```

2. Para abrir o dashboard usando os dados já existentes:

```bash
python main.py
```

3. Para atualizar os 1000 repositórios, gerar o snapshot do board e depois abrir o dashboard:

```bash
python main.py --refresh
```

4. Para apenas atualizar os dados, sem abrir o Streamlit:

```bash
python main.py --refresh --collect-only
```

## GitHub Token

A atualização dos dados exige a variável de ambiente `GITHUB_TOKEN`.

PowerShell, usando GitHub CLI:

```powershell
$env:GITHUB_TOKEN = (gh auth token)
python main.py --refresh
```

## Estrutura principal

- `main.py`: orquestra coleta, snapshot do board e dashboard.
- `scripts/extract_repositories.py`: coleta as métricas RQ01–RQ06 via GitHub GraphQL.
- `scripts/snapshot_board.py`: gera o snapshot do GitHub Projects para a sprint.
- `scripts/dashboard.py`: dashboard Streamlit com RQ01–RQ07, correlações e visão do board.
- `data/`: datasets e snapshots gerados.
- `Relatorios/`: relatório consolidado do laboratório.

## Configuração opcional do snapshot

O snapshot aceita variáveis de ambiente para evitar edição manual do código:

```powershell
$env:PROJECT_OWNER = "gsantss"
$env:PROJECT_NUMBER = "2"
$env:SPRINT_LABEL = "Lab01S02"
```
