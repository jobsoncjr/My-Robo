import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="OneNation: Scanner Mestre", layout="wide", page_icon="🦁")

# --- SUA CHAVE ---
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281"

st.title("🦁 Scanner OneNation: Modo Agressivo")
st.write("Buscando jogos em todos os campeonatos globais disponíveis...")

def buscar_sem_filtros():
    # Data de HOJE (Dinâmica)
    hoje = datetime.now().strftime('%Y-%m-%d')
    
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    # O SEGREDO: Tiramos o filtro de 'season'. Pedimos apenas a data.
    # Isso força a API a entregar tudo que existe.
    querystring = {"date": hoje}
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        dados = response.json()
        
        # DEBUG: Se der erro na conta, mostramos na tela
        if "errors" in dados and dados["errors"]:
            st.error(f"⚠️ BLOQUEIO DA API: {dados['errors']}")
            return []
            
        lista_jogos = dados.get("response", [])
        return lista_jogos
    except Exception as e:
        st.error(f"Erro de Conexão: {e}")
        return []

# --- BOTÃO E VISUALIZAÇÃO ---
if st.button("🔎 VARRER MERCADO GLOBAL AGORA"):
    with st.spinner('Acessando satélites de dados esportivos...'):
        jogos = buscar_sem_filtros()
        
        if jogos:
            st.success(f"✅ SUCESSO! A API retornou {len(jogos)} jogos brutos.")
            
            # Processamento para mostrar apenas o que interessa
            lista_tratada = []
            for item in jogos:
                status = item['fixture']['status']['short']
                # Filtramos para mostrar jogos que NÃO terminaram (NS = Not Started, LIVE = Ao Vivo)
                if status in ['NS', '1H', '2H', 'HT', 'LIVE']:
                    lista_tratada.append({
                        "Horário": item['fixture']['date'][11:16],
                        "Liga": f"{item['league']['country']} - {item['league']['name']}",
                        "Confronto": f"{item['teams']['home']['name']} x {item['teams']['away']['name']}",
                        "Status": "🔴 AO VIVO" if status in ['1H', '2H', 'LIVE'] else "🟢 Agendado",
                        "Sugestão OneNation": "Over 1.5 Gols" # Estratégia Padrão para Volume
                    })
            
            # Se tivermos jogos filtrados
            if lista_tratada:
                df = pd.DataFrame(lista_tratada)
                # Ordenar por horário
                df = df.sort_values(by="Horário")
                
                # Exibição em Tabela Interativa
                st.dataframe(
                    df, 
                    column_config={
                        "Status": st.column_config.TextColumn(
                            "Status",
                            help="Estado atual da partida",
                            validate="^🔴.*" # Destaca live em vermelho se possível
                        ),
                    },
                    use_container_width=True,
                    hide_index=True
                )
                st.info("👆 Estes são os jogos reais acontecendo ou agendados para hoje. Copie o nome e busque na OneNation.bet")
            else:
                st.warning("A API trouxe dados, mas todos os jogos de hoje já terminaram (FT). Tente amanhã cedo!")
        else:
            st.error("A lista veio vazia. Isso confirma 100% que sua chave RapidAPI ainda não foi aprovada ou atingiu o limite diário.")
            st.markdown("[Clique aqui para verificar sua conta RapidAPI](https://rapidapi.com/developer/dashboard)")

st.divider()
st.caption("OneNation Tech | Data Ref: " + datetime.now().strftime('%d/%m/%Y'))
