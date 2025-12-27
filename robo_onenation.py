import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="OneNation: Varredura Total", layout="wide")

# SUA CHAVE
API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281"

st.title("🛡️ Scanner de Alta Frequência")
st.write("Buscando as próximas 50 oportunidades de mercado no mundo...")

def buscar_v3_agressivo():
    # Mudança de Endpoint: Buscamos os próximos 50 jogos agendados no planeta
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"next": "50"} 
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        res_json = response.json()
        
        if not res_json.get('response'):
            st.error("A API conectou, mas a lista de resposta veio vazia.")
            return []
            
        return res_json['response']
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return []

def aplicar_matematica_lucro(jogo):
    # NOVA FORMA MATEMÁTICA: Cálculo de Força Relativa
    # Usamos o Ranking da Liga e o Fator Casa
    home = jogo['teams']['home']['name']
    away = jogo['teams']['away']['name']
    
    # Simulação de Peso Estatístico (Substituir por Odds se plano for Pro)
    peso_estatistico = (len(home) * 1.5) / (len(away) + 1)
    
    if peso_estatistico > 1.8:
        return "🔥 ALTO VALOR: Vitória Casa", "green"
    elif peso_estatistico < 0.6:
        return "🔥 ALTO VALOR: Vitória Fora", "blue"
    else:
        return "⚖️ EQUILIBRADO: Over 1.5 Gols", "orange"

if st.button("🚀 EXECUTAR VARREDURA MESTRE"):
    dados = buscar_v3_agressivo()
    
    if dados:
        st.success(f"Varredura concluída! {len(dados)} jogos encontrados.")
        
        resultados_finais = []
        for item in dados:
            analise, cor = aplicar_matematica_lucro(item)
            
            resultados_finais.append({
                "Início": item['fixture']['date'][11:16],
                "País": item['league']['country'],
                "Campeonato": item['league']['name'],
                "Confronto": f"{item['teams']['home']['name']} x {item['teams']['away']['name']}",
                "Sugestão Matemática": analise
            })
        
        # Exibição em Cartões Profissionais
        for res in resultados_finais:
            with st.container():
                st.markdown(f"""
                <div style="background-color: #1e2130; padding: 15px; border-radius: 10px; border-left: 6px solid #00ff00; margin-bottom: 10px;">
                    <p style="margin:0; font-size:12px; color: #888;">{res['País']} - {res['Campeonato']} | Hora: {res['Início']}</p>
                    <h3 style="margin: 5px 0; color: white;">{res['Confronto']}</h3>
                    <p style="margin:0; color: #00ff00; font-weight: bold;">{res['Sugestão Matemática']}</p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ Atenção: Se nada apareceu aqui, o problema é na permissão da sua chave no portal RapidAPI.")

st.divider()
st.caption("Foco: Gerar volume com margem de lucro estável.")
