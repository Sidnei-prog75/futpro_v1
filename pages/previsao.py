import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import datetime 
from datetime import date
import telebot

# ======================================================
# SIDEBAR – CONFIGURAÇÕES
# ======================================================
st.sidebar.title("Configurações")

TARGET = st.sidebar.selectbox(
    "Selecione o Mercado",
    [
        "Back_Home",
        "Back_Draw",
        "Back_Away"
    ]
)

COL_PROFIT = f"{TARGET}_Profit"

st.title("Previsão: "+ TARGET)

# Função drop reset index
@st.cache_data
def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

@st.cache_data
def converter_data(df):
    # df = df.copy
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.normalize()
    df = df.sort_values("Date")
    df = df.dropna()
    df = df.reset_index(drop=True)
    return df

@st.cache_data
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
@st.cache_data
def remover_duplicatas_drop_reset_index(df):
    df = df.drop_duplicates(
                 subset=["Date", "League", "Home", "Away"],
                 keep="last"
            )
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

# ===================================
# Configuração Inicial e criar pasta
PASTA_PREVISAO = "Previsões"
os.makedirs(PASTA_PREVISAO, exist_ok=True)
            
# Nome de arquivo de previsão
nome_previsao = f"{PASTA_PREVISAO}/{TARGET}_Previsão"
            
# --------------------------------------------------
# Salvar Previsões
# --------------------------------------------------
if not os.path.exists(nome_previsao + ".csv"):
    # Salvar previsão recente se previsão passada não existir
    # df_Entradas.to_csv(nome_previsao + ".csv", index=False)
    print(f"\nℹ️ Arquivo Não Existe: {nome_previsao}.csv")
    # print(f"\n✅ Previsão Salvo: {TARGET}_Previsão")
            
else:
    # Carregar previsão 
    previsao = pd.read_csv(f"{nome_previsao + '.csv'}")

# =====================================================
# =============== FILTRO DE DATA =======================
col1, col2 = st.columns(2)

with col1:
    data_min = st.date_input(
        "Data inicial",
        date.today()
    )

with col2:
    data_max = st.date_input(
        "Data final",
        date.today()
    )

# 🧼 VERSÃO MAIS LIMPA (MINHA FAVORITA)
# # 🔹 Garanta que a coluna é datetime
# previsao["Date"] = pd.to_datetime(previsao["Date"])
previsao = converter_data(previsao)

data_min = pd.to_datetime(data_min)
data_max = pd.to_datetime(data_max)

previsao = previsao[
    (previsao["Date"] >= data_min) &
    (previsao["Date"] <= data_max)
]

# ================ FILTRO DE LIGAS E ODDS ==========================
# ----------------------- Roda bem ------------------------------------

# ✅ 2️⃣ FUNÇÕES PARA CARREGAR / SALVAR
import json
import os

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
st.sidebar.header("⚙️ Preferências do Usuário")

prefs = carregar_preferencias()

pref_mercado = prefs.get(TARGET, {})

# ---------- LIGAS ----------
ligas_disponiveis = sorted(previsao["League"].unique().tolist())

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
df_filtrado = previsao.copy()

# filtro de ligas
if ligas_selecionadas:
    df_filtrado = df_filtrado[df_filtrado["League"].isin(ligas_selecionadas)]

# filtro de odds
df_filtrado = df_filtrado[
    (df_filtrado["Odd_Entrada"] >= odd_min) &
    (df_filtrado["Odd_Entrada"] <= odd_max)
]
previsao = df_filtrado

previsao =drop_reset_index(previsao)
st.dataframe(previsao)
# ===================================================





# ============================================================================
# ============== FILTRO DE ENTRADAS PARA TELEGRAM ======================
# ✅ 1️⃣ Filtro de partidas por Home x Away (multiselect)
# Cria uma coluna auxiliar de partida:
df=previsao
df["Partida"] = df["League"] + " -- " + df["Home"] + " -x- " + df["Away"]

partidas = sorted(df["Partida"].unique())

partidas_sel = st.multiselect(
    "Selecione as partidas",
    options=partidas,
    # default=partidas
)

df = df[df["Partida"].isin(partidas_sel)]
df = drop_reset_index(df)
st.dataframe(df)


# --------------------------------------------------------------------

# ==================== ENVIAR ENTRADAS PARA TELEGRAM ====================
df_telegram = df
# ✅ FUNÇÃO COMPLETA PARA ENVIAR TUDO EM UMA MENSAGEM
# import telebot
# import os
@st.cache_data
def enviar_entradas_tabela_telegram(df, mercado):
    if df.empty:
        return "Nenhuma entrada para enviar."

    bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_channel = os.getenv("TELEGRAM_CHAT_ID")

    # Data do dia (primeira linha do df)
    data_str = df["Date"].iloc[0].strftime("%d/%m/%Y")

    # Cabeçalho
    mensagem = f"📊 *{mercado.upper()}* | {data_str}\n\n"
    mensagem += "*Hora | Jogo | Odd*\n"
    mensagem += "---------------------------------------\n"

    # Linhas da tabela
    for _, row in df.iterrows():
        hora = row["Time"]
        jogo = f"{row['Home']} x {row['Away']}"
        odd = round(row["Odd_Entrada"], 2)

        mensagem += f"{hora} | {jogo} | {odd}\n"

    # Enviar mensagem
    bot.send_message(
        chat_channel,
        mensagem,
        parse_mode="Markdown"
    )

    return "Entradas enviadas com sucesso!"
# ▶️ COMO USAR NO STREAMLIT (COM BOTÃO)
import streamlit as st

if st.button("📤 Enviar Entradas para Telegram"):
    status = enviar_entradas_tabela_telegram(df_telegram, TARGET)
    st.success(status)
# 🔐 VARIÁVEIS DE AMBIENTE (OBRIGATÓRIO)
# .env ou configurações do Streamlit Cloud
# TELEGRAM_BOT_TOKEN=SEU_TOKEN_AQUI
# TELEGRAM_CHAT_ID=-100XXXXXXXXXX
# 🎨 MELHORIAS VISUAIS (OPCIONAL)
# 🔹 Alinhar melhor a tabela (monoespaçado)
# Troque parse_mode="Markdown" por:

# bot.send_message(chat_channel, f"```{mensagem}```")
# Isso deixa tudo alinhado perfeitamente no Telegram.
