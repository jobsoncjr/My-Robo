import streamlit as st
import pandas as pd
import requests
import json

st.set_page_config(page_title="Analista NCAA – Conferences", layout="wide")

st.title("🏈 Analista NCAA – Futebol Americano Universitário")
st.write("Painel para explorar Conferências usando sua API Key.")

# --- CONFIGURAÇÃO DA API ---
# Em produção, use st.secrets para esconder a chave
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281" 

# O JSON que você forneceu (para garantir que funcione offline para teste)
# Quando colocar a URL real, você pode apagar este bloco ou usar como fallback
MOCK_JSON = """
{
  "conferences": [
    {"conference_id": 91, "division_id": 1, "sport_id": 1, "name": "Atlantic Coast Conference"},
    {"conference_id": 731, "division_id": 1, "sport_id": 1, "name": "Big 12 Conference"},
    {"conference_id": 88, "division_id": 1, "sport_id": 1, "name": "Big Ten Conference"},
    {"conference_id": 766, "sport_id": 1, "name": "SEC - East"},
    {"conference_id": 760, "sport_id": 1, "name": "SEC - West"},
    {"conference_id": 86, "division_id": 1, "sport_id": 1, "name": "Southeastern Conference"},
    {"conference_id": 85, "division_id": 1, "sport_id": 1, "name": "Pac-12 Conference"},
    {"conference_id": 93, "division_id": 1, "sport_id": 1, "name": "Conference USA"},
    {"conference_id": 84, "division_id": 1, "sport_id": 1, "name": "Mid-American Conference"},
    {"conference_id": 83, "division_id": 1, "sport_id": 1, "name": "Mountain West Conference"},
    {"conference_id": 139, "division_id": 1, "sport_id": 1, "name": "FBS Independents"},
    {"conference_id": 740, "division_id": 4, "sport_id": 1, "name": "Big Sky Conference"},
    {"conference_id": 81, "division_id": 4, "sport_id": 1, "name": "Missouri Valley Football Conference"},
    {"conference_id": 743, "division_id": 4, "sport_id": 1, "name": "Ivy League"},
    {"conference_id": 72, "division_id": 4, "sport_id": 1, "name": "Southland Conference"},
    {"conference_id": 42, "division_id": 1, "sport_id": 1, "name": "Sun Belt Conference"},
    {"conference_id": 60, "sport_id": 1, "name": "NCAA Football"}
  ]
}
"""

st.sidebar.header("⚙️ Configuração")

# Checkbox para alternar entre modo "API Real" e "Dados de Exemplo"
usar_api_real = st.sidebar.checkbox("Usar API Real (URL Externa)", value=False)

url_api = st.sidebar.text_input(
    "Endpoint da API (Ex: Odds API)", 
    "https://odds.p.rapidapi.com/v4/sports/americanfootball_ncaaf/conferences"
)

st.markdown("---")

# --- LÓGICA DE DADOS ---

data_json = None
source = "Dados Exemplo (JSON Manual)"

if usar_api_real:
    try:
        headers = {
            "x-rapidapi-key": API_KEY,
            "x-rapidapi-host": "odds.p.rapidapi.com" # Ajuste o host se necessário
        }
        response = requests.get(url_api, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data_json = response.json()
            source = "API (Dados Ao Vivo)"
            st.sidebar.success(f"✅ Conectado! Status: {response.status_code}")
        else:
            st.sidebar.error(f"❌ Erro na API: {response.status_code}")
            st.error("Falha ao buscar dados da API. Usando dados de exemplo.")
            data_json = json.loads(MOCK_JSON)
    except Exception as e:
        st.sidebar.error(f"Erro de conexão: {e}")
        st.error("Não foi possível conectar. Usando dados de exemplo.")
        data_json = json.loads(MOCK_JSON)
else:
    # Carrega o JSON manual que você mandou
    try:
        # Tenta carregar o JSON completo que você colou no prompt (simulado aqui pela string MOCK_JSON)
        # Se você tiver o arquivo local, pode usar json.load(open('data.json'))
        data_json = json.loads(MOCK_JSON)
    except:
        st.error("Erro ao carregar dados de exemplo.")

# --- PROCESSAMENTO ---

if data_json and "conferences" in data_json:
    df_conferences = pd.DataFrame(data_json["conferences"])
    
    # Tratamento de divisões (muitos tem 'division_id' nulo no JSON original, preenchemos com 'Geral')
    df_conferences['division_id'] = df_conferences['division_id'].fillna(0).astype(int)
    
    # Mapeamento de nomes de divisões para ficar mais legível
    mapa_divisoes = {
        1: "FBS (Divisão I-A)",
        4: "FCS (Divisão I-AA)",
        5: "Divisão II",
        6: "Divisão III",
        0: "Geral / Outros"
    }
    df_conferences['Nome_Divisao'] = df_conferences['division_id'].map(mapa_divisoes)

    st.header(f"📂 Lista de Conferências ({source})")

    # Filtros
    col1, col2 = st.columns(2)
    
    with col1:
        divisao_selecionada = st.multiselect(
            "Filtrar por Divisão:", 
            options=df_conferences['Nome_Divisao'].unique(), 
            default=["FBS (Divisão I-A)"]
        )
    
    # Aplicar filtro
    if divisao_selecionada:
        df_filtrado = df_conferences[df_conferences['Nome_Divisao'].isin(divisao_selecionada)]
    else:
        df_filtrado = df_conferences

    st.dataframe(
        df_filtrado[['name', 'Nome_Divisao', 'conference_id']], 
        use_container_width=True,
        column_config={
            "name": st.column_config.TextColumn("Nome da Conferência"),
            "Nome_Divisao": st.column_config.TextColumn("Divisão"),
            "conference_id": st.column_config.NumberColumn("ID na API")
        }
    )

    st.markdown("---")
    st.subheader("🎯 Próximo Passo: Análise de Jogos")
    
    st.info("👆 Agora que temos as conferências, o próximo passo seria usar o ID da conferência para buscar os **jogos (odds)** de hoje.")
    
    # Exemplo visual de como seria a seleção
    conferencia_escolhida = st.selectbox("Selecione uma conferência para simular a busca de odds:", options=df_filtrado['name'].tolist())
    
    if st.button("Buscar Jogos (Simulação)"):
        st.write(f"Você escolheu: **{conferencia_escolhida}**")
        st.write("Aqui entraria a chamada para o endpoint de odds usando o ID da conferência.")

else:
    st.error("Nenhum dado de conferência encontrado para exibir.")
