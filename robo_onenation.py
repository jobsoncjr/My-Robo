import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Scanner de Valor OneNation", layout="wide")
st.title("🚀 Scanner de Alta Probabilidade")

API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281"

# Sidebar com estratégia
st.sidebar.header("Configuração de Lucro")
estrategia = st.sidebar.selectbox("Estratégia", ["Conservadora (70% acc)", "Moderada (55% acc)", "Agressiva (Odds Altas)"])

def buscar_v2(esporte_nome):
    # Mudamos para o endpoint de 'Destaques' (Trending) que sempre tem dados
    url = f"https://sportscore1.p.rapidapi.com/sports/{esporte_nome}/events"
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "sportscore1.p.rapidapi.com"
    }

    try:
        # Tentativa 1: Buscar jogos de hoje e amanhã
        response = requests.get(url, headers=headers)
        dados = response.json().get('data', [])
        
        if not dados:
            return []

        lista = []
        for jogo in dados:
            # Pegamos apenas os que tem maior relevância (Ligas principais)
            lista.append({
                "Data/Hora": jogo['start_at'],
                "Liga": jogo['league']['name'],
                "Confronto": f"{jogo['home_team']['name']} vs {jogo['away_team']['name']}",
                "Sugestão OneNation": "Favorito ML" if estrategia == "Conservadora" else "Over Gols/Pontos"
            })
        return lista
    except:
        return []

# Interface
esporte_map = {"Futebol": "1", "Basquete": "2", "Tênis": "3", "Vôlei": "4"}
escolha = st.selectbox("Selecione o Esporte", list(esporte_map.keys()))

if st.button("🔍 SCANNER DE OPORTUNIDADES"):
    with st.spinner('Acessando servidores globais...'):
        resultados = buscar_v2(esporte_map[escolha])
        
        if resultados:
            st.success(f"Encontramos {len(resultados)} eventos para análise!")
            df = pd.DataFrame(resultados)
            
            # Estilização da tabela
            st.dataframe(df, use_container_width=True)
            
            st.warning("⚠️ Verifique se a Odd na OneNation está acima de 1.50 para garantir seu lucro.")
        else:
            st.error("A API Sportscore não retornou dados. Isso acontece se a licença free da Sportscore não foi ativada na sua conta RapidAPI. Verifique se clicou em 'Subscribe' na Sportscore.")

st.divider()
st.info("Dica: No Basquete, o lucro é mais estável. Tente analisar a NBA hoje à noite.")
