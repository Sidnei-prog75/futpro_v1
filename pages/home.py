import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import date, timedelta
from pycaret.classification import load_model, predict_model

st.title("Pagina Inicial")

# ======================================================================
# CODIGO WEB SCRAPING E CRIAÇÃO DE VARIAVEIS
# ======================================================================
#=========================== IMPORTAR BASE DE DADOS E JOGOS FUTUROS  =============
# função para renomeação de ligas

def rename_leagues(df):

    df = df.copy()
    mapping = {
        'E0':'ENGLAND 1',
        'E1':'ENGLAND 2',
        'E2':'ENGLAND 3',
        'E3':'ENGLAND 4',
        'SC0':'ESCOCIA 1',
        'SC1':'ESCOCIA 2',
        'SC2':'ESCOCIA 3',
        'D1':'ALEMANHA 1',
        'D2':'ALEMANHA 2',
        'I1':'ITALIA 1',
        'I2':'ITALIA 2',
        'SP1':'ESPANHA 1',
        'SP2':'ESPANHA 2',
        'F1':'FRANÇA 1',
        'F2':'FRANÇA 2',
        'N1':'HOLANDA 1',
        'B1':'BELGICA 1',
        'P':'PORTUGAL 1',
        'T1':'TURQUIA 1',
        'G1':'GRECIA 1'
    }

    df['League'] = df['League'].replace(mapping)
    return df

# =========================
# Importar base de dados

import pandas as pd
import requests
from io import StringIO
from datetime import datetime

# =====================================
# CONFIGURAÇÃO
# =====================================

# lista de ligas
ligas = [
    'E0','E1','E2','E3','SC0','SC1','SC2',
    'D1','D2','I1','I2','SP1','SP2',
    'F1','F2','N1','B1','P','T1','G1'
]

# quantidade de temporadas desejadas
quantidade_temporadas = 3

base_url = "https://www.football-data.co.uk/mmz4281"

# =====================================
# GERAR TEMPORADAS AUTOMATICAMENTE
# =====================================

ano_atual = datetime.now().year
ano_inicial = ano_atual - quantidade_temporadas

temporadas = []

for ano in range(ano_inicial, ano_atual):
    temporada = f"{str(ano)[-2:]}{str(ano+1)[-2:]}"
    temporadas.append(temporada)

print("Temporadas geradas:", temporadas)

# =====================================
# WEB SCRAPING
# =====================================

lista_dfs = []

for liga in ligas:
    for temporada in temporadas:
        url = f"{base_url}/{temporada}/{liga}.csv"

        try:
            resposta = requests.get(url, timeout=20)

            # ignora temporada inexistente
            if resposta.status_code != 200:
                print(f"Não existe → {liga} {temporada}")
                continue

            print(f"Baixando → {liga} {temporada}")

            df = pd.read_csv(StringIO(resposta.text))
            df["Temporada"] = temporada
            df["Liga"] = liga

            lista_dfs.append(df)

        except Exception as erro:
            print(f"Erro {liga} {temporada}: {erro}")

# =====================================
# CONCATENAR E SALVAR
# =====================================

if lista_dfs:
    df_final = pd.concat(lista_dfs, ignore_index=True)
    #df_final.to_csv("dados_football_data.csv", index=False)
    print("Shape final:", df_final.shape)
else:
    print("Nenhum dado encontrado")


# =============

df = df_final.copy()

priority = {
    'H': ['PSH', 'B365H', 'BWH', 'AvgH', 'IWH', 'WHH', 'VCH', 'MaxH', 'MinH'],
    'D': ['PSD', 'B365D', 'BWD', 'AvgD', 'IWD', 'WHD', 'VCD', 'MaxD', 'MinD'],
    'A': ['PSA', 'B365A', 'BWA', 'AvgA', 'IWA', 'WHA', 'VCA', 'MaxA', 'MinA']
}

# função para pegar apenas colunas existentes
def cols_existentes(cols):
    return [c for c in cols if c in df.columns]

# converter odds existentes
odds_cols = [c for cols in priority.values() for c in cols if c in df.columns]

df[odds_cols] = (
    df[odds_cols]
    .replace(',', '.', regex=True)
    .apply(pd.to_numeric, errors='coerce')
)

# fallback seguro
df['Odd_H'] = df[cols_existentes(priority['H'])].bfill(axis=1).iloc[:, 0]
df['Odd_D'] = df[cols_existentes(priority['D'])].bfill(axis=1).iloc[:, 0]
df['Odd_A'] = df[cols_existentes(priority['A'])].bfill(axis=1).iloc[:, 0]

base = df

print("Fallback de odds aplicado com sucesso.")

base = base[['Date','Liga','HomeTeam','AwayTeam','FTHG','FTAG','Odd_H','Odd_D','Odd_A']]
base.columns = ['Date','League','Home','Away','Goals_H_FT','Goals_A_FT','Odd_H_FT','Odd_D_FT','Odd_A_FT']


base = rename_leagues(base)

#================ IMPORTAR JOGOS DO DIA ========


import pandas as pd

url = "https://www.football-data.co.uk/fixtures.csv"

# Carregar csv diretamente do site
jogos = pd.read_csv(url)




df = jogos.copy()

