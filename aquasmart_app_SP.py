# ----- DADOS SABESP COM SIMULAÇÃO DE BACKUP -----
st.header("📊 Nível do Reservatório - Sistema Cantareira (SABESP)")

sabesp_url = "https://sabesp-api.herokuapp.com/v2"

try:
    sabesp_response = requests.get(sabesp_url)
    if sabesp_response.status_code == 200 and sabesp_response.text.strip():
        sabesp_data = sabesp_response.json()
        cantareira = next(item for item in sabesp_data if item["name"] == "Cantareira")
        dados = cantareira["data"]

        col1, col2, col3 = st.columns(3)
        col1.metric("💧 Volume Armazenado", dados["volume_armazenado"])
        col2.metric("🌧️ Pluviometria (hoje)", dados["pluviometria_do_dia"])
        col3.metric("📆 Média Hist. do mês", dados["media_historica_do_mes"])
    else:
        raise ValueError("API offline ou vazia")
except Exception:
    st.warning("⚠️ Dados reais indisponíveis. Exibindo valores estimados com base histórica.")
    col1, col2, col3 = st.columns(3)
    col1.metric("💧 Volume Armazenado", "45,2 %")
    col2.metric("🌧️ Pluviometria (hoje)", "1,1 mm")
    col3.metric("📆 Média Hist. do mês", "58,0 mm")
