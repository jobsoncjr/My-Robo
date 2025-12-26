import streamlit as st
import requests
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Scanner Simples OneNation", layout="wide")

API_KEY = "3779e7d05fmshefa7f914e6ddcbdp16afecjsn04b2f826e281"

st.title("💰 Scanner de Valor Simplificado")
st.write("Matemática leve, lucro consistente.")

# --- CONFIGURAÇÕES ---
st.sidebar.header("⚙️ Suas Preferências")
odd_minima = st.sidebar.slider("Odd Mínima Aceitável", 1.30, 3.00, 1.50)
odd_maxima = st.sidebar.slider("Odd Máxima Aceitável", 1.50, 5.00, 2.50)

data_escolhida = st.date_input("Data para analisar:", datetime.now())
data_formatada = data_escolhida.strftime('%Y-%m-%d')

def calcular_valor_simples(odd_casa, odd_fora, odd_empate):
    """
    Matemática Simples de Value Betting
    Converte odds em probabilidades implícitas
    """
    # A casa de apostas diz que a probabilidade é:
    prob_casa_casa = 100 / odd_casa
    prob_fora_casa = 100 / odd_fora
    prob_empate_casa = 100 / odd_empate
    
    # Total sempre é > 100% (é a margem da casa)
    total = prob_casa_casa + prob_fora_casa + prob_empate_casa
    margem_casa = total - 100
    
    # Nossa estimativa simples (removendo a margem)
    prob_real_casa = (prob_casa_casa / total) * 100
    prob_real_fora = (prob_fora_casa / total) * 100
    
    # Cálculo de Valor Esperado SIMPLIFICADO
    # Se a probabilidade real × odd > 100, há valor
    valor_casa = (prob_real_casa / 100) * odd_casa
    valor_fora = (prob_real_fora / 100) * odd_fora
    
    return {
        "prob_casa": round(prob_real_casa, 1),
        "prob_fora": round(prob_real_fora, 1),
        "valor_casa": round(valor_casa, 2),
        "valor_fora": round(valor_fora, 2),
        "margem": round(margem_casa, 2)
    }

def buscar_jogos_com_odds():
    """Busca jogos reais com odds"""
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    
    querystring = {"date": data_formatada}
    
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "api-football-v1.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json()
        
        if 'errors' in data and data['errors']:
            return None, "API com Pending Approval"
            
        jogos = data.get('response', [])
        
        if not jogos:
            return [], "Sem jogos para esta data"
        
        # Buscar odds para cada jogo
        jogos_analisados = []
        
        for jogo in jogos[:10]:  # Limita a 10 para não sobrecarregar
            fixture_id = jogo['fixture']['id']
            
            # Buscar odds do jogo
            url_odds = "https://api-football-v1.p.rapidapi.com/v3/odds"
            querystring_odds = {"fixture": fixture_id}
            
            try:
                response_odds = requests.get(url_odds, headers=headers, params=querystring_odds)
                odds_data = response_odds.json().get('response', [])
                
                if odds_data and len(odds_data) > 0:
                    # Pegar as odds da primeira casa (geralmente Bet365)
                    bookmaker = odds_data[0].get('bookmakers', [])
                    if bookmaker:
                        bets = bookmaker[0].get('bets', [])
                        # Procurar pelo mercado "Match Winner"
                        for bet in bets:
                            if bet['name'] == 'Match Winner':
                                values = bet['values']
                                odd_casa = float(values[0]['odd'])
                                odd_empate = float(values[1]['odd'])
                                odd_fora = float(values[2]['odd'])
                                
                                # Aplicar nossa matemática simples
                                analise = calcular_valor_simples(odd_casa, odd_fora, odd_empate)
                                
                                # Filtrar pela sua preferência de odds
                                if odd_minima <= odd_casa <= odd_maxima:
                                    recomendacao = "✅ APOSTAR CASA" if analise['valor_casa'] > 1.05 else "⚠️ SEM VALOR"
                                elif odd_minima <= odd_fora <= odd_maxima:
                                    recomendacao = "✅ APOSTAR FORA" if analise['valor_fora'] > 1.05 else "⚠️ SEM VALOR"
                                else:
                                    recomendacao = "❌ ODDS FORA DO SEU CRITÉRIO"
                                
                                jogos_analisados.append({
                                    "Hora": jogo['fixture']['date'][11:16],
                                    "Liga": jogo['league']['name'],
                                    "Jogo": f"{jogo['teams']['home']['name']} vs {jogo['teams']['away']['name']}",
                                    "Odd Casa": odd_casa,
                                    "Odd Fora": odd_fora,
                                    "Prob. Real Casa": f"{analise['prob_casa']}%",
                                    "Valor": recomendacao
                                })
            except:
                continue
        
        return jogos_analisados, None
        
    except Exception as e:
        return None, str(e)

# --- INTERFACE ---
if st.button("🔍 ANALISAR JOGOS"):
    with st.spinner('Calculando valores...'):
        resultados, erro = buscar_jogos_com_odds()
        
        if erro:
            st.error(f"❌ {erro}")
            st.info("""
            **Soluções:**
            - Aguarde aprovação da API-Football no RapidAPI
            - Ou tente outra data (amanhã, por exemplo)
            """)
        elif not resultados:
            st.warning("Sem jogos encontrados para análise nesta data")
        else:
            st.success(f"✅ {len(resultados)} jogos analisados!")
            
            # Filtrar só os que têm valor
            com_valor = [j for j in resultados if "APOSTAR" in j['Valor']]
            
            if com_valor:
                st.subheader("🎯 Oportunidades Detectadas")
                for jogo in com_valor:
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: #1e2130; padding: 15px; border-radius: 10px; border-left: 5px solid #00ff00; margin-bottom: 10px;">
                            <p style="margin:0; color: #00ff00;">{jogo['Hora']} - {jogo['Liga']}</p>
                            <h3 style="margin: 5px 0; color: white;">{jogo['Jogo']}</h3>
                            <p style="margin:0; color: #ddd;">Odd Casa: <b>{jogo['Odd Casa']}</b> | Odd Fora: <b>{jogo['Odd Fora']}</b></p>
                            <p style="margin:0; color: #888;">{jogo['Prob. Real Casa']} de chance real</p>
                            <p style="margin:5px 0; color: #00ff00; font-size: 16px;"><b>{jogo['Valor']}</b></p>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("Nenhum jogo com valor positivo detectado hoje. Tente outra data.")
            
            # Mostrar todos os jogos analisados
            with st.expander("📊 Ver Todos os Jogos Analisados"):
                df = pd.DataFrame(resultados)
                st.dataframe(df, use_container_width=True)

st.divider()
st.caption("Matemática: Value Betting Simplificado | Foco: Odds entre 1.50 e 2.50")
