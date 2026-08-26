import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent
DATA_1000 = ROOT_DIR / "data" / "repositories_1000.csv"
DATA_100 = ROOT_DIR / "data" / "repositories_100.json"

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

def render_log(lines: list[str]) -> None:
    """Mostra o log numa caixa com scroll que acompanha o final automaticamente."""
    import html as html_lib
    import streamlit.components.v1 as components

    text = html_lib.escape("\n".join(lines[-500:]))
    components.html(
        f"""
        <div id="log-box" style="
            height: 300px; overflow-y: auto; background: #0e1117; color: #fafafa;
            font-family: monospace; font-size: 12px; padding: 8px; border-radius: 4px;
            white-space: pre-wrap; word-break: break-word;
        ">{text}</div>
        <script>
            var box = document.getElementById("log-box");
            box.scrollTop = box.scrollHeight;
        </script>
        """,
        height=310,
    )


def run_script(script_name: str, token: str) -> None:
    """Roda o script mostrando o log em tempo real, igual rodando no terminal."""
    env = os.environ.copy()
    env["GITHUB_TOKEN"] = token
    env["PYTHONIOENCODING"] = "utf-8"

    with st.status(f"Rodando {script_name}...", expanded=True) as status:
        process = subprocess.Popen(
            [sys.executable, "-u", str(BASE_DIR / script_name)],
            cwd=BASE_DIR,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
        )

        log_lines: list[str] = []
        log_area = st.empty()

        for line in process.stdout:
            log_lines.append(line.rstrip("\n"))
            with log_area.container():
                render_log(log_lines)

        process.wait()

        if process.returncode == 0:
            status.update(label=f"{script_name} concluído", state="complete")
        else:
            status.update(label=f"{script_name} terminou com erro (código {process.returncode})", state="error")

    st.cache_data.clear()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Lab01 — Controles")

token_input = os.environ.get("GITHUB_TOKEN", "")

st.sidebar.markdown("### Rodar extração")

if st.sidebar.button("Extrair 1000 repositórios (todas as RQs)"):
    if not token_input:
        st.sidebar.error(
            "GITHUB_TOKEN não encontrado no ambiente. Feche o dashboard e rode "
            '`$env:GITHUB_TOKEN = (gh auth token)` no terminal antes de abrir ele.'
        )
    else:
        run_script("extract_repositories.py", token_input)

if st.sidebar.button("Recarregar dados (sem rodar nada)"):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# CORPO PRINCIPAL
# ============================================================

def styled_histogram(data: pd.DataFrame, x: str, title: str, nbins: int = 40):
    """Histograma com contorno escuro entre as barras, pra dar mais contraste."""
    fig = px.histogram(data, x=x, nbins=nbins, title=title)
    fig.update_traces(marker_line_color="#0e1117", marker_line_width=1.5)
    fig.update_layout(bargap=0.08)
    return fig


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
    st.plotly_chart(styled_histogram(filtered, "age_years", "Distribuição de idade (anos)"), use_container_width=True)

with tabs[2]:
    st.subheader("RQ02 — Sistemas populares recebem muita contribuição externa?")
    col1, col2 = st.columns(2)
    col1.metric("PRs aceitas — mediana", f"{filtered['accepted_pull_requests'].median():.0f}")
    col2.metric("PRs aceitas — média", f"{filtered['accepted_pull_requests'].mean():.0f}")
    prs_log = filtered.assign(log_prs=np.log10(filtered["accepted_pull_requests"] + 1))
    prs_fig = px.histogram(
        prs_log, x="log_prs", nbins=40,
        title="Distribuição de PRs aceitas (escala logarítmica)",
    )
    prs_fig.update_traces(marker_line_color="#0e1117", marker_line_width=1.5)
    prs_fig.update_layout(bargap=0.08)
    prs_fig.update_xaxes(
        tickvals=[0, 1, 2, 3, 4, 5],
        ticktext=["0", "10", "100", "1k", "10k", "100k"],
        title="PRs aceitas",
    )
    st.plotly_chart(prs_fig, use_container_width=True)
    st.caption(
        "Escala logarítmica no eixo X — os dados são muito assimétricos "
        "(mediana de 768, mas repositórios extremos com mais de 100 mil PRs, "
        "e alguns com 0), então em escala normal quase todas as barras "
        "ficariam achatadas perto do zero."
    )

with tabs[3]:
    if "releases" in filtered.columns:
        st.subheader("RQ03 — Sistemas populares lançam releases com frequência?")
        st.metric("Releases — mediana", f"{filtered['releases'].median():.0f}")
        st.plotly_chart(styled_histogram(filtered, "releases", "Distribuição de releases"), use_container_width=True)
    else:
        st.info("Campo `releases` não encontrado no dataset atual.")

with tabs[4]:
    if "days_since_last_update" in filtered.columns:
        st.subheader("RQ04 — Sistemas populares são atualizados com frequência?")
        st.metric("Dias desde a última atualização — mediana", f"{filtered['days_since_last_update'].median():.0f}")
        st.plotly_chart(styled_histogram(filtered, "days_since_last_update", "Dias desde a última atualização"), use_container_width=True)
    else:
        st.info("Campo `days_since_last_update` não encontrado no dataset atual.")

with tabs[5]:
    if "primary_language" in filtered.columns:
        st.subheader("RQ05 — Sistemas populares são escritos nas linguagens mais populares?")
        lang_counts = filtered["primary_language"].value_counts().head(15).reset_index()
        lang_counts.columns = ["linguagem", "quantidade"]
        pie_fig = px.pie(lang_counts, names="linguagem", values="quantidade", title="Top 15 linguagens primárias")
        pie_fig.update_traces(marker_line_color="#0e1117", marker_line_width=1.5)
        st.plotly_chart(pie_fig, use_container_width=True)
    else:
        st.info("Campo `primary_language` não encontrado no dataset atual.")

with tabs[6]:
    if "closed_issues_percentage" in filtered.columns:
        st.subheader("RQ06 — Sistemas populares possuem alto percentual de issues fechadas?")
        st.metric("% issues fechadas — mediana", f"{filtered['closed_issues_percentage'].median():.2f}%")
        st.plotly_chart(styled_histogram(filtered, "closed_issues_percentage", "Distribuição do % de issues fechadas"), use_container_width=True)
    else:
        st.info("Campo `closed_issues_percentage` não encontrado no dataset atual.")
