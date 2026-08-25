import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
DATA_1000 = BASE_DIR / "data" / "repositories_1000.csv"
DATA_100 = BASE_DIR / "data" / "repositories_100.json"

st.set_page_config(
    page_title="Lab01 — Dashboard de repositórios populares",
    layout="wide",
)


# ============================================================
# CARREGAR DADOS
# ============================================================

@st.cache_data
def load_data(path: Path, mtime: float) -> pd.DataFrame:
    if path.suffix == ".csv":
        return pd.read_csv(path)
    import json
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    return pd.DataFrame(payload["repositories"])


def get_dataframe() -> pd.DataFrame | None:
    if DATA_1000.exists():
        return load_data(DATA_1000, DATA_1000.stat().st_mtime)
    if DATA_100.exists():
        return load_data(DATA_100, DATA_100.stat().st_mtime)
    return None


# ============================================================
# RODAR SCRIPTS DE EXTRAÇÃO
# ============================================================

def run_script(script_name: str, token: str) -> None:
    env = os.environ.copy()
    env["GITHUB_TOKEN"] = token

    with st.spinner(f"Rodando {script_name}... isso pode demorar alguns minutos"):
        result = subprocess.run(
            [sys.executable, str(BASE_DIR / script_name)],
            cwd=BASE_DIR,
            env=env,
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:
        st.success(f"{script_name} rodou com sucesso.")
    else:
        st.error(f"{script_name} terminou com erro (código {result.returncode}).")

    with st.expander("Ver saída completa"):
        st.code(result.stdout + "\n" + result.stderr)

    st.cache_data.clear()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Lab01 — Controles")

token_input = st.sidebar.text_input(
    "GITHUB_TOKEN",
    value=os.environ.get("GITHUB_TOKEN", ""),
    type="password",
    help="Se já rodou `$env:GITHUB_TOKEN = (gh auth token)` no terminal antes de abrir o dashboard, isso já vem preenchido.",
)

st.sidebar.markdown("### Rodar extrações")

if st.sidebar.button("Extrair 1000 repositórios (extract_repositories.py)"):
    if not token_input:
        st.sidebar.error("Preencha o GITHUB_TOKEN antes de rodar.")
    else:
        run_script("extract_repositories.py", token_input)

if st.sidebar.button("Extrair amostra RQ01/RQ02 (extract_rq01_rq02.py)"):
    if not token_input:
        st.sidebar.error("Preencha o GITHUB_TOKEN antes de rodar.")
    else:
        run_script("extract_rq01_rq02.py", token_input)

if st.sidebar.button("Recarregar dados (sem rodar nada)"):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# CORPO PRINCIPAL
# ============================================================

st.title("Dashboard — Características de repositórios populares do GitHub")
st.caption("Laboratório de Experimentação de Software — Lab01")

df = get_dataframe()

if df is None:
    st.warning(
        "Nenhum dado encontrado ainda. Use os botões na barra lateral para "
        "rodar uma extração, ou gere `data/repositories_1000.csv` manualmente."
    )
    st.stop()

st.success(f"{len(df)} repositórios carregados.")

with st.expander("Filtros"):
    min_stars, max_stars = int(df["stars"].min()), int(df["stars"].max())
    star_range = st.slider("Faixa de estrelas", min_stars, max_stars, (min_stars, max_stars))
    languages = sorted(df["primary_language"].dropna().unique().tolist())
    selected_languages = st.multiselect("Linguagem", languages, default=[])

filtered = df[(df["stars"] >= star_range[0]) & (df["stars"] <= star_range[1])]
if selected_languages:
    filtered = filtered[filtered["primary_language"].isin(selected_languages)]

st.caption(f"{len(filtered)} repositórios após filtro")

tabs = st.tabs([
    "Visão geral", "RQ01 — Idade", "RQ02 — PRs aceitas", "RQ03 — Releases",
    "RQ04 — Última atualização", "RQ05 — Linguagem", "RQ06 — Issues fechadas",
])

with tabs[0]:
    st.subheader("Top 20 por estrelas")
    st.dataframe(
        filtered.sort_values("stars", ascending=False)
        .head(20)[["name_with_owner", "stars", "primary_language", "age_years", "accepted_pull_requests"]],
        use_container_width=True,
    )

with tabs[1]:
    st.subheader("RQ01 — Sistemas populares são maduros/antigos?")
    col1, col2 = st.columns(2)
    col1.metric("Idade mediana", f"{filtered['age_years'].median():.2f} anos")
    col2.metric("Idade média", f"{filtered['age_years'].mean():.2f} anos")
    st.plotly_chart(px.histogram(filtered, x="age_years", nbins=40, title="Distribuição de idade (anos)"), use_container_width=True)

with tabs[2]:
    st.subheader("RQ02 — Sistemas populares recebem muita contribuição externa?")
    col1, col2 = st.columns(2)
    col1.metric("PRs aceitas — mediana", f"{filtered['accepted_pull_requests'].median():.0f}")
    col2.metric("PRs aceitas — média", f"{filtered['accepted_pull_requests'].mean():.0f}")
    st.plotly_chart(px.box(filtered, y="accepted_pull_requests", points="outliers", title="Distribuição de PRs aceitas"), use_container_width=True)

with tabs[3]:
    if "releases" in filtered.columns:
        st.subheader("RQ03 — Sistemas populares lançam releases com frequência?")
        st.metric("Releases — mediana", f"{filtered['releases'].median():.0f}")
        st.plotly_chart(px.histogram(filtered, x="releases", nbins=40, title="Distribuição de releases"), use_container_width=True)
    else:
        st.info("Campo `releases` não encontrado no dataset atual.")

with tabs[4]:
    if "days_since_last_update" in filtered.columns:
        st.subheader("RQ04 — Sistemas populares são atualizados com frequência?")
        st.metric("Dias desde a última atualização — mediana", f"{filtered['days_since_last_update'].median():.0f}")
        st.plotly_chart(px.histogram(filtered, x="days_since_last_update", nbins=40, title="Dias desde a última atualização"), use_container_width=True)
    else:
        st.info("Campo `days_since_last_update` não encontrado no dataset atual.")

with tabs[5]:
    if "primary_language" in filtered.columns:
        st.subheader("RQ05 — Sistemas populares são escritos nas linguagens mais populares?")
        lang_counts = filtered["primary_language"].value_counts().head(15).reset_index()
        lang_counts.columns = ["linguagem", "quantidade"]
        st.plotly_chart(px.pie(lang_counts, names="linguagem", values="quantidade", title="Top 15 linguagens primárias"), use_container_width=True)
    else:
        st.info("Campo `primary_language` não encontrado no dataset atual.")

with tabs[6]:
    if "closed_issues_percentage" in filtered.columns:
        st.subheader("RQ06 — Sistemas populares possuem alto percentual de issues fechadas?")
        st.metric("% issues fechadas — mediana", f"{filtered['closed_issues_percentage'].median():.2f}%")
        st.plotly_chart(px.histogram(filtered, x="closed_issues_percentage", nbins=40, title="Distribuição do % de issues fechadas"), use_container_width=True)
    else:
        st.info("Campo `closed_issues_percentage` não encontrado no dataset atual.")