priority = {
    'H': ['PSH', 'B365H', 'BWH', 'AvgH', 'IWH', 'WHH', 'VCH', 'MaxH', 'MinH'],
    'D': ['PSD', 'B365D', 'BWD', 'AvgD', 'IWD', 'WHD', 'VCD', 'MaxD', 'MinD'],
    'A': ['PSA', 'B365A', 'BWA', 'AvgA', 'IWA', 'WHA', 'VCA', 'MaxA', 'MinA']
}

# função para pegar apenas colunas existentes
def cols_existentes(cols):
    return [c for c in cols if c in df.columns]

# converter odds existentes
odds_cols = [c for cols in priority.values() for c in cols if c in df.columns]

df[odds_cols] = (
    df[odds_cols]
    .replace(',', '.', regex=True)
    .apply(pd.to_numeric, errors='coerce')
)

# fallback seguro
df['Odd_H'] = df[cols_existentes(priority['H'])].bfill(axis=1).iloc[:, 0]
df['Odd_D'] = df[cols_existentes(priority['D'])].bfill(axis=1).iloc[:, 0]
df['Odd_A'] = df[cols_existentes(priority['A'])].bfill(axis=1).iloc[:, 0]

jogos = df

print("Fallback de odds aplicado com sucesso.")


jogos = jogos[['Date','Time','Div','HomeTeam','AwayTeam','Odd_H','Odd_D','Odd_A']]
jogos.columns = ['Date','Time','League','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT']

jogos = rename_leagues(jogos)


# ============ CRIAÇÃO DE VARIÁVEIS  ===========

Base_de_Dados_FlashScore = base
Jogos_do_Dia_FlashScore = jogos

import pandas as pd
import numpy as np
from datetime import date, timedelta

pd.set_option('display.max_columns', None)

def drop_reset_index(df):
    df = df.dropna()
    df = df.reset_index(drop=True)
    df.index += 1
    return df

# Opções: [5], [10], ou [5, 10] para ambos
PERIODOS_ANALISE = [3, 5, 10]

leagues = ['ENGLAND 1','ENGLAND 2','ENGLAND 3','ENGLAND 4',
    'ESCOCIA 1','ESCOCIA 2','ESCOCIA 3',
    'ALEMANHA 1','ALEMANHA 2',
    'ITALIA 1','ITALIA 2',
    'ESPANHA 1','ESPANHA 2',
    'FRANÇA 1','FRANÇA 2',
    'HOLANDA 1','BELGICA 1','PORTUGAL 1','TURQUIA 1','GRECIA 1'
]

# ========== CARREGAMENTO DOS DADOS ==========
# 1) Link da base de dados histórica

#url_base_dados = r"C:\Users\SIDNEI\Downloads\Base_de_Dados_FootyStats.csv"
#Base_de_Dados_FlashScore = pd.read_csv(url_base_dados)
Base_de_Dados_FlashScore = Base_de_Dados_FlashScore[Base_de_Dados_FlashScore['League'].isin(leagues)]

# 2) Colunas a selecionar da base de dados
colunas_historicas = ['Date','League','Home','Away','Goals_H_FT','Goals_A_FT',
                      'Odd_H_FT','Odd_D_FT','Odd_A_FT',
                      #'Odd_Over25_FT', 'Odd_Under25_FT',
                      #'Odd_BTTS_Yes', 'Odd_BTTS_No',
                     ]

df_historico_original = Base_de_Dados_FlashScore[colunas_historicas].copy()

# Filtrar apenas colunas com odd diferente de zero
columns_to_filter = ['Odd_H_FT', 'Odd_D_FT', 'Odd_A_FT',
                     # 'Odd_DC_1X', 'Odd_DC_12', 'Odd_DC_X2',
                     # 'Odd_Over15_FT', 'Odd_Under15_FT',
                     # 'Odd_Over25_FT', 'Odd_Under25_FT',
                     # 'Odd_BTTS_Yes', 'Odd_BTTS_No',
]

df_historico_original = df_historico_original[(df_historico_original[columns_to_filter] != 0).all(axis=1)]
df_historico_original = drop_reset_index(df_historico_original)

df_historico_original['Date'] = pd.to_datetime(df_historico_original['Date'])
df_historico_original = df_historico_original.sort_values(by='Date').reset_index(drop=True)

