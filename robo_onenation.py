import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Scanner Multi-Datas OneNation", page_icon="📅", layout="wide")

# Sua Key (Já configurada)
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281"

st.title("📅 Scanner de Eventos e Datas")
st.write("Selecione o esporte e a data para encontrar as melhores margens de lucro.")

# --- BARRA LATERAL DE CONFIGURAÇÃO ---
st.sidebar.header("Filtros de Busca")

esporte = st.sidebar.selectbox("Modalidade", 
                       ["Futebol", "Basquete", "Tênis", "Vôlei", "MMA"])

# SELETOR DE DATA: O usuário escolhe o dia aqui
data_selecionada = st.sidebar.date_input("Escolha a data", datetime.now())
data_formatada = data_selecionada.strftime('%Y-%m-%d')

# Mapeamento para a API
mapa_esportes = {
    "Futebol": "football",
    "Basquete": "basketball",
    "Tênis": "tennis",
    "Vôlei": "volleyball",
    "MMA": "mma"
}

def buscar_dados(data_alvo):
    # Endpoint filtrando por data específica
    url = f"https://sportscore1.p.rapidapi.com/sports/{mapa_esportes[esporte]}/events"
    
    # Parâmetros para buscar por data
    querystring = {"date": data_alvo}
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "sportscore1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        jogos = response.json().get('data', [])
        
        analises = []
        for jogo in jogos:
            # Pegamos apenas jogos agendados ou que ainda não acabaram
            status = jogo.get('status', '')
            if status == 'not_started' or status == 'scheduled':
                analises.append({
                    "Horário": jogo['start_at'][11:16],
                    "Evento": f"{jogo['home_team']['name']} vs {jogo['away_team']['name']}",
                    "Liga": jogo['league']['name'],
                    "ID": jogo['id']
                })
        return analises
    except Exception as e:
        return []

# --- BOTÃO DE COMANDO ---
if st.button(f"🔍 BUSCAR {esporte.upper()} EM {data_selecionada.strftime('%d/%m/%Y')}"):
    with st.spinner(f'IA vasculhando {esporte} para o dia {data_selecionada.strftime("%d/%m")}...'):
        resultados = buscar_dados(data_formatada)
        
        if resultados:
            st.success(f"Encontradas {len(resultados)} oportunidades!")
            
            # Criando uma tabela organizada
            df = pd.DataFrame(resultados).drop(columns=['ID'])
            st.table(df)
            
            st.info("💡 Dica de Lucro: Compare estas partidas com as odds na OneNation.bet")
        else:
            st.warning(f"Ainda não há eventos de {esporte} registrados para esta data.")
            st.info("Tente uma data mais próxima ou mude o esporte.")

st.divider()
st.caption(f"Scanner conectado via Sportscore API. Chave: {API_KEY[:5]}***")
