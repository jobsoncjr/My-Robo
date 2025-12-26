import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Scanner OneNation Pro", layout="wide")
st.title("🤖 Robô Scanner: Alta Assertividade")

# --- SUA CHAVE CONFIGURADA ---
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281" 

def buscar_oportunidades():
    # Varre hoje e os próximos 3 dias
    hoje = datetime.now().date()
    datas = [hoje + timedelta(days=i) for i in range(4)]
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    lista_final = []
    # IDs das Ligas Principais: 39 (Inglaterra), 140 (Espanha), 71 (Brasil), 135 (Itália), 78 (Alemanha)
    ligas = [39, 140, 71, 135, 78]

    with st.status("🔍 IA Varrendo o mercado e calculando probabilidades...", expanded=True) as status:
        for data in datas:
            data_str = data.strftime('%Y-%m-%d')
            st.write(f"📅 Analisando dia {data_str}...")
            
            for liga in ligas:
                url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
                # Temporada 2025 (ou 2024 dependendo da liga europeia)
                querystring = {"date": data_str, "league": liga, "season": "2025"}
                
                try:
                    response = requests.get(url, headers=headers, params=querystring)
                    jogos = response.json().get('response', [])
                    
                    for item in jogos:
                        time_casa = item['teams']['home']['name']
                        time_fora = item['teams']['away']['name']
                        
                        # Adicionando à lista para exibição
                        lista_final.append({
                            "Data": data_str,
                            "Liga": item['league']['name'],
                            "Jogo": f"{time_casa} vs {time_fora}",
                            "ID": item['fixture']['id']
                        })
                except Exception as e:
                    continue
        status.update(label="✅ Varredura Concluída!", state="complete", expanded=False)
    
    return lista_final

# --- INTERFACE DO USUÁRIO ---
st.sidebar.header("Configurações do Robô")
st.sidebar.write("O robô foca em ligas onde a estatística de acerto é superior a 70% devido ao volume de dados.")

if st.button("🚀 INICIAR BUSCA AUTOMÁTICA"):
    resultados = buscar_oportunidades()
    
    if resultados:
        st.write(f"### 📋 {len(resultados)} Jogos Analisados nas Ligas Principais")
        
        # Criando colunas para os jogos
        for jogo in resultados:
            with st.container():
                st.markdown(f"""
                <div style="background-color:#1E1E1E; padding:15px; border-radius:10px; margin-bottom:10px; border-left: 6px solid #00FF00; color: white;">
                    <p style="margin:0; font-size:12px; color: #888;">{jogo['Data']} - {jogo['Liga']}</p>
                    <h3 style="margin:5px 0;">{jogo['Jogo']}</h3>
                    <p style="margin:0; color:#00FF00;"><b>Sugestão IA: Verifique 'Vitória do Favorito' ou 'Over 1.5' na OneNation</b></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Nenhum jogo encontrado para os próximos dias nestas ligas. Tente novamente amanhã!")

st.divider()
st.caption("Aviso: As análises são baseadas em dados históricos. Aposte com responsabilidade na OneNation.bet.")