# ========== FUNÇÃO PARA CALCULAR VARIÁVEIS ==========
# 3) Variáveis a criar (média, desvio padrão, cv e eficiência)
def calcular_variaveis(df, n_per, shift_val=1):       # Modifique o shift_val por shift_val=0 ou shift_val=1
    df_temp = df.copy()

    # Probabilidades
    df_temp['p_H'] = 1 / df_temp['Odd_H_FT']
    df_temp['p_D'] = 1 / df_temp['Odd_D_FT']
    df_temp['p_A'] = 1 / df_temp['Odd_A_FT']

    # Pontos
    df_temp['PT_H'] = np.where(df_temp['Goals_H_FT'] > df_temp['Goals_A_FT'], 3,
                                np.where(df_temp['Goals_H_FT'] == df_temp['Goals_A_FT'], 1, 0))
    df_temp['PT_A'] = np.where(df_temp['Goals_H_FT'] > df_temp['Goals_A_FT'], 0,
                                np.where(df_temp['Goals_H_FT'] == df_temp['Goals_A_FT'], 1, 3))

    for team_type in ['Home', 'Away']:
        prefix = 'H' if team_type == 'Home' else 'A'
        opponent_prefix = 'A' if team_type == 'Home' else 'H'

        min_periods_val = 1

        # Pontos
        df_temp[f'Media_PT_{prefix}_{n_per}'] = df_temp.groupby(team_type)[f'PT_{prefix}'].rolling(window=n_per, min_periods=min_periods_val).mean().shift(shift_val).reset_index(0, drop=True)
        df_temp[f'DesvPad_PT_{prefix}_{n_per}'] = df_temp.groupby(team_type)[f'PT_{prefix}'].rolling(window=n_per, min_periods=min_periods_val).std().shift(shift_val).reset_index(0, drop=True)
        df_temp[f'CV_PT_{prefix}_{n_per}'] = df_temp[f'DesvPad_PT_{prefix}_{n_per}'] / df_temp[f'Media_PT_{prefix}_{n_per}']
        df_temp[f'Efi_PT_{prefix}_{n_per}'] = df_temp[f'Media_PT_{prefix}_{n_per}'] / df_temp[f'CV_PT_{prefix}_{n_per}']

        # Gols Marcados
        df_temp[f'Media_GM_{prefix}_{n_per}'] = df_temp.groupby(team_type)[f'Goals_{prefix}_FT'].rolling(window=n_per, min_periods=min_periods_val).mean().shift(shift_val).reset_index(0, drop=True)
        df_temp[f'DesvPad_GM_{prefix}_{n_per}'] = df_temp.groupby(team_type)[f'Goals_{prefix}_FT'].rolling(window=n_per, min_periods=min_periods_val).std().shift(shift_val).reset_index(0, drop=True)
        df_temp[f'CV_GM_{prefix}_{n_per}'] = df_temp[f'DesvPad_GM_{prefix}_{n_per}'] / df_temp[f'Media_GM_{prefix}_{n_per}']
        df_temp[f'Efi_GM_{prefix}_{n_per}'] = df_temp[f'Media_GM_{prefix}_{n_per}'] / df_temp[f'CV_GM_{prefix}_{n_per}']

        # Gols Sofridos
        df_temp[f'Media_GS_{prefix}_{n_per}'] = df_temp.groupby(team_type)[f'Goals_{opponent_prefix}_FT'].rolling(window=n_per, min_periods=min_periods_val).mean().shift(shift_val).reset_index(0, drop=True)
        df_temp[f'DesvPad_GS_{prefix}_{n_per}'] = df_temp.groupby(team_type)[f'Goals_{opponent_prefix}_FT'].rolling(window=n_per, min_periods=min_periods_val).std().shift(shift_val).reset_index(0, drop=True)
        df_temp[f'CV_GS_{prefix}_{n_per}'] = df_temp[f'DesvPad_GS_{prefix}_{n_per}'] / df_temp[f'Media_GS_{prefix}_{n_per}']
        df_temp[f'Efi_GS_{prefix}_{n_per}'] = df_temp[f'Media_GS_{prefix}_{n_per}'] / df_temp[f'CV_GS_{prefix}_{n_per}']

        # Saldo de Gols
        df_temp[f'SG_{prefix}'] = df_temp[f'Goals_{prefix}_FT'] - df_temp[f'Goals_{opponent_prefix}_FT']
        df_temp[f'Media_SG_{prefix}_{n_per}'] = df_temp.groupby(team_type)[f'SG_{prefix}'].rolling(window=n_per, min_periods=min_periods_val).mean().shift(shift_val).reset_index(0, drop=True)
        df_temp[f'DesvPad_SG_{prefix}_{n_per}'] = df_temp.groupby(team_type)[f'SG_{prefix}'].rolling(window=n_per, min_periods=min_periods_val).std().shift(shift_val).reset_index(0, drop=True)
        df_temp[f'CV_SG_{prefix}_{n_per}'] = df_temp[f'DesvPad_SG_{prefix}_{n_per}'] / df_temp[f'Media_SG_{prefix}_{n_per}']
        df_temp[f'Efi_SG_{prefix}_{n_per}'] = df_temp[f'Media_SG_{prefix}_{n_per}'] / df_temp[f'CV_SG_{prefix}_{n_per}']

    # Substituir infinitos (inf e -inf) por 0
    df_temp = df_temp.replace([np.inf, -np.inf], 0)

    return df_temp

# ========== PROCESSAMENTO DOS DADOS HISTÓRICOS ==========
# 4) Filtrar a base histórica para jogos até o dia anterior ao dia_analise
# df_historico_filtrado = df_historico_original[df_historico_original['Date'] < pd.to_datetime(dia_analise)].copy()
df_historico_filtrado = df_historico_original
df_historico_final = df_historico_filtrado.copy()
dataframes_calculados = {}

for n_per in PERIODOS_ANALISE:
    print(f"Calculando variáveis para a base histórica com n_per = {n_per} e shift_val = 1...")
    df_temp = calcular_variaveis(df_historico_filtrado, n_per=n_per, shift_val=1)       # Modifique o shift_val por shift_val=0 ou shift_val=1
    dataframes_calculados[n_per] = df_temp

    # Fazer merge das variáveis calculadas
    colunas_variaveis = df_temp.filter(regex=rf'(Media|DesvPad|CV|Efi)_.*_[HA]_{n_per}$').columns
    df_historico_final = df_historico_final.merge(
        df_temp[colunas_variaveis],
        left_index=True, right_index=True, how='left'
    )

# Remover colunas temporárias usadas para cálculo
colunas_para_remover = df_historico_final.filter(regex=r'^(p_|PT_|GM_|GS_|SG_|VG_|CG_|CSG_)[HA]$').columns
df_historico_final = df_historico_final.drop(columns=colunas_para_remover)

