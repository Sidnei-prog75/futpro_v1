import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import date, timedelta
from pycaret.classification import load_model, predict_model

st.title("Pagina Inicial")

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
url_jogos_dia = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Base_de_Dados_Teste_com_Variaveis.csv"
# Carregar jogos do dia
# url_jogos_dia = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Jogos_do_Dia_Teste_com_Variaveis.csv"
jogos_do_dia = pd.read_csv(url_jogos_dia)

url_base_dados = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Base_de_Dados_Teste_com_Variaveis.csv"
base = pd.read_csv(url_base_dados)

# ==========================================================
# garantir que Data é datetime
df = jogos_do_dia
# df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = converter_data(df)

# data mais recente da base
data_mais_recente = df["Date"].max()
data_mais_recente = data_mais_recente.strftime("%d/%m/%Y")
# st.write(f"Data de jogos do dia mais recente: {data_mais_recente.strftime("%d/%m/%Y")}")
st.write(f"Data de jogos do dia mais recente: {data_mais_recente} Total: {len(jogos_do_dia)} jogos")

# -------------------------------------------------
df_base = base
# df_base["Date"] = pd.to_datetime(df_base["Date"], errors="coerce")
df_base = converter_data(df_base)
# data mais recente da base
data_mais_recente_base = df_base["Date"].max()
data_mais_recente_base = data_mais_recente_base.strftime("%d/%m/%Y")
st.write(f"Base de Dados Ultima data: {data_mais_recente_base}")


# ======================== GERAR PREVISÃO  =====================================
if ATUALIZAR:

    # Esse url e apenas para teste
    # url_jogos_dia = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Base_de_Dados_Teste_com_Variaveis.csv"
   # Carregar jogos do dia
    # url_jogos_dia = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Jogos_do_Dia_Teste_com_Variaveis.csv"
    jogos_do_dia = pd.read_csv(url_jogos_dia)

    # url_base_dados = r"C:\Users\SIDNEI\Desktop\meu_app_futebol\Base_de_Dados_Teste_com_Variaveis.csv"
    base = pd.read_csv(url_base_dados)

    # ==========================================================
    # garantir que Data é datetime
    df = jogos_do_dia
    # df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = converter_data(df)

    # # data mais recente da base
    # data_mais_recente = df["Date"].max()
    # data_mais_recente = data_mais_recente.strftime("%d/%m/%Y")
    # # st.write(f"Data de jogos do dia mais recente: {data_mais_recente.strftime("%d/%m/%Y")}")
    # st.write(f"Data de jogos do dia mais recente: {data_mais_recente} Total: {len(jogos_do_dia)} jogos")
    
    # -------------------------------------------------
    df_base = base
    # df_base["Date"] = pd.to_datetime(df_base["Date"], errors="coerce")
    df_base = converter_data(df_base)
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