import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Scanner Real OneNation", layout="wide")

# SUA CHAVE (Funcional)
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281"

st.title("🤖 Scanner de Jogos Reais")
st.write("Buscando dados ao vivo das APIs...")

# --- SELETOR DE DATA ---
data_escolhida = st.date_input("Escolha a data para analisar:", datetime.now())
data_formatada = data_escolhida.strftime('%Y-%m-%d')

def buscar_jogos_reais():
    """Busca jogos reais da API-Football"""
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    querystring = {"date": data_formatada}
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        # Verifica se há erro (como Pending Approval)
        if 'errors' in data and data['errors']:
            st.error(f"❌ Erro da API: {data['errors']}")
            return None
            
        jogos = data.get('response', [])
        
        if not jogos:
            return []
        
        lista_jogos = []
        for jogo in jogos:
            # Filtra apenas jogos que não começaram ainda
            status = jogo['fixture']['status']['short']
            if status in ['NS', 'TBD']:  # Not Started ou To Be Defined
                lista_jogos.append({
                    "Hora": jogo['fixture']['date'][11:16],
                    "País": jogo['league']['country'],
                    "Liga": jogo['league']['name'],
                    "Jogo": f"{jogo['teams']['home']['name']} vs {jogo['teams']['away']['name']}",
                    "ID": jogo['fixture']['id']
                })
        
        return lista_jogos
        
    except Exception as e:
        st.error(f"❌ Erro de conexão: {str(e)}")
        return None

# --- BOTÃO DE BUSCA ---
if st.button("🔍 BUSCAR JOGOS REAIS"):
    with st.spinner(f'Buscando jogos reais para {data_formatada}...'):
        resultados = buscar_jogos_reais()
        
        if resultados is None:
            st.warning("⚠️ **SUA API ESTÁ COM PENDING APPROVAL**")
            st.info("""
            **O que fazer:**
            1. Vá em: https://rapidapi.com/api-sports/api/api-football
            2. Verifique se o status mudou de "Pending" para "Active"
            3. Se continuar pendente, aguarde algumas horas (aprovação manual)
            
            **OU**
            
            Crie uma conta nova no RapidAPI com outro email e pegue uma chave nova.
            """)
            
        elif len(resultados) == 0:
            st.warning(f"Não há jogos agendados para {data_formatada}")
            st.info("Tente selecionar outra data (amanhã ou próximos dias)")
            
        else:
            st.success(f"✅ Encontrados {len(resultados)} jogos!")
            
            # Criar tabela organizada
            df = pd.DataFrame(resultados)
            
            # Remover coluna ID da exibição
            df_display = df.drop(columns=['ID'])
            
            # Exibir em formato de tabela
            st.dataframe(df_display, use_container_width=True)
            
            # Exibir em cartões também
            st.subheader("📋 Detalhes dos Jogos")
            for _, row in df.iterrows():
                with st.expander(f"⚽ {row['Jogo']}"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Horário", row['Hora'])
                    with col2:
                        st.metric("País", row['País'])
                    with col3:
                        st.metric("Liga", row['Liga'])
                    
                    st.info("💡 Busque este jogo na OneNation.bet e compare as odds")

st.divider()

# Informações da API
with st.expander("ℹ️ Status da Conexão"):
    st.write(f"**API Key:** {API_KEY[:10]}...")
    st.write(f"**Data selecionada:** {data_formatada}")
    st.write("**Endpoint:** API-Football v3")