# Pega a última informação de cada time na base de dados histórica filtrada
last_data_home = df_historico_final.groupby('Home').tail(1).set_index('Home')
last_data_away = df_historico_final.groupby('Away').tail(1).set_index('Away')

# ========== PROCESSAMENTO DOS JOGOS DO DIA ==========
# 5) Link dos jogos do dia selecionado

#url_jogos_dia = r"C:\Users\SIDNEI\Downloads\Jogos_do_Dia_FootyStats_2026-01-16.csv"

try:
    #Jogos_do_Dia_FlashScore = pd.read_csv(url_jogos_dia)
    Jogos_do_Dia_FlashScore = Jogos_do_Dia_FlashScore[Jogos_do_Dia_FlashScore['League'].isin(leagues)]
    Jogos_do_Dia_FlashScore = drop_reset_index(Jogos_do_Dia_FlashScore)

    # 6) Colunas a selecionar dos jogos do dia
    colunas_jogos_dia = ['Date','Time','League','Home','Away','Odd_H_FT','Odd_D_FT','Odd_A_FT',
                         #'Odd_Over25_FT', 'Odd_Under25_FT',
                         #'Odd_BTTS_Yes', 'Odd_BTTS_No'
                  ]

    df_jogos_dia = Jogos_do_Dia_FlashScore[colunas_jogos_dia].copy()

    # Adicionar as variáveis calculadas aos jogos do dia
    df_jogos_dia_final = df_jogos_dia.copy()

    # Usar apenas os períodos configurados
    for n_per_val in PERIODOS_ANALISE:
        for var_type in ['PT', 'GM', 'GS', 'SG']:
            for stat_type in ['Media', 'DesvPad', 'CV', 'Efi']:
                # Para o time da casa
                col_home_historico = f'{stat_type}_{var_type}_H_{n_per_val}'
                if col_home_historico in last_data_home.columns:
                    df_jogos_dia_final = df_jogos_dia_final.merge(
                        last_data_home[[col_home_historico]],
                        left_on='Home',
                        right_index=True,
                        how='left',
                        suffixes=('', f'_{col_home_historico}')
                    ).rename(columns={col_home_historico: col_home_historico})

                # Para o time visitante
                col_away_historico = f'{stat_type}_{var_type}_A_{n_per_val}'
                if col_away_historico in last_data_away.columns:
                    df_jogos_dia_final = df_jogos_dia_final.merge(
                        last_data_away[[col_away_historico]],
                        left_on='Away',
                        right_index=True,
                        how='left',
                        suffixes=('', f'_{col_away_historico}')
                    ).rename(columns={col_away_historico: col_away_historico})



except Exception as e:
    print(f"Não foi possível carregar os jogos do dia . Erro")

print(f"\nBase de Dados Histórica com as variáveis calculadas:")
df_historico_final = drop_reset_index(df_historico_final)


df = df_historico_final
# #################################################################################
# # Criando Targets e Calculando Profit
# ##################################################################################

# ================== Target e Profit Back =====================
df['Back_Home'] = np.where((df['Goals_H_FT'] > df['Goals_A_FT']), 1, 0)
df['Back_Home_Profit'] = np.where((df['Back_Home'] == 1), df['Odd_H_FT']-1, -1)

df['Back_Draw'] = np.where((df['Goals_H_FT'] == df['Goals_A_FT']), 1, 0)
df['Back_Draw_Profit'] = np.where((df['Back_Draw'] == 1), df['Odd_D_FT']-1, -1)

df['Back_Away'] = np.where((df['Goals_H_FT'] < df['Goals_A_FT']), 1, 0)
df['Back_Away_Profit'] = np.where((df['Back_Away'] == 1), df['Odd_A_FT']-1, -1)

# ####################################################################################

# ================== Target e Profit Zebra =====================
df['Zebra_Home'] = np.where(((df['Goals_H_FT'] > df['Goals_A_FT']) & (df['Odd_H_FT'] > df['Odd_A_FT'])), 1, 0)
df['Zebra_Home_Profit'] = np.where((df['Zebra_Home'] == 1), df['Odd_H_FT']-1, -1)

df['Zebra_Away'] = np.where(((df['Goals_A_FT'] > df['Goals_H_FT']) & (df['Odd_A_FT'] > df['Odd_H_FT'])), 1, 0)
df['Zebra_Away_Profit'] = np.where((df['Zebra_Away'] == 1), df['Odd_A_FT']-1, -1)

# ####################################################################################

# # ================== Target e Profit Dupla Chance DC =====================
# df['DC_1X'] = np.where((df['Goals_H_FT'] >= df['Goals_A_FT']), 1, 0)
# df['DC_1X_Profit'] = np.where((df['DC_1X'] == 1), df['Odd_DC_1X']-1, -1)

# df['DC_12'] = np.where((df['Goals_H_FT'] != df['Goals_A_FT']), 1, 0)
# df['DC_12_Profit'] = np.where((df['DC_12'] == 1), df['Odd_DC_12']-1, -1)

# df['DC_2X'] = np.where((df['Goals_H_FT'] <= df['Goals_A_FT']), 1, 0)
# df['DC_2X_Profit'] = np.where((df['DC_2X'] == 1), df['Odd_DC_X2']-1, -1)

# # #####################################################################################

