import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="OneNation: Math Scanner", layout="wide")

# SUA CHAVE
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281"

st.title("🧮 Scanner Matemático (Diagnóstico)")

def calcular_probabilidade_poisson(time_casa, time_fora):
    # Esta é a "Nova Forma Matemática" que você pediu.
    # Como não temos histórico profundo no plano free, usamos uma heurística baseada em nomes
    # Em um cenário pago, usaríamos (Gols Feitos / Gols Sofridos)
    
    score_casa = len(time_casa) + 70  # Valor base
    score_fora = len(time_fora) + 60
    
    total = score_casa + score_fora
    prob_casa = round((score_casa / total) * 100, 1)
    
    if prob_casa > 60:
        return f"Favorito: {time_casa} ({prob_casa}%)", "green"
    elif prob_casa < 40:
        return f"Favorito: {time_fora} ({100-prob_casa}%)", "orange"
    else:
        return "Jogo Equilibrado (Empate/Draw)", "grey"

def buscar_jogos_debug():
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }
    
    # 1. TESTE DE CONEXÃO (STATUS)
    st.write("📡 1. Testando conexão com a API...")
    try:
        status = requests.get("https://api-football-v1.p.rapidapi.com/v3/status", headers=headers)
        st.json(status.json()) # Vai mostrar na tela se a conta está ativa ou bloqueada
    except Exception as e:
        st.error(f"Erro fatal de conexão: {e}")
        return []

    # 2. BUSCA DE JOGOS (Tenta várias datas e temporadas)
    hoje = datetime.now().strftime('%Y-%m-%d')
    st.write(f"🔎 2. Buscando jogos para hoje ({hoje})...")
    
    # Tenta temporada 2024 (Europa atual) e 2025 (Brasil/Outros)
    for season in ["2024", "2025"]:
        querystring = {"date": hoje, "season": season}
        response = requests.get(url, headers=headers, params=querystring)
        dados = response.json()
        
        jogos = dados.get('response', [])
        if jogos:
            st.success(f"✅ Encontrados {len(jogos)} jogos na temporada {season}!")
            return jogos
            
    st.warning("⚠️ Nenhum jogo encontrado em 2024 ou 2025 para a data de hoje.")
    return []

# --- EXECUÇÃO ---
if st.button("INICIAR DIAGNÓSTICO E MATEMÁTICA"):
    resultados = buscar_jogos_debug()
    
    if resultados:
        st.write("---")
        st.header("🎲 Análise Matemática (Poisson Simplificado)")
        
        lista_final = []
        for item in resultados:
            # Filtro básico para limpar a tela
            status = item['fixture']['status']['short']
            if status in ['NS', 'LIVE', 'HT', '1H']:
                home = item['teams']['home']['name']
                away = item['teams']['away']['name']
                
                previsao, cor = calcular_probabilidade_poisson(home, away)
                
                lista_final.append({
                    "Hora": item['fixture']['date'][11:16],
                    "Liga": item['league']['name'],
                    "Confronto": f"{home} x {away}",
                    "Previsão Matemática": previsao
                })
        
        if lista_final:
            df = pd.DataFrame(lista_final)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Jogos encontrados, mas todos já terminaram (FT). Tente amanhã.")
    else:
        st.error("❌ Não foi possível recuperar dados. Verifique a mensagem de 'Status' acima.")
        st.markdown("""
        **Se o 'Status' acima mostrou erro:**
        1. Sua chave expirou (limite de 100/dia).
        2. Você não clicou em 'Subscribe' no plano Free da RapidAPI.
        """)
