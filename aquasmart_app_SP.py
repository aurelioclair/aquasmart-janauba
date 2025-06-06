import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# 1) Page config – sempre em primeiro
st.set_page_config(page_title="AquaSmart – São Paulo/SP", layout="wide")

# 2) CSS customizado
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

# 4) Previsão de Chuva
st.markdown("<div class='card'><h2>🌦️ Previsão de Chuva (Próximos 7 dias)</h2></div>", unsafe_allow_html=True)
@st.cache_data(ttl=600)
def fetch_precip(lat, lon):
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={lat}&longitude={lon}&daily=precipitation_sum"
           "&timezone=America%2FSao_Paulo")
    r = requests.get(url, timeout=5)
    r.raise_for_status()
    js = r.json()
    df = pd.DataFrame({
        "Data": pd.to_datetime(js["daily"]["time"]),
        "Precipitação (mm)": js["daily"]["precipitation_sum"]
    })
    df = df.set_index("Data")
    return df

try:
    df_chuva = fetch_precip(-23.5505, -46.6333)
    st.line_chart(df_chuva, use_container_width=True)
except Exception as e:
    st.error("Erro ao obter previsão de chuva: " + str(e))

st.markdown("---")

# 5) Nível do Reservatório (Fallback simulado)
st.markdown("<div class='card'><h2>📊 Nível do Reservatório – Sistema Cantareira</h2></div>", unsafe_allow_html=True)
# Simulação de volume e entrada
volume_pct = 46.2  # % médio histórico
entrada_mm  = 1.3  # mm precipitação * fator
# Exiba como métricas
col1, col2 = st.columns(2)
col1.metric("💧 Volume Armazenado", f"{volume_pct:.1f} %")
col2.metric("🌧️ Entrada de Água (estimada)", f"{entrada_mm:.1f} mm")
# Gráfico de tendência (simulado)
dias = np.arange(1, 31)
volumes = np.clip(volume_pct + np.random.normal(0, 0.5, size=30).cumsum(), 20, 80)
fig, ax = plt.subplots()
ax.plot(dias, volumes, marker='o', linestyle='-', color='#0055aa')
ax.set_title("📈 Tendência do Volume (%)")
ax.set_xlabel("Dia do mês")
ax.set_ylabel("% Volume")
ax.grid(alpha=0.3)
st.pyplot(fig, use_container_width=True)

st.markdown("---")

# 6) Alerta e Simulação de Consumo
st.markdown("<div class='card'><h2>🚨 Alerta e Simulação</h2></div>", unsafe_allow_html=True)
# Exemplo de alerta
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

# Simulação de consumo x entrada
sim_x = np.arange(0, 10)
sim_consumo = np.linspace(15, 5, 10)
sim_entrada = np.linspace(5, 15, 10)
fig2, ax2 = plt.subplots()
ax2.plot(sim_x, sim_consumo, label="Consumo", color='#0055aa')
ax2.plot(sim_x, sim_entrada, label="Entrada de Água", color='#88bfff')
ax2.set_title("Simulação: Consumo vs. Entrada")
ax2.legend()
ax2.grid(alpha=0.3)
st.pyplot(fig2, use_container_width=True)

st.markdown("---")
st.caption(f"Última atualização: {datetime.now():%d/%m/%Y %H:%M}")