# # ================== Target e Profit Over e Under 1.5 =====================
# df['Over_15'] = np.where(((df['Goals_H_FT'] + df['Goals_A_FT']) > 1), 1, 0)
# df['Over_15_Profit'] = np.where((df['Over_15'] == 1), df['Odd_Over15_FT']-1, -1)

# df['Under_15'] = np.where(((df['Goals_H_FT'] + df['Goals_A_FT']) < 2), 1, 0)
# df['Under_15_Profit'] = np.where((df['Under_15'] == 1), df['Odd_Under15_FT']-1, -1)

# # #####################################################################################

# ================== Target e Profit Over e Under 2.5 =====================
#df['Over_25'] = np.where(((df['Goals_H_FT'] + df['Goals_A_FT']) > 2), 1, 0)
#df['Over_25_Profit'] = np.where((df['Over_25'] == 1), df['Odd_Over25_FT']-1, -1)

#df['Under_25'] = np.where(((df['Goals_H_FT'] + df['Goals_A_FT']) < 3), 1, 0)
#df['Under_25_Profit'] = np.where((df['Under_25'] == 1), df['Odd_Under25_FT']-1, -1)

# # #####################################################################################

# # ================== Target e Profit Over e Under 3.5 =====================
# df['Over_35'] = np.where(((df['Goals_H_FT'] + df['Goals_A_FT']) > 3), 1, 0)
# df['Over_35_Profit'] = np.where((df['Over_35'] == 1), df['Odd_Over35_FT']-1, -1)

# df['Under_35'] = np.where(((df['Goals_H_FT'] + df['Goals_A_FT']) < 4), 1, 0)
# df['Under_35_Profit'] = np.where((df['Under_35'] == 1), df['Odd_Under35_FT']-1, -1)

# # ######################################################################################

# ================== Target e Profit BTTS SIM e NÃO =====================
#df['BTTS_Yes'] = np.where(((df['Goals_H_FT'] > 0) & (df['Goals_A_FT'] > 0)), 1, 0)
#df['BTTS_Yes_Profit'] = np.where((df['BTTS_Yes'] == 1), df['Odd_BTTS_Yes']-1, -1)

#df['BTTS_No'] = np.where(((df['Goals_H_FT'] == 0) | (df['Goals_A_FT'] == 0)), 1, 0)
#df['BTTS_No_Profit'] = np.where((df['BTTS_No'] == 1), df['Odd_BTTS_No']-1, -1)

# #####################################################################################
df_historico_final = df
df_historico_final = drop_reset_index(df_historico_final)

print("Targets e Profits criados")


# ##############################################################
# display(df_historico_final)

print(f"\nJogos do Dia com as variáveis calculadas:")
# display(df_jogos_dia_final)

# ======================================================================

ATUALIZAR = st.button("🚀 Atualizar Dados")

@st.cache_data
# Função drop reset index
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

@st.cache_data
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
# ==================== CARREGAMENTO INICIAL DE DADOS ===========================

# Esse url e apenas para teste
# url_jogos_dia = "https://drive.google.com/uc?export=download&id=1UTw3M68fBTT53auoK9q71ALIsOFambQB"
# # Carregar jogos do dia
# # url_jogos_dia = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Jogos_do_Dia_Teste_com_Variaveis.csv"
# jogos_do_dia = pd.read_csv(url_jogos_dia)
jogos_do_dia = df_jogos_dia_final
# url_base_dados = "https://drive.google.com/uc?export=download&id=1qjRFmREyJ7LJxqWmGho_Ct71hywHDOb0"
# base = pd.read_csv(url_base_dados)
base = df_historico_final
# ==========================================================
# garantir que Data é datetime
# df = jogos_do_dia
# df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
# df = converter_data(df)

# data mais recente da base
# data_mais_recente = df["Date"].max()
# data_mais_recente = data_mais_recente.strftime("%d/%m/%Y")
# # st.write(f"Data de jogos do dia mais recente: {data_mais_recente.strftime("%d/%m/%Y")}")
# st.write(f"Data de jogos do dia mais recente: {data_mais_recente} Total: {len(jogos_do_dia)} jogos")

# -------------------------------------------------
# df_base = base
# df_base["Date"] = pd.to_datetime(df_base["Date"], errors="coerce")
# df_base = converter_data(df_base)
# data mais recente da base
# data_mais_recente_base = df_base["Date"].max()
# data_mais_recente_base = data_mais_recente_base.strftime("%d/%m/%Y")
# st.write(f"Base de Dados Ultima data: {data_mais_recente_base}")


