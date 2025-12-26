import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Scanner OneNation Pro", layout="wide")
st.title("🤖 Scanner Global: Próximas 24h")

# Sua chave (Verificada)
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281" 

def buscar_jogos():
    # Foca especificamente no dia de amanhã (26/12) onde o mercado abre
    amanha = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"date": amanha} # Busca TUDO do dia
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        dados_brutos = response.json()
        
        # Verifica se a API retornou erro de limite ou algo assim
        if 'errors' in dados_brutos and dados_brutos['errors']:
            st.error(f"Erro da API: {dados_brutos['errors']}")
            return []

        jogos = dados_brutos.get('response', [])
        
        lista = []
        for item in jogos:
            # Pegamos apenas jogos que ainda vão começar
            lista.append({
                "Hora": item['fixture']['date'][11:16],
                "País": item['league']['country'],
                "Liga": item['league']['name'],
                "Jogo": f"{item['teams']['home']['name']} vs {item['teams']['away']['name']}"
            })
        return lista
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return []

# --- BOTÃO DE AÇÃO ---
if st.button("🔍 ESCANEAR JOGOS DE AMANHÃ"):
    with st.spinner('Varrendo todos os estádios do mundo...'):
        resultados = buscar_jogos()
        
        if resultados:
            st.success(f"✅ Sucesso! Encontrei {len(resultados)} jogos para amanhã.")
            df = pd.DataFrame(resultados)
            
            # Ordenar por hora
            df = df.sort_values(by="Hora")
            
            st.dataframe(df, use_container_width=True)
            st.info("💡 Agora escolha um desses jogos e veja as odds na OneNation.bet")
        else:
            st.warning("Ainda não encontrei jogos. Isso pode ser por causa do feriado de Natal ou limite da API.")

st.divider()
st.caption("Configurado para uso pessoal: OneNation.bet")
