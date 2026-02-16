import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import datetime 
from datetime import date




# ======================================================
# SIDEBAR – CONFIGURAÇÕES
# ======================================================
# st.sidebar.title("⚙️ Configurações")

TARGET = st.sidebar.selectbox(
    "Selecione o Mercado",
    [
        "Back_Home",
        "Back_Draw",
        "Back_Away"
    ]
)

COL_PROFIT = f"{TARGET}_Profit"


st.title("Ranking: "+ TARGET)
# =================== FUNÇÕES===================================================
# Função drop reset index
@st.cache_data
def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

def converter_data(df):
    # df = df.copy
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    df = df.sort_values("Date")
    df = df.dropna()
    df = df.reset_index(drop=True)
    return df

def garantir_schema(df, schema):
    for col, tipo in schema.items():
        if col not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente: {col}")

        if tipo == "float":
            df[col] = pd.to_numeric(df[col], errors="coerce")

        elif tipo == "int":
            df[col] = (
                pd.to_numeric(df[col], errors="coerce")
                .fillna(0)
                .astype(int)
            )

        elif tipo == "datetime":
            df[col] = pd.to_datetime(df[col], errors="coerce")

        elif tipo == "str":
            df[col] = df[col].astype(str).str.strip()

    return df

# Função remover duplicatas
def remover_duplicatas_drop_reset_index(df):
    df = df.drop_duplicates(
                 subset=["Date", "League", "Home", "Away"],
                 keep="last"
            )
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df


# Configuração Inicial e criar pasta de resultados
PASTA_PREVISAO_RESUL = "Resultados"
os.makedirs(PASTA_PREVISAO_RESUL, exist_ok=True)

# Nome de arquivo de historico de resultado
nome_resultado = f"{PASTA_PREVISAO_RESUL}/{TARGET}_Resultado_Previsão"
# --------------------------------------------------
if not os.path.exists(nome_resultado + ".csv"):
            
    # df_Entradas.to_csv(nome_modelo + ".csv", index=False)
    print(f"\nℹ️ Arquivo Não Existe: {nome_resultado}.csv")
    # print(f"\n✅ Previsão Salvo: {TARGET}_Previsão")
            
else:
    # Carregar dados da previsão passada, do resultado passado e da base de dados
    resultado = pd.read_csv(f"{nome_resultado + '.csv'}")
    resultado = converter_data(resultado)

# =============== FILTRO DE DATA =======================
col1, col2 = st.columns(2)

with col1:
    data_min = st.date_input(
        "Data inicial",
        value=(resultado["Date"].min().date()
        ))

with col2:
    data_max = st.date_input(
        "Data final",
        value=(resultado["Date"].max().date()
        ))

# 🧼 VERSÃO MAIS LIMPA (MINHA FAVORITA)
# # 🔹 Garanta que a coluna é datetime
# previsao["Date"] = pd.to_datetime(previsao["Date"])
resultado = converter_data(resultado)

data_min = pd.to_datetime(data_min)
data_max = pd.to_datetime(data_max)

resultado = resultado[
    (resultado["Date"] >= data_min) &
    (resultado["Date"] <= data_max)
]

# ================ FILTRO DE LIGAS E ODDS ==========================
# ----------------------- Roda bem ------------------------------------

# ✅ 2️⃣ FUNÇÕES PARA CARREGAR / SALVAR

ARQ_PREF = "preferencias.json"