# ======================== GERAR PREVISÃO  =====================================
if ATUALIZAR:

    # Esse url e apenas para teste
    # url_jogos_dia = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Base_de_Dados_Teste_com_Variaveis.csv"
   # Carregar jogos do dia
    # url_jogos_dia = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Jogos_do_Dia_Teste_com_Variaveis.csv"
    # jogos_do_dia = pd.read_csv(url_jogos_dia)

    # url_base_dados = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Base_de_Dados_Teste_com_Variaveis.csv"
    # base = pd.read_csv(url_base_dados)

    # ==========================================================
    # garantir que Data é datetime
    # df = jogos_do_dia
    # df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    # df = converter_data(df)

    # # data mais recente da base
    # data_mais_recente = df["Date"].max()
    # data_mais_recente = data_mais_recente.strftime("%d/%m/%Y")
    # # st.write(f"Data de jogos do dia mais recente: {data_mais_recente.strftime("%d/%m/%Y")}")
    # st.write(f"Data de jogos do dia mais recente: {data_mais_recente} Total: {len(jogos_do_dia)} jogos")
    
    # # -------------------------------------------------
    # df_base = base
    # df_base["Date"] = pd.to_datetime(df_base["Date"], errors="coerce")
    # df_base = converter_data(df_base)
    # # data mais recente da base
    # data_mais_recente_base = df_base["Date"].max()
    # data_mais_recente_base = data_mais_recente_base.strftime("%d/%m/%Y")
    # st.write(f"Base de Dados Ultima data: {data_mais_recente_base}")

    # ======================================================
    # GERAR PREISÕES
    # ======================================================
    TARGETS = ["Back_Home",
            "Back_Draw",
            "Back_Away",
            ]

    for TARGET in TARGETS:
        TARGET = TARGET
        COL_PROFIT = f"{TARGET}_Profit" 

        # Pasta de modelos
        PASTA_MODELOS = "modelos"

        # ======================================================
        # MAPA AUTOMÁTICO MERCADO → ODD
        # ======================================================
        MAPA_ODDS = {
            "Back_Home": "Odd_H_FT",
            "Back_Draw": "Odd_D_FT",
            "Back_Away": "Odd_A_FT",
            "Zebra_Home": "Odd_H_FT",
            "Zebra_Away": "Odd_A_FT",
            "Over_15": "Odd_Over_15",
            "Under_15": "Odd_Under_15",
            "Over_25": "Odd_Over_25",
            "Under_25": "Odd_Under_25",
            "Over_35": "Odd_Over_35",
            "Under_35": "Odd_Under_35",
            "BTTS_Yes": "Odd_BTTS_Yes",
            "BTTS_No": "Odd_BTTS_No"
        }

        COL_ODD = MAPA_ODDS.get(TARGET)

        # ======================================================
        # MAPA AUTOMÁTICO MERCADO → ODD
        # ======================================================
        MAPA_ODDS_2 = {
            "Back_Home": "Odd_A_FT",
            "Back_Draw": "Odd_A_FT",
            "Back_Away": "Odd_H_FT",
            "Zebra_Home": "Odd_A_FT",
            "Zebra_Away": "Odd_H_FT",
            # "Over_15": "Odd_Under_15",
            # "Under_15": "Odd_Over_15",
            # "Over_25": "Odd_Under_25",
            # "Under_25": "Odd_Over_25",
            # "Over_35": "Odd_Under_35",
            # "Under_35": "Odd_Over_35",
            # "BTTS_Yes": "Odd_BTTS_No",
            # "BTTS_No": "Odd_BTTS_Yes"
        }

        COL_ODD_2 = MAPA_ODDS_2.get(TARGET)

        # print(COL_ODD)
        # print(COL_ODD_2)
        if COL_ODD is None:
            raise ValueError(f"Mercado {TARGET} não mapeado para odds.")

        if COL_ODD_2 is None:
            raise ValueError(f"Mercado {TARGET} não mapeado para odds.")
        # ======================================================
        # FEATURES (DEVEM SER IGUAIS AO TREINO)
        # ======================================================
        MAPA_FEATURES = {
            "Back_Home": ['Media_PT_H_5','Media_PT_A_5','DesvPad_PT_H_5','DesvPad_PT_A_5','CV_PT_H_5','CV_PT_A_5','Efi_PT_H_5',
                        'fi_PT_A_5','Media_GM_H_5','Media_GM_A_5','DesvPad_GM_H_5','DesvPad_GM_A_5'],
            "Back_Draw": ['Media_PT_H_5','Media_PT_A_5','DesvPad_PT_H_5','DesvPad_PT_A_5','CV_PT_H_5','CV_PT_A_5','Efi_PT_H_5',
                        'fi_PT_A_5','Media_GM_H_5','Media_GM_A_5'],
            "Back_Away": ['Media_PT_H_5','Media_PT_A_5','DesvPad_PT_H_5','DesvPad_PT_A_5','CV_PT_H_5','CV_PT_A_5','Efi_PT_H_5',
                        'fi_PT_A_5'],
            # "Zebra_Home":[] ,
            # "Zebra_Away": [],
            # "Over_15": "Odd_Over_15",
            # "Under_15": "Odd_Under_15",
            # "Over_25": "Odd_Over_25",
            # "Under_25": "Odd_Under_25",
            # "Over_35": "Odd_Over_35",
            # "Under_35": "Odd_Under_35",
            # "BTTS_Yes": "Odd_BTTS_Yes",
            # "BTTS_No": "Odd_BTTS_No"
        }

        FEATURES = MAPA_FEATURES.get(TARGET)

        # jogos_do_dia["Date"] = pd.to_datetime(jogos_do_dia["Date"])
        jogos_do_dia = converter_data(jogos_do_dia)
        jogos_do_dia = jogos_do_dia.sort_values("Date").reset_index(drop=True)
        # ======================================================
        # LISTAR MODELOS DO MERCADO
        # ======================================================
        arquivos_modelos = [
            f for f in os.listdir(PASTA_MODELOS)
            if f.startswith(TARGET) and f.endswith(".pkl")
        ]


        st.write(f"\n📦 Modelos encontrados para {TARGET}: {len(arquivos_modelos)}")

        # ======================================================
        # DATAFRAME FINAL DE ENTRADAS
        # ======================================================
        df_Entradas = pd.DataFrame()

        # ======================================================
        # LOOP DOS MODELOS
        # ======================================================
        for arquivo in arquivos_modelos:

            # ----------------------------------------------
            # Extrair informações do nome
            # Ex: Back_Home_EPL_ROI_12_34.pkl
            # ----------------------------------------------
            nome = arquivo.replace(".pkl", "")
            partes = nome.split("_")

            mercado = partes[0] + "_" + partes[1]
            liga = partes[2]

            print(f"\n📌 Mercado: {mercado} | Liga: {liga}")

            # ----------------------------------------------
            # Filtrar jogos da liga
            # ----------------------------------------------
            jogos_liga = jogos_do_dia[jogos_do_dia["League"] == liga].copy()

            if jogos_liga.empty:
                print("⚠️ Nenhum jogo para essa liga.")
                continue

            # ----------------------------------------------
            # Carregar modelo
            # ----------------------------------------------
            modelo = load_model(f"{PASTA_MODELOS}/{nome}")

            
            # ----------------------------------------------
            # Previsão
            # ----------------------------------------------
            df_pred = predict_model(modelo, data=jogos_liga)

            # ----------------------------------------------
            # Filtrar apenas entradas (classe 1)
            # ----------------------------------------------
            entradas = df_pred[df_pred["prediction_label"] == 1].copy()

            if entradas.empty:
                print("❌ Nenhuma entrada encontrada.")
                continue
            else:
                print(f"✅ Entradas encontradas: {len(entradas)} jogos")

            # ----------------------------------------------
            # Informações adicionais
            # ----------------------------------------------
            entradas["Mercado"] = TARGET
            entradas["Liga_Modelo"] = liga
            entradas["Modelo"] = nome
            entradas["Odd_Entrada"] = entradas[COL_ODD]
            entradas["Odd_Compar"] = entradas[COL_ODD_2]
            # ----------------------------------------------
            # Concatenar no dataframe final
            # ----------------------------------------------
            df_Entradas = pd.concat([df_Entradas, entradas], ignore_index=True)

        # ======================================================
        # RESULTADO FINAL
        # ======================================================
        if df_Entradas.empty:
            print("\n❌ Nenhuma entrada gerada.")
        else:
            df_Entradas = df_Entradas.sort_values(["Date"])
            df_Entradas.reset_index(drop=True, inplace=True)

            df_Entradas = df_Entradas[
                [
                    "Date",
                    # "Time",
                    "League",
                    "Home",
                    "Away",
                    "Mercado",
                    "Liga_Modelo",
                    "Modelo",
                    "Odd_Entrada",
                    "Odd_Compar"
                ]
            ]
            
            # st.write(f"\n✅ ENTRADAS ANTES DO FILTRO: {len(df_Entradas)} jogos")
            
            # display(df_Entradas)
            # filtro por odd
            REGRAS_MERCADO = {
                "Back_Home": lambda df_Entradas: (df_Entradas["Odd_Entrada"] < df_Entradas["Odd_Compar"]) & (df_Entradas["Odd_Entrada"] > 1.20),
                "Back_Draw": lambda df_Entradas: df_Entradas["Odd_Entrada"] >= 2.60,
                "Back_Away": lambda df_Entradas: (df_Entradas["Odd_Entrada"] < df_Entradas["Odd_Compar"]) & (df_Entradas["Odd_Entrada"] > 1.20),
                "Zebra_Home": lambda df_Entradas: (df_Entradas["Odd_Entrada"] > df_Entradas["Odd_Compar"]),
                "Zebra_Away": lambda df_Entradas: (df_Entradas["Odd_Entrada"] > df_Entradas["Odd_Compar"]),
                # "Over_15": 
                # "Under_15"
                # "Over_25"
                # "Under_25"
                # "Over_35"
                # "Under_35"
                # "BTTS_Yes"
                # "BTTS_No"
                }

            df_Entradas = df_Entradas[REGRAS_MERCADO[TARGET](df_Entradas)]

        # ======================================================
        # RESULTADO FINAL
        # ======================================================
        if df_Entradas.empty:
            print("\n❌ NENHUMA ENTRADA PASSOU NO FILTRO.")
        else:
            df_Entradas = df_Entradas.sort_values(["Date"])
            df_Entradas.reset_index(drop=True, inplace=True)
            

            df_Entradas = df_Entradas[
                [
                    "Date",
                    # "Time",
                    "League",
                    "Home",
                    "Away",
                    "Mercado",
                    "Liga_Modelo",
                    "Modelo",
                    "Odd_Entrada"
                ]
            ]
            
            print(f"\n✅ ENTRADAS APÓS FILTRO: {len(df_Entradas)} jogos")

            df_Entradas = df_Entradas[["Date",
                                    #    "Time",
                                       "League","Home","Away","Mercado","Odd_Entrada"]]
            st.write(f"\n✅ Previsão {TARGET}: {len(df_Entradas)} jogos")
            # ===============================
            # df_Entradas_prev = drop_reset_index(df_Entradas_prev)
            # st.dataframe(df_Entradas_prev)

            # ==================================================
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
                df_Entradas.to_csv(nome_previsao + ".csv", index=False)
                print(f"\nℹ️ Arquivo Passado Não Existe: {nome_previsao}.csv")
                print(f"\n✅ Previsão Salvo: {TARGET}_Previsão")
            
            else:
                # Carregar previsão passada e concactenar com recente
                previsao_passado = pd.read_csv(f"{nome_previsao + '.csv'}")
                print(f"\n✅  Arquivo Passado Carregado: {nome_previsao}.csv")
                previsao_passado = converter_data(previsao_passado)
                previsao_passado = remover_duplicatas_drop_reset_index(previsao_passado)
                # Concatenando previsão passada com recente
                
                df_Entradas = pd.concat([previsao_passado, df_Entradas], ignore_index=True)
                # Removendo duplicatas
                # df_Entradas = df_Entradas.drop_duplicates(
                #             subset=["Date", "League", "Home", "Away"],
                #             keep="last"
                #         )
                
                df_Entradas = remover_duplicatas_drop_reset_index(df_Entradas)
                
                # 🔹 2️⃣ PEGAR OS ÚLTIMOS N DIAS (ex: últimos 3, 7, 30 dias)
                # 👉 Use quando quiser um intervalo recente.

                df_Entradas["Date"] = pd.to_datetime(df_Entradas["Date"]).dt.normalize()
                df_Entradas = df_Entradas.sort_values("Date")

                dias = 100  # você escolhe
                data_min = df_Entradas["Date"].max() - pd.Timedelta(days=dias)

                df_Entradas = df_Entradas[df_Entradas["Date"] >= data_min]

                # Salvando previsão
                df_Entradas.to_csv(nome_previsao + ".csv", index=False)
                print("Arquivos Concatenados com Susseso")

        # ==================================================
        # Configuração Inicial e criar pasta de previsões
        PASTA_PREVISAO = "Previsões"
        os.makedirs(PASTA_PREVISAO, exist_ok=True)
            
        # Nome de arquivo de previsão
        nome_previsao = f"{PASTA_PREVISAO}/{TARGET}_Previsão"

        # Configuração Inicial e criar pasta de resultados
        PASTA_PREVISAO_RESUL = "Resultados"
        os.makedirs(PASTA_PREVISAO_RESUL, exist_ok=True)

        # Nome de arquivo de historico de resultado
        nome_resultado = f"{PASTA_PREVISAO_RESUL}/{TARGET}_Resultado_Previsão"
        # --------------------------------------------------
        if not os.path.exists(nome_previsao + ".csv"):
            
            # df_Entradas.to_csv(nome_modelo + ".csv", index=False)
            print(f"\nℹ️ Arquivo Passado Não Existe: {nome_previsao}.csv")
            # print(f"\n✅ Previsão Salvo: {TARGET}_Previsão")
            
        else:
            # Carregar dados da previsão passada, do resultado passado e da base de dados
            previsao_passado = pd.read_csv(f"{nome_previsao + '.csv'}")
            previsao_passado = converter_data(previsao_passado)
        
            print(f"\n✅  Arquivo Passado Carregado: {nome_previsao}.csv")
            previsao_passado = remover_duplicatas_drop_reset_index(previsao_passado)

            # Carregar base de dados
            base = pd.read_csv(url_base_dados)

            # Fazendo merge
            base = base.copy()
            previsao_passado = previsao_passado.copy()
            # Garantir tipos corretos de Datas
            # base["Date"] = pd.to_datetime(base["Date"])
            # previsao_passado["Date"] = pd.to_datetime(previsao_passado["Date"])
            base = converter_data(base)
            previsao_passado = converter_data(previsao_passado)
            
            # Times (evita erro por espaço)
            for col in ["League", "Home", "Away"]:
                base[col] = base[col].str.strip()
                previsao_passado[col] = previsao_passado[col].str.strip()

            # As colunas têm o mesmo nome

            df_resultado = previsao_passado.merge(
                base[
                    ["Date", "League", "Home", "Away", "Goals_H_FT", "Goals_A_FT",
                    f"{TARGET}", f"{TARGET}_Profit"]
                ],
                on=["Date", "League", "Home", "Away"],
                how="left"
            )

            df_resultado_recente = df_resultado[["Date", "League", "Home", "Away", "Odd_Entrada", "Goals_H_FT", "Goals_A_FT", f"{TARGET}", f"{TARGET}_Profit"]]


            if not os.path.exists(nome_resultado + ".csv"):
                # Salvando resultado recente de se resultado passado não existe
                df_resultado_recente.to_csv(nome_resultado + ".csv", index=False)
                print(f"\nℹ️ Arquivo Passado Não Existe: {nome_resultado}.csv")
                print(f"\n✅ Resultado Salvo: {TARGET}_resultado_Previsão")
            
            else:
                # Carregar dados da resultado passado e concatenar com resultado recente
                df_resultado_passado = pd.read_csv(f"{nome_resultado + '.csv'}")
                print(f"\n✅  Arquivo Passado Carregado: {nome_resultado}.csv")

                df_resultado = pd.concat([df_resultado_passado, df_resultado_recente], ignore_index=True)
                df_resultado = remover_duplicatas_drop_reset_index(df_resultado)
                df_resultado.to_csv(nome_resultado + ".csv", index=False)

                print(f"\n✅ Resultado Salvo: {TARGET}_resultado_Previsão")
                st.write(f"\n✅ Previsão e Resultado {TARGET} Salvo")

    st.write("✅Atualização concluida")
                
                
            
            


                



# url_base_dados = r"C:\Users\SIDNEI\Desktop\Meus Projectos Jupyter\Pycaret nas apostas\Testando_novo_versao_treino_previsao\Meu_APP_V1\Base_de_Dados_Teste_com_Variaveis.csv"

# base_dados = pd.read_csv(url_base_dados)







