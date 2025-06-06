import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from requests.exceptions import RequestException

st.set_page_config(page_title="AquaSmart - São Paulo/SP", layout="wide")

# ---- Helpers Caching ----
@st.cache_data(ttl=3600)
def get_weather_data(lat: float, lon: float) -> pd.DataFrame:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&daily=precipitation_sum&timezone=America%2FSao_Paulo"
    )
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    js = resp.json()
    df = pd.DataFrame({
        "Data": pd.to_datetime(js["daily"]["time"]),
        "Precipitação (mm)": js["daily"]["precipitation_sum"]
    }).set_index("Data")
    return df

@st.cache_data(ttl=3600)
def get_sabesp_data(url: str) -> list[dict]:
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    data = resp.json()
    if not data:
        raise ValueError("API retornou lista vazia")
    return data

# ---- Display Functions ----
def show_weather():
    st.header("🌦️ Previsão de Chuva (Próximos 7 dias)")
    try:
        df = get_weather_data(-23.5505, -46.6333)
        st.line_chart(df, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao obter dados climáticos: {e}")

def show_sabesp():
    st.header("📊 Nível do Reservatório - Sistema Cantareira (SABESP)")
    try:
        data = get_sabesp_data("https://sabesp-api.herokuapp.com/v2")
        sistemas = [item["name"] for item in data]
        escolha = st.selectbox("Escolha o sistema:", sistemas, index=sistemas.index("Cantareira"))
        entry = next(item for item in data if item["name"] == escolha)["data"]

        # parse percent to float
        pct = float(entry["volume_armazenado"].replace("%", "").strip())
        pluviod = entry["pluviometria_do_dia"]
        media = entry["media_historica_do_mes"]

        col1, col2, col3 = st.columns(3)
        col1.metric("💧 Volume Armazenado", f"{pct:.1f} %")
        col2.metric("🌧️ Pluviometria (hoje)", pluviod)
        col3.metric("📆 Média Hist. do mês", media)
        st.caption(f"Última atualização: {datetime.now():%d/%m/%Y %H:%M}")
    except (RequestException, ValueError, KeyError) as e:
        st.warning(f"⚠️ Dados reais indisponíveis ({e}). Usando valores estimados.")
        fallback = st.slider("Volume Estimado (%)", 0.0, 100.0, 45.2, 0.1)
        col1, col2, col3 = st.columns(3)
        col1.metric("💧 Volume Estimado", f"{fallback:.1f} %")
        col2.metric("🌧️ Pluviometria (hoje)", "1.1 mm")
        col3.metric("📆 Média Hist. do mês", "58.0 mm")
        st.caption("Estimativa baseada em média histórica")

def show_consumo():
    st.header("🏠 Simulação de Consumo Diário de Água (residencial)")
    dias = list(range(1, 31))
    np.random.seed(42)
    consumo = np.random.normal(loc=200, scale=20, size=30)
    df = pd.DataFrame({"Dia": dias, "Consumo (L/pessoa)": consumo}).set_index("Dia")
    st.line_chart(df, use_container_width=True)

# ---- Main ----
st.title("💧 AquaSmart - São Paulo/SP")
st.markdown("Sistema inteligente para monitoramento de chuva e reservatórios")

show_weather()
show_sabesp()
show_consumo()

