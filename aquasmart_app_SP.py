import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
from requests.exceptions import RequestException

# ——— Page config must be first ———
st.set_page_config(page_title="AquaSmart", layout="wide", initial_sidebar_state="expanded")

# ——— Global CSS for cards, colors, typography ———
st.markdown("""<style>
/* Background */
[data-testid="stAppViewContainer"] { background-color: #f7faff; }
/* Sidebar */
[data-testid="stSidebar"] { background-color: #ffffff; }
[data-testid="stSidebar"] .css-1d391kg { font-size: 1.2rem; font-weight: bold; color: #003366; margin-bottom: 1rem; }
/* Card styling */
.card {
  background-color: #ffffff;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
/* Headings */
h1, .css-18e3th9 { color: #003366; }
/* Metrics button */
.css-1emrehy.edgvbvh3 { background-color: #0055aa !important; color: white !important; }
</style>""", unsafe_allow_html=True)

# ——— Sidebar ———
with st.sidebar:
    st.image("https://raw.githubusercontent.com/aurelioclair/aquasmart-janauba/main/logo.png", width=100)
    st.markdown("## AquaSmart")
    page = st.radio("", ["Previsão Climática", "Nível do Reservatório", "Alerta e Simulação"])

# ——— Data fetchers ———
@st.cache_data(ttl=3600)
def get_weather():
    lat, lon = -23.5505, -46.6333
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=precipitation_sum&timezone=America%2FSao_Paulo"
    r = requests.get(url, timeout=5); r.raise_for_status()
    js = r.json()
    df = pd.DataFrame({
        "Data": pd.to_datetime(js["daily"]["time"]),
        "Precipitação": js["daily"]["precipitation_sum"]
    })
    return df

@st.cache_data(ttl=3600)
def get_sabesp():
    url = "https://sabesp-api.herokuapp.com/v2"
    r = requests.get(url, timeout=5); r.raise_for_status()
    data = r.json()
    return { item["name"]: item["data"] for item in data }

# ——— Previsão Climática ———
if page == "Previsão Climática":
    st.markdown("<div class='card'><h2>Previsão Climática</h2></div>", unsafe_allow_html=True)
    df = get_weather()
    # Bar chart
    fig_bar = px.bar(df, x=df["Data"].dt.strftime("%a"), y="Precipitação",
                     labels={"x": "", "Precipitação":"mm"},
                     color_discrete_sequence=["#0055aa"])
    fig_bar.update_layout(margin=dict(l=0,r=0,t=20,b=20), paper_bgcolor="white")
    # Risk indicator
    risk = "Alto" if df["Precipitação"].mean() < 5 else "Moderado"
    risk_color = "red" if risk=="Alto" else "orange"

    col1, col2 = st.columns([3,2])
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown(f"<p style='text-align:center; color:{risk_color};'>☁️ Risco de Estiagem: <strong>{risk}</strong></p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='card' style='text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h3>Nível do Reservatório</h3>", unsafe_allow_html=True)
        # placeholder gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=75,
            gauge={'axis': {'range': [0,100], 'bar': {'color': '#0055aa'}}}
        ))
        fig_gauge.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=200, paper_bgcolor="white")
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# ——— Nível do Reservatório ———
elif page == "Nível do Reservatório":
    st.markdown("<div class='card'><h2>Nível do Reservatório</h2></div>", unsafe_allow_html=True)
    try:
        sabesp = get_sabesp()
        cant = sabesp["Cantareira"]
        pct = float(cant["volume_armazenado"].replace("%",""))
        entrada = float(cant["pluviometria_do_dia"].replace(" mm","")) * 50e3  # exemplo
        consumo = 52e6  # m3 placeholder

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=pct,
            gauge={'axis': {'range': [0,100], 'bar': {'color': '#0055aa'}}}
        ))
        fig_gauge.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=300, paper_bgcolor="white")

        fig_line = px.line(x=[0,1,2,3,4], y=[consumo, consumo*0.9, consumo*1.1, consumo, consumo*0.95],
                           labels={'x':'', 'y':'m³'}, color_discrete_sequence=["#0055aa"])
        fig_line.update_layout(margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="white")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.plotly_chart(fig_gauge, use_container_width=True)
            st.write(f"<p style='text-align:center;'>Consumo: {int(consumo/1e6)} mil m³</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.plotly_chart(fig_line, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
    except Exception as e:
        st.error("Erro ao obter dados SABESP: " + str(e))

# ——— Alerta e Simulação ———
else:
    st.markdown("<div class='card'><h2>Alerta e Simulação</h2></div>", unsafe_allow_html=True)
    # days until empty
    days_left = 15
    st.markdown(f"<h3>Se continuar assim, faltará água em {days_left} dias</h3>", unsafe_allow_html=True)
    if st.button("Ativar Alerta à População"):
        st.success("Alerta enviado!")
    # advice icons
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("💧 Reduza o banho para 5 min")
    with col2:
        st.markdown("🚰 Feche torneiras ao escovar")
    # simulation line
    sim_x = list(range(10))
    sim_y1 = np.linspace(15,5,10)
    sim_y2 = np.linspace(5,15,10)
    fig_sim = go.Figure()
    fig_sim.add_trace(go.Scatter(x=sim_x, y=sim_y1, name="Consumo", line=dict(color="#0055aa")))
    fig_sim.add_trace(go.Scatter(x=sim_x, y=sim_y2, name="Entrada de Água", line=dict(color="#88bfff")))
    fig_sim.update_layout(margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor="white")
    st.plotly_chart(fig_sim, use_container_width=True)




