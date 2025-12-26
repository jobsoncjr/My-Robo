import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Analista OneNation – Futebol", layout="wide")

st.title("⚽ Analista OneNation – Calculadora de Valor (Futebol)")
st.write("Ferramenta simples e funcional para avaliar se uma aposta tem valor na OneNation.bet.")

st.markdown("---")

st.header("1️⃣ Dados do Jogo")

col_times = st.columns(2)
with col_times[0]:
    time_casa = st.text_input("Time da Casa", "Time A")
with col_times[1]:
    time_fora = st.text_input("Time Visitante", "Time B")

st.subheader("Últimos jogos (forma recente)")
st.markdown("Preencha os **últimos jogos** de cada time (por exemplo, últimos 10 jogos):")

col_forma = st.columns(2)

with col_forma[0]:
    st.markdown(f"### {time_casa} (Casa)")
    jogos_casa = st.number_input("Jogos analisados (Casa)", 1, 50, 10)
    v_casa = st.number_input("Vitórias", 0, 50, 6)
    e_casa = st.number_input("Empates", 0, 50, 2)
    d_casa = st.number_input("Derrotas", 0, 50, 2)
    gols_pro_casa = st.number_input("Gols marcados", 0, 200, 18)
    gols_contra_casa = st.number_input("Gols sofridos", 0, 200, 8)

with col_forma[1]:
    st.markdown(f"### {time_fora} (Fora)")
    jogos_fora = st.number_input("Jogos analisados (Fora)", 1, 50, 10)
    v_fora = st.number_input("Vitórias ", 0, 50, 4)
    e_fora = st.number_input("Empates ", 0, 50, 3)
    d_fora = st.number_input("Derrotas ", 0, 50, 3)
    gols_pro_fora = st.number_input("Gols marcados ", 0, 200, 14)
    gols_contra_fora = st.number_input("Gols sofridos ", 0, 200, 12)

st.markdown("---")

st.header("2️⃣ Odds da OneNation")
st.markdown("Informe as odds que você vê na OneNation para este jogo:")

col_odds = st.columns(3)
with col_odds[0]:
    odd_casa = st.number_input("Odd Casa (1)", 1.01, 100.0, 1.60)
with col_odds[1]:
    odd_empate = st.number_input("Odd Empate (X)", 1.01, 100.0, 3.80)
with col_odds[2]:
    odd_fora = st.number_input("Odd Fora (2)", 1.01, 100.0, 5.00)

st.markdown("---")


def calcular_rating_time(jogos, v, e, d, gols_pro, gols_contra, bonus_mando=0.0):
    """Rating simples baseado em pontos por jogo e saldo de gols por jogo."""
    if jogos <= 0:
        return 0.0

    pontos = v * 3 + e
    ppg = pontos / jogos                     # pontos por jogo
    saldo = (gols_pro - gols_contra) / jogos  # saldo médio

    # Fórmula simples e transparente
    # O peso do mando de campo (bonus_mando) ajuda a diferenciar casa/fora
    rating = ppg * 2.0 + saldo * 0.5 + bonus_mando
    return rating


def prob_resultados(rating_casa, rating_fora):
    """
    Converte ratings em probabilidades de:
    - Casa vencer
    - Empate
    - Fora vencer
    """
    # Para evitar valores nulos ou negativos que quebrariam a conta, garantimos um mínimo
    base_casa = max(0.1, rating_casa)
    base_fora = max(0.1, rating_fora)

    # Peso base do empate – ajustável (aqui definido como 40% da média dos ratings)
    base_empate = (base_casa + base_fora) * 0.4

    soma = base_casa + base_empate + base_fora

    p_casa = base_casa / soma
    p_empate = base_empate / soma
    p_fora = base_fora / soma

    return p_casa, p_empate, p_fora


def calc_odd_justa(p):
    """Calcula a odds justa (decimal) baseada na probabilidade."""
    if p <= 0:
        return None
    return round(1.0 / p, 2)


