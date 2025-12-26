import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OneNation Multi-Scanner", page_icon="🏆")

# Sua Key (Já configurada)
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281"

st.title("🏆 Scanner Multiesportes")
st.write("Análise automática para busca de lucro consistente.")

# Escolha do Esporte
esporte = st.selectbox("O que vamos analisar hoje?", 
                       ["Futebol", "Basquete", "Tênis", "Vôlei", "MMA"])

# Mapeamento para a API
mapa_esportes = {
    "Futebol": "football",
    "Basquete": "basketball",
    "Tênis": "tennis",
    "Vôlei": "volleyball",
    "MMA": "mma"
}

def buscar_dados():
    # Usando o endpoint da Sportscore (Garante todos os esportes em um só lugar)
    url = f"https://sportscore1.p.rapidapi.com/sports/{mapa_esportes[esporte]}/events"
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "sportscore1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers)
        jogos = response.json().get('data', [])
        
        analises = []
        for jogo in jogos:
            # Filtramos apenas jogos que ainda não começaram
            if jogo['status'] == 'not_started':
                analises.append({
                    "Horário": jogo['start_at'][11:16],
                    "Evento": f"{jogo['home_team']['name']} vs {jogo['away_team']['name']}",
                    "Liga": jogo['league']['name'],
                    "Probabilidade": "Analise na OneNation"
                })
        return analises
    except:
        return []

# --- BOTÃO DE COMANDO ---
if st.button(f"🔍 ESCANEAR {esporte.upper()}"):
    with st.spinner('IA varrendo mercados...'):
        resultados = buscar_dados()
        
        if resultados:
            st.success(f"Encontrado {len(resultados)} oportunidades em {esporte}")
            for r in resultados:
                with st.expander(f"⏰ {r['Horário']} - {r['Evento']}"):
                    st.write(f"🏟️ **Competição:** {r['Liga']}")
                    st.write(f"✅ **Estratégia Recomendada:** Focar em mercados de 'Vencedor' ou 'Total de Pontos'.")
                    st.info("Acesse a OneNation.bet para conferir as Odds.")
        else:
            st.warning(f"Sem jogos de {esporte} disponíveis para análise imediata.")

st.divider()
st.caption("Foco em margem de lucro e gestão de banca.")
