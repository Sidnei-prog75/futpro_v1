
import streamlit as st
# import pandas as pd
# import numpy as np
# import os
# from pycaret.classification import load_model, predict_model

pg = st.navigation([
    st.Page("pages/home.py", title= "Home"),
    st.Page("pages/previsao.py", title= "Previsao"),
    st.Page("pages/historico.py", title= "Historico"),
    # st.Page("pages/graficos.py", title= "Graficos"),
    st.Page("pages/ranking.py", title= "Ranking")
])

pg.run()