def calc_edge(odd, odd_justa):
    """Calcula o valor esperado (Edge) em porcentagem."""
    if odd is None or odd_justa is None:
        return None
    return round((odd / odd_justa - 1.0) * 100, 1)


st.header("3️⃣ Resultado da Análise")

if st.button("🚀 Calcular Probabilidades e Valor"):
    # 1) Calcular ratings dos times
    rating_casa = calcular_rating_time(
        jogos_casa, v_casa, e_casa, d_casa, gols_pro_casa, gols_contra_casa, bonus_mando=0.5
    )
    rating_fora = calcular_rating_time(
        jogos_fora, v_fora, e_fora, d_fora, gols_pro_fora, gols_contra_fora, bonus_mando=0.0
    )

    st.subheader("📌 Ratings dos Times (Modelo Próprio)")
    col_r = st.columns(2)
    with col_r[0]:
        st.metric(f"Rating {time_casa}", f"{rating_casa:.2f}")
    with col_r[1]:
        st.metric(f"Rating {time_fora}", f"{rating_fora:.2f}")

    # 2) Calcular probabilidades aproximadas
    p_casa, p_empate, p_fora = prob_resultados(rating_casa, rating_fora)

    # 3) Calcular odds justas
    odd_justa_casa = calc_odd_justa(p_casa)
    odd_justa_empate = calc_odd_justa(p_empate)
    odd_justa_fora = calc_odd_justa(p_fora)

    # 4) Calcular edge (valor)
    edge_casa = calc_edge(odd_casa, odd_justa_casa)
    edge_empate = calc_edge(odd_empate, odd_justa_empate)
    edge_fora = calc_edge(odd_fora, odd_justa_fora)

    # 5) Montar tabela de dados
    dados = [
        {
            "Mercado": "Casa (1)",
            "Prob_Modelo_%": round(p_casa * 100, 1),
            "Odd_Justa": odd_justa_casa,
            "Odd_OneNation": odd_casa,
            "Edge_%": edge_casa,
        },
        {
            "Mercado": "Empate (X)",
            "Prob_Modelo_%": round(p_empate * 100, 1),
            "Odd_Justa": odd_justa_empate,
            "Odd_OneNation": odd_empate,
            "Edge_%": edge_empate,
        },
        {
            "Mercado": "Fora (2)",
            "Prob_Modelo_%": round(p_fora * 100, 1),
            "Odd_Justa": odd_justa_fora,
            "Odd_OneNation": odd_fora,
            "Edge_%": edge_fora,
        },
    ]

    df = pd.DataFrame(dados)
    st.subheader("📊 Comparação: Modelo Matemático x OneNation")
    
    # Formatação condicional simples para destacar valores positivos na tabela
    st.dataframe(df, use_container_width=True)

    # 6) Destaque das melhores oportunidades (Value Betting)
    st.subheader("🎯 Sinal de Valor")

    melhor = None
    for linha in dados:
        if linha["Edge_%"] is not None and linha["Edge_%"] > 0:
            if melhor is None or linha["Edge_%"] > melhor["Edge_%"]:
                melhor = linha

    if melhor:
        st.success(
            f"✅ **Valor Encontrado:** Aposte no **{melhor['Mercado']}**.\n\n"
            f"O modelo estima uma probabilidade de **{melhor['Prob_Modelo_%']}%** (Odd Justa ≈ {melhor['Odd_Justa']}),\n"
            f"mas a OneNation está pagando **{melhor['Odd_OneNation']}**.\n\n"
            f"**Edge (Retorno Esperado): {melhor['Edge_%']}%**"
        )
    else:
        st.warning("⚠️ Nenhum mercado com 'Edge' positivo encontrado. Segundo o modelo, as odds da OneNation estão baixas ou justas. Recomendo não apostar neste jogo.")
else:
    st.info("Preencha os dados estatísticos e as odds da OneNation acima, depois clique em **'Calcular Probabilidades e Valor'**.")
