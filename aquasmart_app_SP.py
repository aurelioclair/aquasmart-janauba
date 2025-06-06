import streamlit as st
import requests
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# 1) Configuração da página (sempre primeiro)
st.set_page_config(
    page_title="AquaSmart – São Paulo/SP",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2) CSS customizado para tema branco+azul e cards
st.markdown("""
<style>
/* Fundo geral suave */
[data-testid="stAppViewContainer"] { background-color: #f7faff; }

/* Cards */
.card {
  background-color: #ffffff;
  border-radius: 10px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 6px rgba(0,0,0,0.07);
}

/* Títulos */
h1, h2 {
  color: #003366;
}

/* Métricas destacadas */
.stMetric > div {
  background-color: #e9f0ff !important;
  border-radius: 8px;
  padding: 10px 14px;
}

/* Botões */
.stButton>button {
  background-color: #0055aa !important;
  color: white !important;
  border-radius: 4px;
}
</style>
""", unsafe_allow_html=True)

# 3) Cabeçalho
st.title("💧 AquaSmart – São Paulo/SP")
st.markdown("> Sistema inteligente para monitoramento de chuva e abastecimento de água")
st.markdown("---")

# 4) Previsão de Chuva (next 7 days)
st.markdown("<div class='card'><h2>🌦️ Previsão de Chuva (Próximos 7 dias)</h2></div>", unsafe_allow_html=True)

@st.cache_data(ttl=600)
def fetch_precip(lat: float, lon: float) -> pd.DataFrame:
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&daily=precipitation_sum&timezone=America%2FSao_Paulo"
    )
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    js = r.json()
    df = pd.DataFrame({
        "Data": pd.to_datetime(js["daily"]["time"]),
        "Precipitação (mm)": js["daily"]["precipitation_sum"]
    }).set_index("Data")
    return df

try:
    df_chuva = fetch_precip(-23.5505, -46.6333)
    fig_prec = px.line(
        df_chuva.reset_index(),
        x="Data",
        y="Precipitação (mm)",
        line_shape="spline",
        markers=True,
        height=300,
        template="plotly_white"
    )
    fig_prec.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis_title="Dia",
        yaxis_title="mm"
    )
    st.plotly_chart(fig_prec, use_container_width=True)
except Exception as e:
    st.error(f"Erro ao obter previsão de chuva: {e}")

st.markdown("---")

# 5) Nível do Reservatório (fallback simulado)
st.markdown("<div class='card'><h2>📊 Nível do Reservatório – Sistema Cantareira</h2></div>", unsafe_allow_html=True)

# Valores simulados
volume_pct = 46.2   # % médio histórico
entrada_mm  = 1.3   # mm estimados de entrada

# Exibir métricas
col1, col2 = st.columns(2)
col1.metric("💧 Volume Armazenado", f"{volume_pct:.1f} %")
col2.metric("🌧️ Entrada de Água (estimada)", f"{entrada_mm:.1f} mm")

# Gráfico de tendência de volume
dias = np.arange(1, 31)
volumes = np.clip(volume_pct + np.random.normal(0, 0.5, size=30).cumsum(), 20, 80)
df_vol = pd.DataFrame({
    "Dia do mês": dias,
    "% Volume": volumes
})

fig_vol = px.line(
    df_vol,
    x="Dia do mês",
    y="% Volume",
    line_shape="spline",
    markers=True,
    height=300,
    template="plotly_white"
)
fig_vol.update_layout(
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(showgrid=False),
    yaxis=dict(title="% Volume")
)
st.plotly_chart(fig_vol, use_container_width=True)

st.markdown("---")

# 6) Alerta e Simulação de Consumo
st.markdown("<div class='card'><h2>🚨 Alerta e Simulação</h2></div>", unsafe_allow_html=True)

dias_restantes = 15
st.markdown(f"### Se continuar assim, faltarão água em **{dias_restantes} dias**")

if st.button("Ativar Alerta à População"):
    st.success("✅ Alerta enviado com sucesso!")

# Dicas práticas
col1, col2 = st.columns(2)
with col1:
    st.markdown("💧 **Dica:** Reduza o banho para 5 minutos")
with col2:
    st.markdown("🚰 **Dica:** Feche torneiras ao escovar os dentes")

# Gráfico de Consumo vs Entrada
sim_x       = np.arange(0, 10)
sim_consumo = np.linspace(15, 5, 10)
sim_entrada = np.linspace(5, 15, 10)
df_sim = pd.DataFrame({
    "Dia": sim_x,
    "Consumo": sim_consumo,
    "Entrada de Água": sim_entrada
})

fig_sim = px.line(
    df_sim,
    x="Dia",
    y=["Consumo", "Entrada de Água"],
    line_shape="spline",
    markers=True,
    height=300,
    template="plotly_white",
    color_discrete_map={"Consumo":"#0055aa", "Entrada de Água":"#88bfff"}
)
fig_sim.update_layout(
    margin=dict(l=20, r=20, t=30, b=20),
    yaxis_title="m³",
    legend_title_text=""
)
st.plotly_chart(fig_sim, use_container_width=True)

st.markdown("---")
st.caption(f"Última atualização: {datetime.now():%d/%m/%Y %H:%M}")
