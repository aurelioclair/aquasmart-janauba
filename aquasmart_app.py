import pandas as pd
import numpy as np
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import streamlit as st

# ----- PARTE 1: Previsão de chuva (Open-Meteo) -----
lat, lon = -15.8024, -43.3086
url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=America%2FSao_Paulo"

data = requests.get(url).json()
df_clima = pd.DataFrame({
    "Data": pd.to_datetime(data['daily']['time']),
    "Precipitacao_Prevista_mm": data['daily']['precipitation_sum']
})

# ----- PARTE 2: Simulação de consumo e nível de reservatório -----
dias = 60
np.random.seed(42)
datas_passadas = pd.date_range(end=datetime.today(), periods=dias)

chuva_hist = np.random.gamma(2, 4, dias)
consumo = np.random.normal(15000, 1000, dias)
entrada = chuva_hist * 80
nivel = np.clip(np.cumsum(entrada - consumo) + 5e5, 0, None)

df_hist = pd.DataFrame({
    "Data": datas_passadas,
    "Precipitacao_mm": chuva_hist,
    "Consumo_m3": consumo,
    "Entrada_Agua_m3": entrada,
    "Nivel_Reservatorio_m3": nivel
})

# ----- PARTE 3: Streamlit Dashboard -----
st.set_page_config(page_title="AquaSmart - Janaúba", layout="wide")

st.title("💧 AquaSmart - Janaúba/MG")
st.subheader("Previsão de Chuva e Gestão de Abastecimento de Água")

col1, col2 = st.columns(2)

with col1:
    st.metric("Precipitação prevista para amanhã", f"{df_clima['Precipitacao_Prevista_mm'][1]:.1f} mm")
    st.bar_chart(df_clima.set_index("Data")["Precipitacao_Prevista_mm"])

with col2:
    st.metric("Nível atual do reservatório", f"{df_hist['Nivel_Reservatorio_m3'].iloc[-1]:,.0f} m³")
    st.line_chart(df_hist.set_index("Data")[["Consumo_m3", "Entrada_Agua_m3"]])

# ----- PARTE 4: Simulação de risco -----
media_entrada = df_hist["Entrada_Agua_m3"][-7:].mean()
media_consumo = df_hist["Consumo_m3"][-7:].mean()
saldo_diario = media_entrada - media_consumo
dias_restantes = df_hist['Nivel_Reservatorio_m3'].iloc[-1] / abs(saldo_diario) if saldo_diario < 0 else 999

st.subheader("🔔 Alerta de Abastecimento")
if dias_restantes < 30:
    st.error(f"🚨 Se nada mudar, a água pode acabar em aproximadamente {int(dias_restantes)} dias!")
    st.info("Sugestão: Ativar campanha de economia e revisão do uso agrícola.")
else:
    st.success("✅ Abastecimento dentro dos padrões para os próximos 30 dias.")
