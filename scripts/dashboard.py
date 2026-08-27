from __future__ import annotations

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
DATA_DIR = ROOT_DIR / "data"
DATA_1000 = DATA_DIR / "repositories_1000.csv"
DATA_100 = DATA_DIR / "repositories_100.json"

st.set_page_config(
    page_title="Lab01 — Repositórios populares",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 1.8rem; padding-bottom: 3rem;}
        [data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.22);
            padding: 0.9rem;
            border-radius: 0.75rem;
        }
        div[data-testid="stDataFrame"] {border-radius: 0.65rem; overflow: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CARREGAMENTO DE DADOS
# ============================================================

@st.cache_data
def load_data(path: Path, mtime: float) -> pd.DataFrame:
    del mtime  # usado apenas para invalidar o cache quando o arquivo muda
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)

    import json

    with open(path, "r", encoding="utf-8") as file:
        payload = json.load(file)
    return pd.DataFrame(payload["repositories"])


@st.cache_data
def load_board_snapshots(files: tuple[tuple[str, float], ...]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for filename, _mtime in files:
        path = Path(filename)
        try:
            frames.append(pd.read_csv(path))
        except (OSError, pd.errors.EmptyDataError):
            continue

    if not frames:
        return pd.DataFrame()

    board = pd.concat(frames, ignore_index=True)
    if "snapshot_date" in board.columns:
        board["snapshot_date"] = pd.to_datetime(
            board["snapshot_date"], errors="coerce", utc=True
        )
    return board


def get_dataframe() -> pd.DataFrame | None:
    for path in (DATA_1000, DATA_100):
        if path.exists():
            return load_data(path, path.stat().st_mtime)
    return None


def get_board_dataframe() -> pd.DataFrame:
    files = tuple(
        (str(path), path.stat().st_mtime)
        for path in sorted(DATA_DIR.glob("snapshot_board_*.csv"))
    )
    if not files:
        return pd.DataFrame()
    return load_board_snapshots(files)


# ============================================================
# EXECUÇÃO DOS SCRIPTS
# ============================================================

def render_log(lines: list[str]) -> None:
    """Mostra o log em uma caixa com scroll acompanhando o final."""
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


def run_script(script_name: str, token: str) -> bool:
    """Executa um script e apresenta stdout/stderr em tempo real."""
    env = os.environ.copy()
    env["GITHUB_TOKEN"] = token
    env["PYTHONIOENCODING"] = "utf-8"

    success = False
    with st.status(f"Rodando {script_name}...", expanded=True) as status:
        process = subprocess.Popen(
            [sys.executable, "-u", str(BASE_DIR / script_name)],
            cwd=ROOT_DIR,
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

        if process.stdout is not None:
            for line in process.stdout:
                log_lines.append(line.rstrip("\n"))
                with log_area.container():
                    render_log(log_lines)

        process.wait()
        success = process.returncode == 0

        if success:
            status.update(label=f"{script_name} concluído", state="complete")
        else:
            status.update(
                label=f"{script_name} terminou com erro (código {process.returncode})",
                state="error",
            )

    st.cache_data.clear()
    return success


def run_full_refresh(token: str) -> None:
    """Atualiza repositórios e snapshot do board na ordem correta."""
    if run_script("extract_repositories.py", token):
        run_script("snapshot_board.py", token)


# ============================================================
# FUNÇÕES DE VISUALIZAÇÃO
# ============================================================

def styled_histogram(data: pd.DataFrame, x: str, title: str, nbins: int = 40):
    fig = px.histogram(data, x=x, nbins=nbins, title=title)
    fig.update_traces(marker_line_width=0.8)
    fig.update_layout(bargap=0.06)
    return fig


def safe_metric(series: pd.Series, operation: str = "median") -> float:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return float("nan")
    return float(clean.median() if operation == "median" else clean.mean())


def format_number(value: float, decimals: int = 0) -> str:
    if pd.isna(value):
        return "—"
    return f"{value:,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def latest_board_snapshot(board: pd.DataFrame) -> pd.DataFrame:
    if board.empty:
        return board

    result = board.copy()
    if "snapshot_date" in result.columns and result["snapshot_date"].notna().any():
        latest_date = result["snapshot_date"].max()
        result = result[result["snapshot_date"] == latest_date]
    return result


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("Lab01 — Controles")
st.sidebar.caption("Coleta, filtros e atualização dos dados")

token_input = os.environ.get("GITHUB_TOKEN", "")

with st.sidebar.expander("Atualizar dados", expanded=False):
    st.caption("O token é lido somente da variável de ambiente `GITHUB_TOKEN`.")

    if st.button("Atualizar tudo", use_container_width=True):
        if not token_input:
            st.error(
                "GITHUB_TOKEN não encontrado. Configure no terminal antes de abrir o dashboard."
            )
        else:
            run_full_refresh(token_input)
            st.rerun()

    if st.button("Somente repositórios", use_container_width=True):
        if not token_input:
            st.error("GITHUB_TOKEN não encontrado no ambiente.")
        elif run_script("extract_repositories.py", token_input):
            st.rerun()

    if st.button("Somente snapshot do board", use_container_width=True):
        if not token_input:
            st.error("GITHUB_TOKEN não encontrado no ambiente.")
        elif run_script("snapshot_board.py", token_input):
            st.rerun()

if st.sidebar.button("Recarregar arquivos locais", use_container_width=True):
    st.cache_data.clear()
    st.rerun()


# ============================================================
# CORPO PRINCIPAL
# ============================================================

st.title("Dashboard — Características de repositórios populares do GitHub")
st.caption("Laboratório de Experimentação de Software · análise das RQ01–RQ07 e acompanhamento do board")

df = get_dataframe()
board_df = get_board_dataframe()

if df is None:
    st.warning(
        "Nenhum dado de repositórios foi encontrado em `data/`. Rode `python main.py --refresh` "
        "ou use a atualização pela barra lateral."
    )
    st.stop()

numeric_columns = [
    "stars",
    "age_years",
    "accepted_pull_requests",
    "releases",
    "days_since_last_update",
    "closed_issues_percentage",
]
for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# Filtros globais
st.sidebar.markdown("### Filtros")
min_stars = int(df["stars"].min())
max_stars = int(df["stars"].max())
star_range = st.sidebar.slider(
    "Faixa de estrelas",
    min_stars,
    max_stars,
    (min_stars, max_stars),
)

languages = sorted(df["primary_language"].dropna().astype(str).unique().tolist())
selected_languages = st.sidebar.multiselect("Linguagem primária", languages, default=[])

max_position = int(df["position"].max()) if "position" in df.columns else len(df)
position_limit = st.sidebar.slider(
    "Top N repositórios",
    min_value=10,
    max_value=max_position,
    value=max_position,
    step=10 if max_position >= 100 else 1,
)

filtered = df[(df["stars"] >= star_range[0]) & (df["stars"] <= star_range[1])].copy()
if "position" in filtered.columns:
    filtered = filtered[filtered["position"] <= position_limit]
if selected_languages:
    filtered = filtered[filtered["primary_language"].isin(selected_languages)]

if filtered.empty:
    st.warning("Os filtros atuais não retornaram nenhum repositório.")
    st.stop()

# Cabeçalho de KPIs
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Repositórios", format_number(len(filtered)))
k2.metric("Mediana de estrelas", format_number(safe_metric(filtered["stars"])))
k3.metric("Idade mediana", f"{format_number(safe_metric(filtered['age_years']), 2)} anos")
k4.metric("PRs aceitas · mediana", format_number(safe_metric(filtered["accepted_pull_requests"])))
valid_languages = filtered["primary_language"].dropna()
top_language = valid_languages.mode().iloc[0] if not valid_languages.empty else "—"
k5.metric("Linguagem mais comum", top_language)

st.caption(f"{len(filtered)} de {len(df)} repositórios no recorte atual")

csv_bytes = filtered.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "Baixar recorte filtrado (.csv)",
    data=csv_bytes,
    file_name="repositorios_filtrados.csv",
    mime="text/csv",
)


tabs = st.tabs(
    [
        "Visão geral",
        "RQ01 — Idade",
        "RQ02 — PRs",
        "RQ03 — Releases",
        "RQ04 — Atualização",
        "RQ05 — Linguagem",
        "RQ06 — Issues",
        "RQ07 — Por linguagem",
        "Correlações",
        "Board / Sprint",
    ]
)

with tabs[0]:
    left, right = st.columns([1.45, 1])

    with left:
        st.subheader("Top 20 por estrelas")
        columns = [
            "position",
            "name_with_owner",
            "stars",
            "primary_language",
            "age_years",
            "accepted_pull_requests",
            "url",
        ]
        columns = [column for column in columns if column in filtered.columns]
        top20 = filtered.sort_values("stars", ascending=False).head(20)[columns]

        column_config = {}
        if "url" in top20.columns:
            column_config["url"] = st.column_config.LinkColumn("GitHub", display_text="Abrir")

        st.dataframe(
            top20,
            use_container_width=True,
            hide_index=True,
            column_config=column_config,
        )

    with right:
        st.subheader("Distribuição das linguagens")
        language_overview = (
            filtered["primary_language"]
            .fillna("Sem linguagem")
            .value_counts()
            .head(10)
            .rename_axis("linguagem")
            .reset_index(name="repositórios")
        )
        lang_fig = px.bar(
            language_overview,
            x="repositórios",
            y="linguagem",
            orientation="h",
            title="Top 10 linguagens primárias",
        )
        lang_fig.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(lang_fig, use_container_width=True)

    st.subheader("Resumo estatístico")
    summary_columns = [
        column
        for column in [
            "stars",
            "age_years",
            "accepted_pull_requests",
            "releases",
            "days_since_last_update",
            "closed_issues_percentage",
        ]
        if column in filtered.columns
    ]
    summary = filtered[summary_columns].describe().T
    summary = summary[["count", "mean", "50%", "min", "max"]].rename(
        columns={"count": "N", "mean": "Média", "50%": "Mediana", "min": "Mín.", "max": "Máx."}
    )
    st.dataframe(summary.round(2), use_container_width=True)

with tabs[1]:
    st.subheader("RQ01 — Sistemas populares são maduros/antigos?")
    col1, col2, col3 = st.columns(3)
    col1.metric("Idade mediana", f"{format_number(safe_metric(filtered['age_years']), 2)} anos")
    col2.metric("Idade média", f"{format_number(safe_metric(filtered['age_years'], 'mean'), 2)} anos")
    col3.metric("Mais de 10 anos", f"{(filtered['age_years'].ge(10).mean() * 100):.1f}%")
    st.plotly_chart(
        styled_histogram(filtered, "age_years", "Distribuição de idade (anos)"),
        use_container_width=True,
    )

with tabs[2]:
    st.subheader("RQ02 — Sistemas populares recebem muita contribuição externa?")
    col1, col2, col3 = st.columns(3)
    col1.metric("PRs aceitas · mediana", format_number(safe_metric(filtered["accepted_pull_requests"])))
    col2.metric("PRs aceitas · média", format_number(safe_metric(filtered["accepted_pull_requests"], "mean")))
    col3.metric("Repositórios sem PR aceita", format_number((filtered["accepted_pull_requests"] == 0).sum()))

    prs_log = filtered.assign(log_prs=np.log10(filtered["accepted_pull_requests"].fillna(0) + 1))
    prs_fig = px.histogram(
        prs_log,
        x="log_prs",
        nbins=40,
        title="Distribuição de PRs aceitas (escala logarítmica)",
    )
    prs_fig.update_layout(bargap=0.06)
    prs_fig.update_xaxes(
        tickvals=[0, 1, 2, 3, 4, 5],
        ticktext=["0", "10", "100", "1k", "10k", "100k"],
        title="PRs aceitas",
    )
    st.plotly_chart(prs_fig, use_container_width=True)
    st.info(
        "A escala logarítmica facilita a leitura porque a distribuição tem cauda longa: "
        "poucos projetos concentram volumes muito altos de pull requests aceitas."
    )

with tabs[3]:
    st.subheader("RQ03 — Sistemas populares lançam releases com frequência?")
    if "releases" in filtered.columns:
        col1, col2, col3 = st.columns(3)
        col1.metric("Releases · mediana", format_number(safe_metric(filtered["releases"])))
        col2.metric("Releases · média", format_number(safe_metric(filtered["releases"], "mean"), 2))
        col3.metric("Sem releases", f"{(filtered['releases'].eq(0).mean() * 100):.1f}%")
        st.plotly_chart(
            styled_histogram(filtered, "releases", "Distribuição de releases"),
            use_container_width=True,
        )
    else:
        st.info("Campo `releases` não encontrado no dataset atual.")

with tabs[4]:
    st.subheader("RQ04 — Sistemas populares são atualizados com frequência?")
    if "days_since_last_update" in filtered.columns:
        col1, col2 = st.columns(2)
        col1.metric(
            "Dias desde última atualização · mediana",
            format_number(safe_metric(filtered["days_since_last_update"])),
        )
        col2.metric(
            "Atualizados no mesmo dia",
            f"{(filtered['days_since_last_update'].le(0).mean() * 100):.1f}%",
        )
        st.plotly_chart(
            styled_histogram(
                filtered,
                "days_since_last_update",
                "Dias desde a última atualização",
            ),
            use_container_width=True,
        )
        st.warning(
            "Limitação metodológica: `updatedAt` também muda por atividades que não são push de código. "
            "Por isso a métrica pode se concentrar em zero; `pushedAt` seria mais específico para atividade de desenvolvimento."
        )
    else:
        st.info("Campo `days_since_last_update` não encontrado no dataset atual.")

with tabs[5]:
    st.subheader("RQ05 — Quais linguagens aparecem nos repositórios populares?")
    lang_counts = (
        filtered["primary_language"]
        .fillna("Sem linguagem")
        .value_counts()
        .reset_index()
    )
    lang_counts.columns = ["linguagem", "quantidade"]

    col1, col2, col3 = st.columns(3)
    col1.metric("Linguagens distintas", format_number(filtered["primary_language"].nunique()))
    col2.metric("Mais frequente", lang_counts.iloc[0]["linguagem"])
    col3.metric("Sem linguagem", format_number(filtered["primary_language"].isna().sum()))

    top15 = lang_counts.head(15)
    pie_fig = px.pie(
        top15,
        names="linguagem",
        values="quantidade",
        title="Top 15 linguagens primárias",
        hole=0.35,
    )
    st.plotly_chart(pie_fig, use_container_width=True)

with tabs[6]:
    st.subheader("RQ06 — Sistemas populares possuem alto percentual de issues fechadas?")
    if "closed_issues_percentage" in filtered.columns:
        valid_closed = filtered["closed_issues_percentage"].dropna()
        col1, col2, col3 = st.columns(3)
        col1.metric("Issues fechadas · mediana", f"{format_number(valid_closed.median(), 2)}%")
        col2.metric("Issues fechadas · média", f"{format_number(valid_closed.mean(), 2)}%")
        col3.metric("Sem issues", format_number(filtered["closed_issues_percentage"].isna().sum()))
        st.plotly_chart(
            styled_histogram(
                filtered.dropna(subset=["closed_issues_percentage"]),
                "closed_issues_percentage",
                "Distribuição do percentual de issues fechadas",
            ),
            use_container_width=True,
        )
    else:
        st.info("Campo `closed_issues_percentage` não encontrado no dataset atual.")

with tabs[7]:
    st.subheader("RQ07 — Contribuição, releases e atualização por linguagem")
    language_df = filtered.copy()
    language_df["primary_language"] = language_df["primary_language"].fillna("Sem linguagem")

    language_stats = (
        language_df.groupby("primary_language", as_index=False)
        .agg(
            repos=("name_with_owner", "count"),
            mediana_prs=("accepted_pull_requests", "median"),
            mediana_releases=("releases", "median"),
            mediana_dias_atualizacao=("days_since_last_update", "median"),
            mediana_stars=("stars", "median"),
        )
        .sort_values("repos", ascending=False)
    )

    min_repos = st.slider(
        "Mínimo de repositórios por linguagem",
        min_value=1,
        max_value=max(1, min(50, int(language_stats["repos"].max()))),
        value=min(10, max(1, int(language_stats["repos"].max()))),
        key="rq07_min_repos",
    )
    language_stats = language_stats[language_stats["repos"] >= min_repos]

    metric_choice = st.selectbox(
        "Métrica para comparar",
        ["mediana_prs", "mediana_releases", "mediana_stars", "mediana_dias_atualizacao"],
        format_func=lambda value: {
            "mediana_prs": "Mediana de PRs aceitas",
            "mediana_releases": "Mediana de releases",
            "mediana_stars": "Mediana de estrelas",
            "mediana_dias_atualizacao": "Mediana de dias sem atualização",
        }[value],
    )

    rq07_fig = px.bar(
        language_stats.sort_values(metric_choice, ascending=True),
        x=metric_choice,
        y="primary_language",
        orientation="h",
        hover_data=["repos"],
        title="Comparação entre linguagens",
        labels={"primary_language": "Linguagem", metric_choice: "Valor"},
    )
    st.plotly_chart(rq07_fig, use_container_width=True)
    st.dataframe(language_stats.round(2), use_container_width=True, hide_index=True)

with tabs[8]:
    st.subheader("Correlações entre métricas")
    correlation_columns = [
        column
        for column in [
            "stars",
            "age_years",
            "accepted_pull_requests",
            "releases",
            "days_since_last_update",
            "closed_issues_percentage",
        ]
        if column in filtered.columns
    ]
    corr = filtered[correlation_columns].corr(method="spearman")
    corr_fig = px.imshow(
        corr,
        text_auto=".2f",
        zmin=-1,
        zmax=1,
        title="Correlação de Spearman",
        aspect="auto",
    )
    st.plotly_chart(corr_fig, use_container_width=True)
    st.caption(
        "Spearman mede associação monotônica e é mais resistente a distribuições assimétricas e valores extremos "
        "do que a correlação linear de Pearson. Correlação não implica causalidade."
    )

with tabs[9]:
    st.subheader("Acompanhamento do GitHub Projects")

    if board_df.empty:
        st.info(
            "Nenhum `snapshot_board_*.csv` encontrado. Rode o snapshot para habilitar esta visão."
        )
    else:
        board_latest = latest_board_snapshot(board_df)

        sprint_name = (
            str(board_latest["sprint"].iloc[0])
            if "sprint" in board_latest.columns and not board_latest.empty
            else "—"
        )
        total_items = len(board_latest)
        done_mask = board_latest["status_column"].astype(str).str.lower().eq("done")
        closed_mask = board_latest["state"].astype(str).str.upper().eq("CLOSED")

        b1, b2, b3, b4 = st.columns(4)
        b1.metric("Sprint", sprint_name)
        b2.metric("Itens no snapshot", total_items)
        b3.metric("Em Done", f"{done_mask.mean() * 100:.1f}%" if total_items else "—")
        b4.metric("Issues/PRs fechadas", f"{closed_mask.mean() * 100:.1f}%" if total_items else "—")

        left, right = st.columns(2)
        with left:
            status_counts = (
                board_latest["status_column"]
                .fillna("SEM_STATUS")
                .value_counts()
                .rename_axis("status")
                .reset_index(name="itens")
            )
            st.plotly_chart(
                px.bar(status_counts, x="status", y="itens", title="Itens por status"),
                use_container_width=True,
            )

        with right:
            assignee_counts = (
                board_latest.assign(
                    assignee=board_latest["assignees"].fillna("SEM_ASSIGNEE").astype(str)
                )
                .assign(assignee=lambda data: data["assignee"].str.split(","))
                .explode("assignee")
                .assign(assignee=lambda data: data["assignee"].str.strip())
                ["assignee"]
                .value_counts()
                .rename_axis("responsável")
                .reset_index(name="itens")
            )
            st.plotly_chart(
                px.bar(
                    assignee_counts,
                    x="itens",
                    y="responsável",
                    orientation="h",
                    title="Distribuição de itens por responsável",
                ),
                use_container_width=True,
            )

        display_columns = [
            column
            for column in ["number", "title", "status_column", "state", "assignees", "repository"]
            if column in board_latest.columns
        ]
        st.dataframe(
            board_latest[display_columns].sort_values(
                ["status_column", "number"] if "number" in display_columns else ["status_column"]
            ),
            use_container_width=True,
            hide_index=True,
        )

        if "sprint" in board_df.columns and board_df["sprint"].nunique() > 1:
            st.subheader("Histórico por sprint")
            history = (
                board_df.assign(
                    done=board_df["status_column"].astype(str).str.lower().eq("done").astype(int)
                )
                .groupby("sprint", as_index=False)
                .agg(itens=("number", "count"), concluidos=("done", "sum"))
            )
            history["percentual_done"] = np.where(
                history["itens"] > 0,
                history["concluidos"] / history["itens"] * 100,
                0,
            )
            st.plotly_chart(
                px.bar(
                    history,
                    x="sprint",
                    y="percentual_done",
                    text_auto=".1f",
                    title="Percentual de itens em Done por sprint",
                    labels={"percentual_done": "% Done"},
                ),
                use_container_width=True,
            )
