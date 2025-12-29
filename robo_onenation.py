import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
import json
import hashlib

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="🎯 OneNation Analyzer Pro",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# SISTEMA DE LOGIN SIMPLES
# =============================================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_login():
    """Sistema de login básico."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.title("🔐 Login - OneNation Analyzer")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            
            if st.button("Entrar", use_container_width=True):
                # Usuários cadastrados (você pode mudar)
                users = {
                    "admin": hash_password("admin123"),
                    "usuario": hash_password("123456")
                }
                
                if username in users and users[username] == hash_password(password):
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos")
        return False
    return True

# =============================================================================
# CONFIGURAÇÃO DAS APIs
# =============================================================================
API_FOOTBALL_KEY = st.secrets.get("API_FOOTBALL_KEY", "")
API_FOOTBALL_HOST = "api-football-v1.p.rapidapi.com"

ODDS_API_KEY = st.secrets.get("ODDS_API_KEY", "")

# =============================================================================
# FUNÇÕES DE API - FUTEBOL
# =============================================================================
def api_football_request(endpoint, params=None):
    """Requisição para API-Football."""
    if not API_FOOTBALL_KEY:
        return None
    
    url = f"https://{API_FOOTBALL_HOST}/v3/{endpoint}"
    headers = {
        "X-RapidAPI-Key": API_FOOTBALL_KEY,
        "X-RapidAPI-Host": API_FOOTBALL_HOST
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", [])
    except Exception as e:
        st.error(f"Erro API Football: {e}")
        return None

def buscar_jogos_futebol(date=None, league=None, live=False):
    """Busca jogos de futebol."""
    params = {}
    
    if live:
        params["live"] = "all"
    elif date:
        params["date"] = date
    
    if league:
        params["league"] = league
    
    return api_football_request("fixtures", params)

def buscar_estatisticas_time(team_id, league_id, season=2024):
    """Busca estatísticas de um time."""
    params = {
        "team": team_id,
        "league": league_id,
        "season": season
    }
    return api_football_request("teams/statistics", params)

def buscar_h2h(team1_id, team2_id, last=10):
    """Busca confrontos diretos."""
    params = {
        "h2h": f"{team1_id}-{team2_id}",
        "last": last
    }
    return api_football_request("fixtures/headtohead", params)

def buscar_odds_jogo(fixture_id):
    """Busca odds de um jogo."""
    params = {"fixture": fixture_id}
    return api_football_request("odds", params)

def buscar_ligas_principais():
    """Retorna as principais ligas para futebol."""
    return [
        {"id": 71, "name": "🇧🇷 Brasileirão Série A", "country": "Brazil"},
        {"id": 72, "name": "🇧🇷 Brasileirão Série B", "country": "Brazil"},
        {"id": 39, "name": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League", "country": "England"},
        {"id": 140, "name": "🇪🇸 La Liga", "country": "Spain"},
        {"id": 135, "name": "🇮🇹 Serie A", "country": "Italy"},
        {"id": 78, "name": "🇩🇪 Bundesliga", "country": "Germany"},
        {"id": 61, "name": "🇫🇷 Ligue 1", "country": "France"},
        {"id": 94, "name": "🇵🇹 Primeira Liga", "country": "Portugal"},
        {"id": 2, "name": "🏆 Champions League", "country": "Europe"},
        {"id": 3, "name": "🏆 Europa League", "country": "Europe"},
        {"id": 13, "name": "🏆 Libertadores", "country": "South America"},
        {"id": 11, "name": "🏆 Copa Sul-Americana", "country": "South America"},
    ]

# =============================================================================
# FUNÇÕES DE ANÁLISE
# =============================================================================
def calcular_probabilidade_poisson(media_gols, gols):
    """Calcula probabilidade usando distribuição de Poisson."""
    import math
    return (math.exp(-media_gols) * (media_gols ** gols)) / math.factorial(gols)

def analisar_partida_futebol(stats_casa, stats_fora, h2h_data=None):
    """
    Analisa uma partida de futebol e retorna probabilidades e sugestões.
    """
    resultado = {
        "prob_casa": 0,
        "prob_empate": 0,
        "prob_fora": 0,
        "media_gols": 0,
        "prob_over_25": 0,
        "prob_btts": 0,
        "prob_mais_35_cartoes": 0,
        "sugestoes": [],
        "confianca": "Baixa"
    }
    
    if not stats_casa or not stats_fora:
        return resultado
    
    # Extrair dados (estrutura da API-Football)
    try:
        # Gols marcados/sofridos por jogo
        gols_casa_marcados = float(stats_casa.get("goals", {}).get("for", {}).get("average", {}).get("home", 0) or 0)
        gols_casa_sofridos = float(stats_casa.get("goals", {}).get("against", {}).get("average", {}).get("home", 0) or 0)
        gols_fora_marcados = float(stats_fora.get("goals", {}).get("for", {}).get("average", {}).get("away", 0) or 0)
        gols_fora_sofridos = float(stats_fora.get("goals", {}).get("against", {}).get("average", {}).get("away", 0) or 0)
        
        # Forma recente (vitórias nos últimos jogos)
        forma_casa = stats_casa.get("form", "")[-5:] if stats_casa.get("form") else ""
        forma_fora = stats_fora.get("form", "")[-5:] if stats_fora.get("form") else ""
        
        vitorias_casa = forma_casa.count("W")
        vitorias_fora = forma_fora.count("W")
        
        # Calcular força de ataque/defesa
        forca_ataque_casa = gols_casa_marcados / 1.5 if gols_casa_marcados else 0.8
        forca_defesa_casa = 1.5 / gols_casa_sofridos if gols_casa_sofridos else 1.0
        forca_ataque_fora = gols_fora_marcados / 1.3 if gols_fora_marcados else 0.7
        forca_defesa_fora = 1.3 / gols_fora_sofridos if gols_fora_sofridos else 1.0
        
        # Expectativa de gols
        exp_gols_casa = forca_ataque_casa * (1 / forca_defesa_fora) * 1.4
        exp_gols_fora = forca_ataque_fora * (1 / forca_defesa_casa) * 1.1
        
        # Probabilidades usando Poisson simplificado
        # Casa vence
        prob_casa = 0
        for gc in range(6):
            for gf in range(gc):
                prob_casa += calcular_probabilidade_poisson(exp_gols_casa, gc) * calcular_probabilidade_poisson(exp_gols_fora, gf)
        
        # Empate
        prob_empate = 0
        for g in range(6):
            prob_empate += calcular_probabilidade_poisson(exp_gols_casa, g) * calcular_probabilidade_poisson(exp_gols_fora, g)
        
        # Fora vence
        prob_fora = 1 - prob_casa - prob_empate
        
        # Ajustar com forma recente
        bonus_forma_casa = (vitorias_casa - 2.5) * 0.03
        bonus_forma_fora = (vitorias_fora - 2.5) * 0.03
        
        prob_casa = max(0.05, min(0.90, prob_casa + bonus_forma_casa))
        prob_fora = max(0.05, min(0.90, prob_fora + bonus_forma_fora))
        prob_empate = 1 - prob_casa - prob_fora
        
        # Over 2.5
        media_total = exp_gols_casa + exp_gols_fora
        prob_over_25 = 0
        for gc in range(10):
            for gf in range(10):
                if gc + gf > 2:
                    prob_over_25 += calcular_probabilidade_poisson(exp_gols_casa, gc) * calcular_probabilidade_poisson(exp_gols_fora, gf)
        
        # BTTS (Ambas marcam)
        prob_casa_marca = 1 - calcular_probabilidade_poisson(exp_gols_casa, 0)
        prob_fora_marca = 1 - calcular_probabilidade_poisson(exp_gols_fora, 0)
        prob_btts = prob_casa_marca * prob_fora_marca
        
        # Cartões (estimativa baseada em média de 4 cartões por jogo)
        prob_mais_35_cartoes = 0.55  # valor médio, idealmente viria da API
        
        resultado = {
            "prob_casa": round(prob_casa * 100, 1),
            "prob_empate": round(prob_empate * 100, 1),
            "prob_fora": round(prob_fora * 100, 1),
            "media_gols": round(media_total, 2),
            "prob_over_25": round(prob_over_25 * 100, 1),
            "prob_btts": round(prob_btts * 100, 1),
            "prob_mais_35_cartoes": round(prob_mais_35_cartoes * 100, 1),
            "exp_gols_casa": round(exp_gols_casa, 2),
            "exp_gols_fora": round(exp_gols_fora, 2),
            "forma_casa": forma_casa,
            "forma_fora": forma_fora,
            "sugestoes": [],
            "confianca": "Média"
        }
        
        # Determinar confiança
        jogos_casa = stats_casa.get("fixtures", {}).get("played", {}).get("total", 0)
        jogos_fora = stats_fora.get("fixtures", {}).get("played", {}).get("total", 0)
        
        if jogos_casa >= 10 and jogos_fora >= 10:
            resultado["confianca"] = "Alta"
        elif jogos_casa >= 5 and jogos_fora >= 5:
            resultado["confianca"] = "Média"
        else:
            resultado["confianca"] = "Baixa"
        
    except Exception as e:
        st.warning(f"Erro ao analisar: {e}")
    
    return resultado

def calcular_odd_justa(probabilidade):
    """Converte probabilidade em odd justa."""
    if probabilidade <= 0:
        return 99.99
    return round(100 / probabilidade, 2)

def calcular_edge(odd_mercado, odd_justa):
    """Calcula o edge (valor) de uma aposta."""
    if odd_justa <= 0:
        return 0
    return round((odd_mercado / odd_justa - 1) * 100, 1)

def gerar_sugestoes(analise, odds_mercado=None):
    """Gera sugestões de apostas baseado na análise."""
    sugestoes = []
    
    # Odds padrão se não fornecidas
    if not odds_mercado:
        odds_mercado = {
            "casa": 2.0,
            "empate": 3.5,
            "fora": 3.5,
            "over_25": 1.9,
            "under_25": 1.9,
            "btts_sim": 1.85,
            "btts_nao": 1.95
        }
    
    # Calcular odds justas
    odd_justa_casa = calcular_odd_justa(analise["prob_casa"])
    odd_justa_empate = calcular_odd_justa(analise["prob_empate"])
    odd_justa_fora = calcular_odd_justa(analise["prob_fora"])
    odd_justa_over = calcular_odd_justa(analise["prob_over_25"])
    odd_justa_btts = calcular_odd_justa(analise["prob_btts"])
    
    # Verificar valor em cada mercado
    mercados = [
        {
            "mercado": "Casa (1)",
            "prob": analise["prob_casa"],
            "odd_justa": odd_justa_casa,
            "odd_mercado": odds_mercado.get("casa", 2.0),
            "tipo": "1X2"
        },
        {
            "mercado": "Empate (X)",
            "prob": analise["prob_empate"],
            "odd_justa": odd_justa_empate,
            "odd_mercado": odds_mercado.get("empate", 3.5),
            "tipo": "1X2"
        },
        {
            "mercado": "Fora (2)",
            "prob": analise["prob_fora"],
            "odd_justa": odd_justa_fora,
            "odd_mercado": odds_mercado.get("fora", 3.5),
            "tipo": "1X2"
        },
        {
            "mercado": "Over 2.5 Gols",
            "prob": analise["prob_over_25"],
            "odd_justa": odd_justa_over,
            "odd_mercado": odds_mercado.get("over_25", 1.9),
            "tipo": "Gols"
        },
        {
            "mercado": "Ambas Marcam (Sim)",
            "prob": analise["prob_btts"],
            "odd_justa": odd_justa_btts,
            "odd_mercado": odds_mercado.get("btts_sim", 1.85),
            "tipo": "BTTS"
        }
    ]
    
    for m in mercados:
        edge = calcular_edge(m["odd_mercado"], m["odd_justa"])
        m["edge"] = edge
        
        if edge > 5:  # Edge mínimo de 5%
            nivel = "🟢 FORTE" if edge > 15 else "🟡 MODERADO" if edge > 10 else "🔵 LEVE"
            sugestoes.append({
                **m,
                "nivel": nivel,
                "recomendacao": f"{nivel} - Edge de {edge}%"
            })
    
    # Ordenar por edge
    sugestoes.sort(key=lambda x: x["edge"], reverse=True)
    
    return sugestoes, mercados

# =============================================================================
# INTERFACE PRINCIPAL
# =============================================================================
def main():
    # Verificar login
    if not check_login():
        return
    
    # Sidebar
    with st.sidebar:
        st.title("🎯 OneNation Analyzer")
        st.write(f"Usuário: **{st.session_state.username}**")
        
        if st.button("🚪 Sair"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.markdown("---")
        
        # Seleção de esporte
        esporte = st.selectbox(
            "⚽ Esporte",
            ["Futebol", "Basquete", "Tênis", "eSports"],
            index=0
        )
        
        st.markdown("---")
        
        # Filtros
        st.subheader("🔍 Filtros")
        
        edge_minimo = st.slider("Edge mínimo (%)", 0, 30, 5)
        
        confianca_minima = st.selectbox(
            "Confiança mínima",
            ["Todas", "Baixa+", "Média+", "Alta"],
            index=1
        )
        
        st.markdown("---")
        
        # Status da API
        st.subheader("📡 Status APIs")
        
        if API_FOOTBALL_KEY:
            st.success("✅ API Football OK")
        else:
            st.error("❌ API Football não configurada")
        
        if ODDS_API_KEY:
            st.success("✅ Odds API OK")
        else:
            st.warning("⚠️ Odds API não configurada")
    
    # Conteúdo principal
    st.title("🎯 OneNation Analyzer Pro")
    st.write("Encontre apostas de valor com análise estatística avançada")
    
    # Tabs principais
    tab_jogos, tab_analise, tab_combinadas, tab_historico = st.tabs([
        "📅 Jogos do Dia",
        "🔬 Análise Manual",
        "🎰 Apostas Combinadas",
        "📊 Histórico"
    ])
    
    # ==========================================================================
    # TAB 1: JOGOS DO DIA
    # ==========================================================================
    with tab_jogos:
        st.header("📅 Jogos de Hoje")
        
        if esporte == "Futebol":
            col1, col2 = st.columns([2, 1])
            
            with col1:
                ligas = buscar_ligas_principais()
                liga_selecionada = st.selectbox(
                    "Selecione a
