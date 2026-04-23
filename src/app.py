import sys
from pathlib import Path

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent

if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from preprocess import carregar_base
from metrics import tratar_followups

st.set_page_config(
    page_title="Smart Follow-Up Manager",
    page_icon="📊",
    layout="wide"
)


st.markdown(
    """
    <style>
    .main {
        background-color: #f8fafc;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .kpi-card {
        background-color: white;
        padding: 18px 20px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    }
    .kpi-title {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 8px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #111827;
    }
    .section-title {
        font-size: 20px;
        font-weight: 700;
        color: #111827;
        margin-top: 10px;
        margin-bottom: 10px;
    }
    .subtle-text {
        color: #6b7280;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

@st.cache_data
def carregar_dados():
    caminho_csv = ROOT_DIR / "data" / "followups.csv"
    df = carregar_base(caminho_csv)
    df = tratar_followups(df)
    return df


df = carregar_dados()

st.sidebar.title("Filtros")

compradores = ["Todos"] + sorted(df["comprador"].unique().tolist())
fornecedores = ["Todos"] + sorted(df["fornecedor"].unique().tolist())
prioridades = ["Todas"] + sorted(df["prioridade"].unique().tolist())
status_lista = ["Todos"] + sorted(df["status"].unique().tolist())

comprador_sel = st.sidebar.selectbox("Comprador", compradores)
fornecedor_sel = st.sidebar.selectbox("Fornecedor", fornecedores)
prioridade_sel = st.sidebar.selectbox("Prioridade", prioridades)
status_sel = st.sidebar.selectbox("Status", status_lista)

df_filtrado = df.copy()

if comprador_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["comprador"] == comprador_sel]

if fornecedor_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["fornecedor"] == fornecedor_sel]

if prioridade_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["prioridade"] == prioridade_sel]

if status_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["status"] == status_sel]


st.markdown('<div class="section-title">Smart Follow-Up Manager</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtle-text">Dashboard executivo de pendências, atrasos e prioridades operacionais</div>',
    unsafe_allow_html=True
)

st.divider()


total_pendencias = len(df_filtrado)
prioridade_alta = (df_filtrado["prioridade"] == "Alta").sum()
atrasados = (df_filtrado["dias_atraso"] > 0).sum()
valor_total = df_filtrado["valor"].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Pendências Totais</div>
            <div class="kpi-value">{total_pendencias}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Prioridade Alta</div>
            <div class="kpi-value" style="color:#dc2626;">{prioridade_alta}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Pedidos Atrasados</div>
            <div class="kpi-value" style="color:#d97706;">{atrasados}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

with col4:
    valor_formatado = f"R$ {valor_total:,.0f}".replace(",", ".")
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">Valor Total</div>
            <div class="kpi-value" style="color:#2563eb;">{valor_formatado}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")
st.write("")


col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("### Aging de Atraso")

    aging = (
        df_filtrado.groupby("faixa_atraso", as_index=False)
        .size()
        .rename(columns={"size": "quantidade"})
    )

    ordem_aging = ["No prazo", "1 a 5 dias", "6 a 10 dias", "11 a 15 dias", "Acima de 15 dias"]
    aging["faixa_atraso"] = pd.Categorical(aging["faixa_atraso"], categories=ordem_aging, ordered=True)
    aging = aging.sort_values("faixa_atraso")

    fig1, ax1 = plt.subplots(figsize=(7, 4))
    barras = ax1.bar(
        aging["faixa_atraso"].astype(str),
        aging["quantidade"],
        color="#2563eb"
    )
    ax1.set_xlabel("Faixa de atraso")
    ax1.set_ylabel("Quantidade")
    ax1.tick_params(axis="x", rotation=25)
    ax1.grid(axis="y", alpha=0.2)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.bar_label(barras, padding=3)
    plt.tight_layout()
    st.pyplot(fig1)

with col_graf2:
    st.markdown("### Top Compradores com Pendências")

    top_compradores = (
        df_filtrado.groupby("comprador", as_index=False)
        .size()
        .rename(columns={"size": "quantidade"})
        .sort_values("quantidade", ascending=False)
        .head(5)
    )

    fig2, ax2 = plt.subplots(figsize=(7, 4))
    barras = ax2.barh(
        top_compradores["comprador"],
        top_compradores["quantidade"],
        color="#f59e0b"
    )
    ax2.invert_yaxis()
    ax2.set_xlabel("Quantidade")
    ax2.set_ylabel("")
    ax2.grid(axis="x", alpha=0.2)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.bar_label(barras, padding=3)
    plt.tight_layout()
    st.pyplot(fig2)


st.markdown("### Top Fornecedores com Pendências")

top_fornecedores = (
    df_filtrado.groupby("fornecedor", as_index=False)
    .size()
    .rename(columns={"size": "quantidade"})
    .sort_values("quantidade", ascending=False)
    .head(5)
)

fig3, ax3 = plt.subplots(figsize=(10, 4))
barras = ax3.bar(
    top_fornecedores["fornecedor"],
    top_fornecedores["quantidade"],
    color="#0f766e"
)
ax3.set_xlabel("Fornecedor")
ax3.set_ylabel("Quantidade")
ax3.tick_params(axis="x", rotation=20)
ax3.grid(axis="y", alpha=0.2)
ax3.spines["top"].set_visible(False)
ax3.spines["right"].set_visible(False)
ax3.bar_label(barras, padding=3)
plt.tight_layout()
st.pyplot(fig3)


st.markdown("### Pendências Priorizadas")

colunas_exibir = [
    "pedido",
    "fornecedor",
    "comprador",
    "data_prevista",
    "dias_atraso",
    "valor",
    "status",
    "criticidade",
    "score_urgencia",
    "prioridade",
    "faixa_atraso",
]

df_tabela = df_filtrado[colunas_exibir].copy()
df_tabela["data_prevista"] = pd.to_datetime(df_tabela["data_prevista"]).dt.strftime("%d/%m/%Y")
df_tabela["valor"] = df_tabela["valor"].map(
    lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

def destacar_prioridade(valor):
    if valor == "Alta":
        return "background-color: #fee2e2; color: #b91c1c; font-weight: bold;"
    if valor == "Média":
        return "background-color: #fef3c7; color: #b45309; font-weight: bold;"
    return "background-color: #dcfce7; color: #166534; font-weight: bold;"

st.dataframe(
    df_tabela.style.map(destacar_prioridade, subset=["prioridade"]),
    use_container_width=True
)


csv_download = df_filtrado.to_csv(index=False).encode("utf-8-sig")

st.download_button(
    label="Baixar CSV tratado",
    data=csv_download,
    file_name="followup_priorizado.csv",
    mime="text/csv"
)

st.divider()
st.caption("Projeto analítico de portfólio | Follow-up | Compras | Python + Dados")
