import streamlit as st
import pandas as pd
import numpy as np
import os
import json
import datetime 
import telebot
from datetime import date
from io import BytesIO
from xlsxwriter import Workbook    

# ======================================================
# SIDEBAR – CONFIGURAÇÕES
# ======================================================
st.sidebar.title("⚙️ Configurações")

TARGET = st.sidebar.selectbox(
    "Selecione o Mercado",
    [
        "Back_Home",
        "Back_Draw",
        "Back_Away"
    ]
)

COL_PROFIT = f"{TARGET}_Profit"

st.title("Historico e Resultado: "+ TARGET)
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

# 🔢 Garantir coluna como int
def garantir_int(df, col):
    if col not in df.columns:
        raise ValueError(f"Coluna '{col}' não existe no DataFrame")

    df[col] = (
        pd.to_numeric(df[col], errors="coerce")
        .fillna(0)
        .astype(int)
    )
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
st.sidebar.header("⚙️ Preferências do Usuário")

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

df_display = df
# ==============================================================
# =============== CRIAR COLUNA PLACAR =======================
df_display = garantir_int(df_display,"Goals_H_FT")
df_display = garantir_int(df_display,"Goals_A_FT")
df_display["Placar"] = (df_display["Goals_H_FT"].astype(str) + " - " + df_display["Goals_A_FT"].astype(str))
df_csv = df_display

df_display["Res"] = df_display[f"{COL_PROFIT}"].apply(
    lambda x: "🟢" if x > 0 else "🔴"
)

df_display=drop_reset_index(df_display)
st.dataframe(df_display)
# =================================================================
# ==================== BAIXAR ARQUIVO CSV E EXCEL ==================
# ============ Roda bem ===================
# ✅ 2️⃣ DOWNLOAD EM CSV (BOTÃO)
# csv = df_csv.to_csv(index=False).encode("utf-8")

# st.download_button(
#     label="⬇️ Baixar CSV",
#     data=csv,
#     file_name=f"{TARGET}_previsoes.csv",
#     mime="text/csv"
# )
# ==========================================

# # ✅ 4️⃣ VERSÃO FINAL (RECOMENDADA – TUDO JUNTO)
# st.subheader("📥 Download dos Resultados")

col1, col2 = st.columns(2)

with col1:
    csv = resultado.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ CSV",
        csv,
        "previsoes.csv",
        "text/csv"
    )

with col2:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        resultado.to_excel(writer, index=False, sheet_name="Previsoes")

    st.download_button(
        "⬇️ Excel",
        output.getvalue(),
        "previsoes.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
# ===============================================



# ===================================



# ============== FILTRO DE RESULTADOS PARA TELEGRAM ======================
# ✅ 1️⃣ Filtro de partidas por Home x Away (multiselect)
# Cria uma coluna auxiliar de partida:
df=resultado
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
        

# ===================== ENVIAR RESULTADO PARA TELEGRAM =======================

df_telegram = df
# 🧠 FUNÇÃO FINAL
# import telebot
# import os

def enviar_resultados_telegram(df, mercado):
    if df.empty:
        return "Nenhum resultado para enviar."

    bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_TOKEN"))
    chat_channel = os.getenv("TELEGRAM_CHAT_ID")

    data_str = df["Date"].iloc[0].strftime("%d/%m/%Y")

    # Métricas
    entradas = len(df)
    green = (df[f"{COL_PROFIT}"] > 0).sum()
    red = (df[f"{COL_PROFIT}"] < 0).sum()
    lucro = round(df[f"{COL_PROFIT}"].sum(), 2)
    roi = round((lucro / entradas) * 100, 2) if entradas > 0 else 0

    # Cabeçalho
    mensagem = f"📊 *RESULTADOS | {mercado.upper()}* | {data_str}\n\n"
    mensagem += "*Hora | Jogo | Odd | Res | Profit*\n"
    mensagem += "--------------------------------------------------\n"

    # Tabela
    for _, row in df.iterrows():
        hora = row["Time"]
        jogo = f"{row['Home']} x {row['Away']}"
        odd = round(row["Odd_Entrada"], 2)
        profit = round(row[f"{COL_PROFIT}"], 2)

        res = "🟢" if profit > 0 else "🔴"

        mensagem += f"{hora} | {jogo} | {odd} | {res} | {profit:+.2f}\n"

    # Resumo
    mensagem += "\n📈 *Resumo:*\n"
    mensagem += f"Entradas: {entradas}\n"
    mensagem += f"Green: {green}\n"
    mensagem += f"Red: {red}\n"
    mensagem += f"Lucro: {lucro:+.2f}\n"
    mensagem += f"ROI: {roi:+.2f}%\n"

    # Enviar
    bot.send_message(chat_channel, mensagem, parse_mode="Markdown")

    return "Resultados enviados com sucesso!"
# ▶️ USO NO STREAMLIT (BOTÃO)
# import streamlit as st

if st.button("📤 Enviar Resultados para Telegram"):
    status = enviar_resultados_telegram(df_telegram, TARGET)
    st.success(status)
# 🎨 MELHORIA VISUAL (OPCIONAL – TABELA ALINHADA)
# Se quiser tudo perfeitamente alinhado, troque o envio por:

# bot.send_message(chat_channel, f"```{mensagem}```")
# (sem parse_mode="Markdown")

# 🔐 RELEMBRANDO (IMPORTANTE)
# Nunca coloque token no código 👇

# TELEGRAM_BOT_TOKEN=seu_token
# TELEGRAM_CHAT_ID=-100xxxxxxxxxx
# 🧠 VANTAGENS DESSE MODELO
# ✅ Uma única mensagem
# ✅ Sem spam
# ✅ Visual limpo no celular
# ✅ Fácil leitura
# ✅ Ideal para canais/grupos