@st.cache_data
def carregar_preferencias():
    if os.path.exists(ARQ_PREF):
        with open(ARQ_PREF, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def salvar_preferencias(prefs):
    with open(ARQ_PREF, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=4, ensure_ascii=False)
# ✅ 3️⃣ INTERFACE STREAMLIT (ODDS + LIGAS)
# 🔹 Sidebar
# st.sidebar.header("⚙️ Preferências do Usuário")

prefs = carregar_preferencias()

pref_mercado = prefs.get(TARGET, {})

# ---------- LIGAS ----------
ligas_disponiveis = sorted(resultado["League"].unique().tolist())

ligas_selecionadas = st.sidebar.multiselect(
    "Ligas",
    ligas_disponiveis,
    default=pref_mercado.get("ligas", [])
    
)

# ---------- ODDS ----------
odd_min = pref_mercado.get("odd_min", 1.20)
odd_max = pref_mercado.get("odd_max", 3.00)

odd_min, odd_max = st.sidebar.slider(
    f"Odds – {TARGET}",
    1.01, 10.0,
    value=(odd_min, odd_max),
    step=0.01
)

# ✅ 4️⃣ BOTÃO SALVAR PREFERÊNCIAS
if st.sidebar.button("💾 Salvar Preferências"):
    prefs[TARGET] = {
        "odd_min": odd_min,
        "odd_max": odd_max,
        "ligas": ligas_selecionadas
    }
    salvar_preferencias(prefs)
    st.sidebar.success("Preferências salvas com sucesso ✅")
# ✅ 5️⃣ APLICAR FILTROS NO DATAFRAME
df_filtrado = resultado.copy()

# filtro de ligas
if ligas_selecionadas:
    df_filtrado = df_filtrado[df_filtrado["League"].isin(ligas_selecionadas)]


# filtro de odds
df_filtrado = df_filtrado[
    (df_filtrado["Odd_Entrada"] >= odd_min) &
    (df_filtrado["Odd_Entrada"] <= odd_max)
]
resultado = df_filtrado

# =======================================================
# CALCULO DE TOTAL
total_entradas = len(resultado)
total_green = (resultado[COL_PROFIT] > 0).sum()
total_red = (resultado[COL_PROFIT] < 0).sum()
lucro_total = resultado[COL_PROFIT].sum()
roi = (lucro_total / total_entradas * 100) if total_entradas > 0 else 0
assertividade = (total_green / total_entradas * 100) if total_entradas else 0

# col1, col2, col3, col4, col5, col6 = st.columns(6)

# col1.metric("🎯 Entradas", total_entradas)
# col2.metric("🟢 Greens", total_green)
# col3.metric("🔴 Reds", total_red)
# col4.metric("💰 Lucro", f"{lucro_total:.2f}")
# col5.metric("📈 ROI (%)", f"{roi:.2f}")
# col6.metric("📊 Acer (%)", f"{assertividade:.2f}")

df = resultado
# ✅ 1️⃣ FUNÇÃO PARA COLORIR VALORES
def cor_valor(valor):
    if valor > 0:
        return "green"
    elif valor < 0:
        return "red"
    else:
        return "gray"
# ✅ 2️⃣ KPIs COLORIDOS (LUCRO / ROI)
total_entradas = len(df)
total_green = (df[COL_PROFIT] > 0).sum()
total_red = (df[COL_PROFIT] < 0).sum()

lucro_total = df[COL_PROFIT].sum()
roi = (lucro_total / total_entradas * 100) if total_entradas > 0 else 0

cor_lucro = cor_valor(lucro_total)
cor_roi = cor_valor(roi)
col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Entradas", total_entradas)

col2.markdown(
    f"<h4 style='color:green;'>Greens<br>{total_green}</h4>",
    unsafe_allow_html=True
)

col3.markdown(
    f"<h4 style='color:red;'>Reds<br>{total_red}</h4>",
    unsafe_allow_html=True
)

col4.markdown(
    f"<h4 style='color:{cor_lucro};'>Lucro<br>{lucro_total:.2f}</h4>",
    unsafe_allow_html=True
)

col5.markdown(
    f"<h4 style='color:{cor_roi};'>ROI (%)<br>{roi:.2f}%</h4>",
    unsafe_allow_html=True
)

col6.metric("Acer (%)", f"{assertividade:.2f}")

resultado = df

# st.subheader("Ranking de Ligas")

# st.dataframe(resultado)


#=================== CÓDIGO SIMPLES PARA RANKING POR LIGA=================
df=resultado
ranking_liga = (
    df
    .groupby("League")
    .agg(
        Lucro=(COL_PROFIT, "sum"),
        Entradas=(TARGET, "count"),
        Green=(TARGET, "sum")
    )
    .reset_index()
)

# calcular red
ranking_liga["Red"] = ranking_liga["Entradas"] - ranking_liga["Green"]

# calcular assertividade (%)
ranking_liga["Acerto"] = (
    ranking_liga["Green"] / ranking_liga["Entradas"] * 100
).round(2)

ranking_liga['ROI'] = (ranking_liga['Lucro'] / ranking_liga['Entradas'] * 100).round(2)

# 📊 Ordenar ranking (opcional, mas recomendado)
# Por lucro (mais usado)
# Por assertividade
ranking_liga = ranking_liga.sort_values("Lucro", ascending=False)
ranking_liga = drop_reset_index(ranking_liga)
# st.dataframe(ranking_liga)

# ======================== RANKING DE ODD ===================================
# 🔹 Ranking de Odds (simples e fácil)
df_rank = df.copy()

# --------------------------------------------------
# Criar faixas de odds (bins)
# # --------------------------------------------------
# bins = [1.00, 1.50, 2.00, 2.50, 3.00, 4.00, 100]
# labels = ['1.00-1.49', '1.50-1.99', '2.00-2.49', 
#           '2.50-2.99', '3.00-3.99', '4.00+']

bins = [1.00, 1.10, 1.20, 1.30, 1.40, 1.50, 1.60, 1.70, 1.80, 1.90, 2.00, 2.10, 2.20, 2.30, 2.40, 2.50,
        2.60, 2.70, 2.80, 2.90, 3.00, 3.10, 3.20, 3.30, 3.40, 3.50, 3.60, 3.70, 3.80, 3.90, 4.00, 100]
labels = ['1.00-1.09', '1.10-1.19', '1.20-1.29', '1.30-1.39', '1.40-1.49', '1.50-1.59', '1.60-1.69',
          '1.70-1.79', '1.80-1.89', '1.90-1.99', '2.00-2.09', '2.10-2.19', '2.20-2.29', '2.30-2.39',
          '2.40-2.49', '2.50-2.59', '2.60-2.69', '2.70-2.79', '2.80-2.89', '2.90-2.99', '3.00-3.09',
          '3.10-3.19', '3.20-3.29', '3.30-3.39', '3.40-3.49', '3.50-3.59', '3.60-3.69', '3.70-3.79',
          '3.80-3.89', '3.90-3.99', '4.00+']

df_rank['Faixa_Odd'] = pd.cut(
    df_rank['Odd_Entrada'],
    bins=bins,
    labels=labels,
    right=False
)

# --------------------------------------------------
# Filtrar apenas entradas
# --------------------------------------------------
df_rank = df_rank[df_rank[f'{TARGET}'] == 1]

# --------------------------------------------------
# Criar ranking
# --------------------------------------------------
ranking_odds = (
    df_rank
    .groupby('Faixa_Odd')
    .agg(
        Entradas=(f'{TARGET}', 'count'),
        Green=(f'{COL_PROFIT}', lambda x: (x > 0).sum()),
        Red=(f'{COL_PROFIT}', lambda x: (x <= 0).sum()),
        Lucro=(f'{COL_PROFIT}', 'sum')
    )
    .reset_index()
)

# --------------------------------------------------
# Métricas
# --------------------------------------------------
ranking_odds['Acerto'] = (ranking_odds['Green'] / ranking_odds['Entradas']) * 100
ranking_odds['ROI'] = (ranking_odds['Lucro'] / ranking_odds['Entradas']) * 100

# --------------------------------------------------
# Ordenar pelo melhor ROI
# --------------------------------------------------
ranking_odds = ranking_odds.sort_values('Lucro', ascending=False)
ranking_odds = drop_reset_index(ranking_odds)
# -------------------------------------------------------------
# ✅ 3️⃣ DATAFRAMES COM LARGURA DIFERENTE (PROFISSIONAL 🔥)
col1, col2 = st.columns([2, 1])  # esquerda maior

with col1:
    st.subheader("Ranking de Liga")
    st.dataframe(ranking_liga, use_container_width=True)

with col2:
    st.subheader("Ranking de Odds")
    st.dataframe(ranking_odds)

# st.dataframe(ranking_odds)

# ===========================================================================
# ======================= GRAFICOS ================================

# ✅ 1️⃣ Gráfico interativo de lucro acumulado
# 📌 Requisitos
# pip install plotly
# 📊 Código
import plotly.express as px

@st.cache_data
def grafico_lucro_acumulado(df):
    df = df.copy()
    df["Profit_acu"] = df[COL_PROFIT].cumsum()

    fig = px.line(
        df,
        x=df.index,
        y="Profit_acu",
        title="📈 Lucro Acumulado",
        labels={
            "index": "Entradas",
            "Profit_acu": "Lucro (Stakes)"
        },
        markers=True
    )

    fig.update_layout(
        hovermode="x unified",
        # template="plotly_dark"
    )

    return fig
# 👉 Usando no Streamlit
# st.plotly_chart(grafico_lucro_acumulado(resultado), use_container_width=True)
# ------------

# ✅ 3️⃣ Gráfico interativo de volume de apostas por dia
@st.cache_data
def grafico_volume_apostas(df):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    volume = df.groupby("Date").size().reset_index(name="Apostas")

    fig = px.bar(
        volume,
        x="Date",
        y="Apostas",
        title="📊 Volume de Apostas por Dia",
        text="Apostas"
    )

    fig.update_layout(
        # template="plotly_dark",
        hovermode="x"
    )

    return fig
# st.plotly_chart(grafico_volume_apostas(resultado), use_container_width=True)

# -------------------------------------------------------

# ✅ 2️⃣ Gráfico interativo de lucro por dia
@st.cache_data
def grafico_lucro_por_dia(df):
    df = df.copy()
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    lucro_dia = df.groupby("Date")[f"{COL_PROFIT}"].sum().reset_index()

    fig = px.bar(
        lucro_dia,
        x="Date",
        y=f"{COL_PROFIT}",
        title="📊 Lucro por Dia",
        text_auto=True
    )

    fig.update_layout(
        template="plotly_dark",
        hovermode="x"
    )

    return fig
# st.plotly_chart(grafico_lucro_por_dia(resultado), use_container_width=True)

# -----------------------------------------------------------------
# ✅ 4️⃣ Gráficos lado a lado (Streamlit)
col1, col2, col3 = st.columns(3)

with col1:
    st.plotly_chart(grafico_lucro_acumulado(resultado), use_container_width=True)

with col2:

    st.plotly_chart(grafico_volume_apostas(resultado), use_container_width=True)

with col3:
    
    st.plotly_chart(grafico_lucro_por_dia(resultado), use_container_width=True)