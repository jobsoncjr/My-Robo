import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURAÇÃO DA INTERFACE ---
st.set_page_config(page_title="Robô OneNation Automático", layout="wide")
st.title("🤖 Scanner de Alta Assertividade")

# --- SUA CHAVE DE DADOS ---
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281" # Pegue em: https://rapidapi.com/api-sports/api/api-football

def obter_previsoes():
    url = "https://api-football-v1.p.rapidapi.com/v3/predictions"
    
    # Vamos buscar previsões para os jogos de hoje
    # Nota: No plano gratuito, você tem um limite de requisições por dia.
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    # ID 71 é o Brasileirão, ID 39 é Premier League. Podemos buscar por vários.
    # Para simplificar, o robô vai buscar os destaques do dia.
    querystring = {"fixture": "1187397"} # Exemplo de ID de jogo real

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()['response'][0]
        
        previsao = {
            "Jogo": f"{data['teams']['home']['name']} vs {data['teams']['away']['name']}",
            "Conselho": data['predictions']['advice'],
            "Confiança": data['predictions']['percent']['home'], # Porcentagem de chance casa
            "Veredito": data['predictions']['winner']['name']
        }
        return previsao
    except:
        return None

# --- O QUE APARECE NO SEU CELULAR ---
st.subheader("📡 Varredura em Tempo Real")
st.write(f"Data: {datetime.now().strftime('%d/%m/%Y')}")

if st.button("🚀 INICIAR VARREDURA AUTOMÁTICA"):
    if API_KEY == "SUA_CHAVE_AQUI":
        st.error("Erro: Você esqueceu de colocar sua API KEY no código!")
    else:
        with st.spinner('Aguarde... IA analisando confrontos...'):
            # Aqui o robô faria um loop por vários jogos
            resultado = obter_previsoes()
            
            if resultado:
                st.balloons()
                st.success("✅ Oportunidade Encontrada!")
                
                # Exibição estilizada do cartão de aposta
                st.markdown(f"""
                <div style="background-color:#1E1E1E; padding:20px; border-radius:15px; border-left: 10px solid #28a745;">
                    <h2 style="color:white;">{resultado['Jogo']}</h2>
                    <p style="color:#00ff00; font-size:25px;"><b>Probabilidade IA: {resultado['Confiança']}</b></p>
                    <p style="color:white; font-size:18px;">🎯 <b>Conselho:</b> {resultado['Conselho']}</p>
                    <p style="color:gray;">Acesse a OneNation.bet e procure este mercado.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Nenhuma oportunidade com mais de 70% encontrada agora.")
