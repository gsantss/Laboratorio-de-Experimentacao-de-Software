"""Ponto de entrada do Laboratório de Experimentação de Software.

Uso principal:
    python main.py

O comportamento padrão aproveita os dados já coletados e abre o dashboard.
Para atualizar os dados antes de abrir o dashboard:
    python main.py --refresh

Também é possível executar apenas a coleta:
    python main.py --refresh --collect-only
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
DATA_DIR = ROOT_DIR / "data"

EXTRACT_SCRIPT = SCRIPTS_DIR / "extract_repositories.py"
SNAPSHOT_SCRIPT = SCRIPTS_DIR / "snapshot_board.py"
DASHBOARD_SCRIPT = SCRIPTS_DIR / "dashboard.py"
REPOSITORIES_CSV = DATA_DIR / "repositories_1000.csv"


def banner(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def run_python_script(script: Path, env: dict[str, str]) -> None:
    """Executa um script Python e interrompe o fluxo em caso de erro."""
    banner(f"Executando: {script.name}")
    subprocess.run(
        [sys.executable, "-u", str(script)],
        cwd=ROOT_DIR,
        env=env,
        check=True,
    )


def collect_data(env: dict[str, str]) -> None:
    """Atualiza a amostra de repositórios e o snapshot do GitHub Projects."""
    token = env.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError(
            "GITHUB_TOKEN não foi encontrado. Configure a variável de ambiente antes "
            "de usar --refresh. No PowerShell, por exemplo: "
            '$env:GITHUB_TOKEN = (gh auth token)'
        )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    run_python_script(EXTRACT_SCRIPT, env)
    run_python_script(SNAPSHOT_SCRIPT, env)


def launch_dashboard(env: dict[str, str]) -> None:
    """Inicia o dashboard Streamlit usando o mesmo interpretador Python."""
    banner("Iniciando dashboard")
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                str(DASHBOARD_SCRIPT),
            ],
            cwd=ROOT_DIR,
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "Não foi possível iniciar o Streamlit. Instale as dependências com: "
            f"{sys.executable} -m pip install -r scripts/requirements.txt"
        ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Orquestra coleta, snapshot do board e dashboard do laboratório."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="Atualiza os 1000 repositórios e o snapshot do board antes do dashboard.",
    )
    parser.add_argument(
        "--collect-only",
        action="store_true",
        help="Executa a coleta e encerra sem abrir o dashboard (implica --refresh).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    should_refresh = args.refresh or args.collect_only or not REPOSITORIES_CSV.exists()

    try:
        if should_refresh:
            collect_data(env)
        else:
            banner("Usando dados locais existentes")
            print(f"Arquivo encontrado: {REPOSITORIES_CSV}")
            print("Use --refresh quando quiser atualizar os dados do GitHub.")

        if not args.collect_only:
            launch_dashboard(env)

    except (RuntimeError, subprocess.CalledProcessError, KeyboardInterrupt) as exc:
        if isinstance(exc, KeyboardInterrupt):
            print("\nExecução interrompida pelo usuário.")
            return 130

        print(f"\nERRO: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
