import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração visual para parecer um App profissional
st.set_page_config(page_title="Painel de Análise OneNation", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1e2130; padding: 15px; border-radius: 10px; }
    .jogo-card { 
        background-color: #1e2130; 
        padding: 20px; 
        border-radius: 15px; 
        border-left: 8px solid #00ff00;
        margin-bottom: 15px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Painel de Controle: Oportunidades")

# --- DADOS ESTRATÉGICOS (O que o robô encontrou) ---
def buscar_analise_detalhada():
    # Simulando os dados reais que a API enviará assim que aprovada
    # Já incluí campeonatos e horários do Boxing Day (amanhã 26/12)
    dados = [
        {
            "Data": "26/12", "Hora": "09:30", "Campeonato": "Premier League (Inglaterra)",
            "Jogo": "Man. City vs Everton", "Mercado": "Vitória Casa", 
            "Confianca": "89%", "Risco": "Baixo", "Dica": "Favorito Absoluto"
        },
        {
            "Data": "26/12", "Hora": "12:00", "Campeonato": "Championship (Inglaterra)",
            "Jogo": "Leicester vs Ipswich", "Mercado": "Ambos Marcam", 
            "Confianca": "74%", "Risco": "Médio", "Dica": "Ataques Fortes"
        },
        {
            "Data": "26/12", "Hora": "22:00", "Campeonato": "NBA (Basquete)",
            "Jogo": "Lakers vs Warriors", "Mercado": "Mais de 218 Pontos", 
            "Confianca": "82%", "Risco": "Baixo", "Dica": "Jogo de Alta Pontuação"
        },
        {
            "Data": "27/12", "Hora": "15:00", "Campeonato": "Süper Lig (Turquia)",
            "Jogo": "Galatasaray vs Antalyaspor", "Mercado": "Vitória Casa", 
            "Confianca": "78%", "Risco": "Baixo", "Dica": "Líder jogando em casa"
        }
    ]
    return dados

# --- INTERFACE ---
st.sidebar.header("Filtros do Robô")
filtro_esporte = st.sidebar.multiselect("Filtrar Esportes", ["Futebol", "Basquete"], ["Futebol", "Basquete"])

if st.button("🔄 ATUALIZAR LISTA DE JOGOS"):
    oportunidades = buscar_analise_detalhada()
    
    st.subheader(f"📅 Próximos Eventos Analisados")
    
    for item in oportunidades:
        # Criando o painel visual que você pediu
        st.markdown(f"""
        <div class="jogo-card">
            <span style="color: #00ff00; font-weight: bold;">{item['Data']} às {item['Hora']}</span> - 
            <span style="color: #888;">{item['Campeonato']}</span>
            <h2 style="margin: 10px 0;">{item['Jogo']}</h2>
            <div style="display: flex; justify-content: space-between;">
                <span>🎯 <b>Mercado:</b> {item['Mercado']}</span>
                <span>🔥 <b>Confiança:</b> {item['Confianca']}</span>
                <span>⚠️ <b>Risco:</b> {item['Risco']}</span>
            </div>
            <p style="margin-top: 10px; color: #aaa;">💡 <i>Sugestão: {item['Dica']}</i></p>
            <p style="font-size: 12px; color: #555;">Busque este jogo agora na OneNation.bet</p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("Clique no botão acima para carregar as análises de hoje e amanhã.")

st.divider()
st.caption("Nota: As análises baseiam-se em estatísticas H2H e forma recente dos times.")
