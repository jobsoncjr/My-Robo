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
                    "Selecione a Liga",
                    options=["Todas"] + [l["name"] for l in ligas]
                )
            
            with col2:
                data_jogo = st.date_input("Data", datetime.today())
            
            if st.button("🔍 Buscar Jogos", use_container_width=True):
                with st.spinner("Buscando jogos..."):
                    # Determinar ID da liga
                    league_id = None
                    if liga_selecionada != "Todas":
                        for l in ligas:
                            if l["name"] == liga_selecionada:
                                league_id = l["id"]
                                break
                    
                    # Buscar jogos
                    jogos = buscar_jogos_futebol(
                        date=data_jogo.strftime("%Y-%m-%d"),
                        league=league_id
                    )
                    
                    if jogos:
                        st.success(f"✅ {len(jogos)} jogos encontrados!")
                        
                        # Armazenar para análise
                        if 'jogos_dia' not in st.session_state:
                            st.session_state.jogos_dia = []
                        st.session_state.jogos_dia = jogos
                        
                        # Mostrar jogos
                        for jogo in jogos[:20]:  # Limitar a 20 jogos
                            fixture = jogo.get("fixture", {})
                            teams = jogo.get("teams", {})
                            league = jogo.get("league", {})
                            
                            time_casa = teams.get("home", {}).get("name", "?")
                            time_fora = teams.get("away", {}).get("name", "?")
                            horario = fixture.get("date", "")[:16].replace("T", " ")
                            liga_nome = league.get("name", "")
                            
                            with st.expander(f"⚽ {time_casa} vs {time_fora} | {horario}"):
                                st.write(f"**Liga:** {liga_nome}")
                                st.write(f"**Horário:** {horario}")
                                
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.write(f"**{time_casa}** (Casa)")
                                with col_b:
                                    st.write(f"**{time_fora}** (Fora)")
                                
                                if st.button(f"📊 Analisar", key=f"btn_{fixture.get('id')}"):
                                    st.info("Use a aba 'Análise Manual' para análise detalhada")
                    else:
                        st.warning("Nenhum jogo encontrado para esta data/liga")
                        st.info("💡 Verifique se a API está configurada corretamente")
        
        else:
            st.info(f"🚧 Módulo de {esporte} em desenvolvimento...")
    
    # ==========================================================================
    # TAB 2: ANÁLISE MANUAL
    # ==========================================================================
    with tab_analise:
        st.header("🔬 Análise Manual de Partida")
        
        st.write("Insira os dados manualmente para análise (funciona sem API)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏠 Time da Casa")
            time_casa_nome = st.text_input("Nome do Time", "Time Casa", key="tc_nome")
            jogos_casa = st.number_input("Jogos na temporada", 1, 50, 15, key="tc_jogos")
            vitorias_casa = st.number_input("Vitórias", 0, 50, 8, key="tc_vit")
            empates_casa = st.number_input("Empates", 0, 50, 4, key="tc_emp")
            derrotas_casa = st.number_input("Derrotas", 0, 50, 3, key="tc_der")
            gols_marcados_casa = st.number_input("Gols Marcados", 0, 200, 22, key="tc_gm")
            gols_sofridos_casa = st.number_input("Gols Sofridos", 0, 200, 12, key="tc_gs")
            forma_casa_input = st.text_input("Forma (últimos 5: W/D/L)", "WWDWL", key="tc_forma")
        
        with col2:
            st.subheader("✈️ Time Visitante")
            time_fora_nome = st.text_input("Nome do Time", "Time Fora", key="tf_nome")
            jogos_fora = st.number_input("Jogos na temporada", 1, 50, 15, key="tf_jogos")
            vitorias_fora = st.number_input("Vitórias", 0, 50, 5, key="tf_vit")
            empates_fora = st.number_input("Empates", 0, 50, 5, key="tf_emp")
            derrotas_fora = st.number_input("Derrotas", 0, 50, 5, key="tf_der")
            gols_marcados_fora = st.number_input("Gols Marcados", 0, 200, 16, key="tf_gm")
            gols_sofridos_fora = st.number_input("Gols Sofridos", 0, 200, 18, key="tf_gs")
            forma_fora_input = st.text_input("Forma (últimos 5: W/D/L)", "LDWDW", key="tf_forma")
        
        st.markdown("---")
        st.subheader("💰 Odds da OneNation (opcional)")
        
        col_o1, col_o2, col_o3, col_o4, col_o5 = st.columns(5)
        
        with col_o1:
            odd_casa_input = st.number_input("Casa (1)", 1.01, 50.0, 1.75, key="odd_1")
        with col_o2:
            odd_empate_input = st.number_input("Empate (X)", 1.01, 50.0, 3.60, key="odd_x")
        with col_o3:
            odd_fora_input = st.number_input("Fora (2)", 1.01, 50.0, 4.50, key="odd_2")
        with col_o4:
            odd_over_input = st.number_input("Over 2.5", 1.01, 50.0, 2.00, key="odd_ov")
        with col_o5:
            odd_btts_input = st.number_input("BTTS Sim", 1.01, 50.0, 1.90, key="odd_btts")
        
        if st.button("🚀 ANALISAR PARTIDA", use_container_width=True, type="primary"):
            # Construir dados no formato esperado
            media_gols_casa = gols_marcados_casa / jogos_casa if jogos_casa > 0 else 0
            media_gols_sofridos_casa = gols_sofridos_casa / jogos_casa if jogos_casa > 0 else 0
            media_gols_fora = gols_marcados_fora / jogos_fora if jogos_fora > 0 else 0
            media_gols_sofridos_fora = gols_sofridos_fora / jogos_fora if jogos_fora > 0 else 0
            
            stats_casa = {
                "goals": {
                    "for": {"average": {"home": media_gols_casa, "total": media_gols_casa}},
                    "against": {"average": {"home": media_gols_sofridos_casa, "total": media_gols_sofridos_casa}}
                },
                "form": forma_casa_input.upper(),
                "fixtures": {"played": {"total": jogos_casa}}
            }
            
            stats_fora = {
                "goals": {
                    "for": {"average": {"away": media_gols_fora, "total": media_gols_fora}},
                    "against": {"average": {"away": media_gols_sofridos_fora, "total": media_gols_sofridos_fora}}
                },
                "form": forma_fora_input.upper(),
                "fixtures": {"played": {"total": jogos_fora}}
            }
            
            # Analisar
            analise = analisar_partida_futebol(stats_casa, stats_fora)
            
            # Odds do mercado
            odds_mercado = {
                "casa": odd_casa_input,
                "empate": odd_empate_input,
                "fora": odd_fora_input,
                "over_25": odd_over_input,
                "btts_sim": odd_btts_input
            }
            
            sugestoes, mercados = gerar_sugestoes(analise, odds_mercado)
            
            # Mostrar resultados
            st.markdown("---")
            st.header(f"📊 Resultado: {time_casa_nome} vs {time_fora_nome}")
            
            # Probabilidades
            col_p1, col_p2, col_p3 = st.columns(3)
            
            with col_p1:
                st.metric("🏠 Casa", f"{analise['prob_casa']}%", 
                         f"Odd Justa: {calcular_odd_justa(analise['prob_casa'])}")
            with col_p2:
                st.metric("🤝 Empate", f"{analise['prob_empate']}%",
                         f"Odd Justa: {calcular_odd_justa(analise['prob_empate'])}")
            with col_p3:
                st.metric("✈️ Fora", f"{analise['prob_fora']}%",
                         f"Odd Justa: {calcular_odd_justa(analise['prob_fora'])}")
            
            st.markdown("---")
            
            # Outros mercados
            col_m1, col_m2, col_m3 = st.columns(3)
            
            with col_m1:
                st.metric("⚽ Média Gols Esperada", f"{analise['media_gols']}")
            with col_m2:
                st.metric("📈 Over 2.5", f"{analise['prob_over_25']}%")
            with col_m3:
                st.metric("🎯 Ambas Marcam", f"{analise['prob_btts']}%")
            
            st.markdown("---")
            
            # Tabela completa
            st.subheader("📋 Análise de Valor por Mercado")
            
            df_mercados = pd.DataFrame(mercados)
            df_mercados.columns = ["Mercado", "Prob %", "Odd Justa", "Odd OneNation", "Tipo", "Edge %"]
            df_mercados = df_mercados[["Mercado", "Prob %", "Odd Justa", "Odd OneNation", "Edge %", "Tipo"]]
            
            # Colorir edges
            def colorir_edge(val):
                if val > 15:
                    return 'background-color: #28a745; color: white'
                elif val > 10:
                    return 'background-color: #ffc107; color: black'
                elif val > 5:
                    return 'background-color: #17a2b8; color: white'
                elif val > 0:
                    return 'background-color: #6c757d; color: white'
                else:
                    return 'background-color: #dc3545; color: white'
            
            st.dataframe(
                df_mercados.style.applymap(colorir_edge, subset=['Edge %']),
                use_container_width=True
            )
            
            # Sugestões
            st.markdown("---")
            st.subheader("🎯 SUGESTÕES DE APOSTA")
            
            if sugestoes:
                for s in sugestoes:
                    if s["edge"] > edge_minimo:
                        cor = "green" if s["edge"] > 15 else "orange" if s["edge"] > 10 else "blue"
                        st.markdown(f"""
                        <div style="padding: 15px; border-radius: 10px; border-left: 5px solid {cor}; background-color: #f8f9fa; margin: 10px 0;">
                            <h4>{s['nivel']} - {s['mercado']}</h4>
                            <p><b>Probabilidade:</b> {s['prob']}% | <b>Odd Justa:</b> {s['odd_justa']} | <b>Odd Mercado:</b> {s['odd_mercado']}</p>
                            <p><b>Edge:</b> +{s['edge']}%</p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ Nenhuma aposta com edge acima de {edge_minimo}% encontrada")
            
            # Confiança
            st.info(f"📊 **Nível de Confiança:** {analise['confianca']}")
    
    # ==========================================================================
    # TAB 3: APOSTAS COMBINADAS
    # ==========================================================================
    with tab_combinadas:
        st.header("🎰 Gerador de Apostas Combinadas")
        
        st.write("Monte combinações com diferentes níveis de risco/retorno")
        
        col1, col2 = st.columns(2)
        
        with col1:
            num_selecoes = st.slider("Número de seleções", 2, 10, 3)
            tipo_combinada = st.selectbox(
                "Perfil de Risco",
                ["🟢 Conservador (odds baixas, mais seguro)",
                 "🟡 Moderado (odds médias, equilibrado)",
                 "🔴 Agressivo (odds altas, mais arriscado)"]
            )
        
        with col2:
            valor_aposta = st.number_input("Valor da Aposta (R$)", 1.0, 10000.0, 10.0)
        
        st.markdown("---")
        st.subheader("Adicionar Seleções")
        
        # Lista de seleções
        if 'selecoes_combinada' not in st.session_state:
            st.session_state.selecoes_combinada = []
        
        col_add1, col_add2, col_add3 = st.columns([2, 2, 1])
        
        with col_add1:
            nome_selecao = st.text_input("Jogo/Seleção", "Time A vs Time B - Casa")
        with col_add2:
            odd_selecao = st.number_input("Odd", 1.01, 100.0, 1.50, key="odd_sel")
        with col_add3:
            st.write("")
            st.write("")
            if st.button("➕ Adicionar"):
                st.session_state.selecoes_combinada.append({
                    "nome": nome_selecao,
                    "odd": odd_selecao
                })
        
        # Mostrar seleções
        if st.session_state.selecoes_combinada:
            st.subheader("📋 Suas Seleções")
            
            odd_total = 1.0
            for i, sel in enumerate(st.session_state.selecoes_combinada):
                col_s1, col_s2, col_s3 = st.columns([3, 1, 1])
                with col_s1:
                    st.write(f"**{i+1}.** {sel['nome']}")
                with col_s2:
                    st.write(f"Odd: **{sel['odd']}**")
                with col_s3:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.selecoes_combinada.pop(i)
                        st.rerun()
                
                odd_total *= sel['odd']
            
            st.markdown("---")
            
            # Resumo
            retorno_potencial = valor_aposta * odd_total
            
            col_r1, col_r2, col_r3 = st.columns(3)
            with col_r1:
                st.metric("Odd Total", f"{odd_total:.2f}")
            with col_r2:
                st.metric("Valor Apostado", f"R$ {valor_aposta:.2f}")
            with col_r3:
                st.metric("Retorno Potencial", f"R$ {retorno_potencial:.2f}")
            
            if st.button("🗑️ Limpar Todas", use_container_width=True):
                st.session_state.selecoes_combinada = []
                st.rerun()
    
    # ==========================================================================
    # TAB 4: HISTÓRICO
    # ==========================================================================
    with tab_historico:
        st.header("📊 Histórico de Sugestões")
        
        st.info("🚧 Funcionalidade em desenvolvimento - Em breve você poderá salvar e acompanhar suas apostas!")
        
        # Placeholder para histórico
        st.write("Funcionalidades planejadas:")
        st.write("- ✅ Salvar sugestões do dia")
        st.write("- ✅ Marcar resultado (green/red)")
        st.write("- ✅ Estatísticas de acerto")
        st.write("- ✅ Gráficos de desempenho")
        st.write("- ✅ ROI por tipo de aposta")

# =============================================================================
# EXECUTAR APP
# =============================================================================
if __name__ == "__main__":
    main()
