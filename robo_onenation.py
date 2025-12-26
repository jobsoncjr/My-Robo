import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Scanner OneNation Pro", layout="wide")
st.title("🤖 Robô Scanner: Varredura Total")

# Sua chave configurada
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281" 

def buscar_oportunidades():
    hoje = datetime.now().date()
    # Vamos olhar hoje e amanhã para garantir que pegamos jogos
    datas = [hoje, hoje + timedelta(days=1)]
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    lista_final = []

    with st.status("🔍 Buscando todos os jogos disponíveis no mundo...", expanded=True) as status:
        for data in datas:
            data_str = data.strftime('%Y-%m-%d')
            st.write(f"📅 Vasculhando dia {data_str}...")
            
            # Buscando TODOS os jogos do dia (sem filtrar por liga específica para garantir resultados)
            url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
            querystring = {"date": data_str}
            
            try:
                response = requests.get(url, headers=headers, params=querystring)
                jogos = response.json().get('response', [])
                
                for item in jogos:
                    # Só pegamos jogos que ainda não começaram
                    if item['fixture']['status']['short'] == 'NS':
                        lista_final.append({
                            "Hora": item['fixture']['date'][11:16],
                            "Liga": item['league']['name'],
                            "País": item['league']['country'],
                            "Jogo": f"{item['teams']['home']['name']} vs {item['teams']['away']['name']}"
                        })
            except Exception as e:
                continue
                
        status.update(label="✅ Varredura Concluída!", state="complete", expanded=False)
    
    return lista_final

# --- INTERFACE ---
if st.button("🚀 INICIAR VARREDURA GLOBAL"):
    resultados = buscar_oportunidades()
    
    if resultados:
        st.write(f"### 📋 {len(resultados)} Jogos encontrados para hoje/amanhã")
        
        # Criando uma tabela para ficar mais fácil de ler muitos jogos
        df = pd.DataFrame(resultados)
        st.dataframe(df, use_container_width=True)
        
        st.info("💡 Dica: Escolha jogos de ligas que você conhece na OneNation.bet")
    else:
        st.warning("A API não retornou jogos. Verifique se sua chave na RapidAPI ainda tem créditos gratuitos (Limite de 100 por dia).")

st.divider()
st.caption("Aviso: Dados via API-Football. Use para análise estatística.")
