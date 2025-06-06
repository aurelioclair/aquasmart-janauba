
import streamlit as st
import requests
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="AquaSmart - São Paulo/SP", layout="wide")

# ----- TÍTULO -----
st.title("💧 AquaSmart - São Paulo/SP")
st.markdown("Sistema inteligente para monitoramento de chuva e reservatórios")

# ----- PREVISÃO DO TEMPO (Open-Meteo) -----
st.header("🌦️ Previsão de Chuva (Próximos 7 dias)")

latitude = -23.5505
longitude = -46.6333

weather_url = (
    f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}"
    "&daily=precipitation_sum&timezone=America%2FSao_Paulo"
)

try:
    weather_response = requests.get(weather_url).json()
    dias = weather_response["daily"]["time"]
    chuva = weather_response["daily"]["precipitation_sum"]

    st.line_chart(
        data=chuva,
        x=dias,
        y="Precipitação (mm)",
        use_container_width=True
    )
except Exception as e:
    st.error("Erro ao obter dados climáticos: " + str(e))

# ----- DADOS DA SABESP (via API pública) -----
st.header("📊 Nível do Reservatório - Sistema Cantareira (SABESP)")

sabesp_url = "https://sabesp-api.herokuapp.com/v2"

try:
    sabesp_response = requests.get(sabesp_url).json()
    cantareira = next(item for item in sabesp_response if item["name"] == "Cantareira")
    dados = cantareira["data"]

    col1, col2, col3 = st.columns(3)
    col1.metric("💧 Volume Armazenado", dados["volume_armazenado"])
    col2.metric("🌧️ Pluviometria (hoje)", dados["pluviometria_do_dia"])
    col3.metric("📆 Média Hist. do mês", dados["media_historica_do_mes"])
except Exception as e:
    st.error("Erro ao obter dados da SABESP: " + str(e))

# ----- SIMULAÇÃO DO CONSUMO -----
st.header("🏠 Simulação de Consumo Diário de Água (residencial)")

dias = list(range(1, 31))
np.random.seed(42)
consumo = np.random.normal(loc=200, scale=20, size=30)  # litros por pessoa por dia

fig, ax = plt.subplots()
ax.plot(dias, consumo, marker='o', linestyle='-', color='blue')
ax.set_title("Consumo Diário Estimado (Litros por Pessoa)")
ax.set_xlabel("Dia")
ax.set_ylabel("Consumo (L)")
st.pyplot(fig)
