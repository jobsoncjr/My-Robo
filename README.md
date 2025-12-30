# 🎯 OneNation Analyzer Pro

Sistema de análise estatística avançada para apostas esportivas com foco em encontrar **apostas de valor** (value bets) usando modelos matemáticos e dados de APIs especializadas.

## 📋 Índice

- [Sobre o Projeto](#-sobre-o-projeto)
- [Funcionalidades](#-funcionalidades)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação](#-instalação)
- [Configuração](#-configuração)
- [Como Executar](#-como-executar)
- [Como Usar](#-como-usar)
- [Metodologia de Análise](#-metodologia-de-análise)
- [APIs Utilizadas](#-apis-utilizadas)
- [Credenciais de Acesso](#-credenciais-de-acesso)
- [Roadmap](#-roadmap)

---

## 🎯 Sobre o Projeto

O **OneNation Analyzer Pro** é uma aplicação web desenvolvida em Streamlit que ajuda apostadores a identificar oportunidades de valor no mercado de apostas esportivas. O sistema:

- 🔬 Analisa estatísticas de times/jogadores
- 📊 Calcula probabilidades usando distribuição de Poisson
- 💰 Compara odds do mercado com odds justas calculadas
- 🎯 Identifica apostas com **edge positivo** (valor)
- 📈 Gera sugestões automáticas de apostas

## ✨ Funcionalidades

### 🔐 Sistema de Login
- Autenticação de usuários com hash de senha (SHA-256)
- Gerenciamento de sessões
- Usuários padrão:
  - **admin** / admin123
  - **usuario** / 123456

### 📅 Jogos do Dia
- Busca jogos de futebol por data
- Filtro por liga/campeonato
- Principais ligas suportadas:
  - 🇧🇷 Brasileirão (Séries A e B)
  - 🏴󠁧󠁢󠁥󠁮󠁧󠁿 Premier League
  - 🇪🇸 La Liga
  - 🇮🇹 Serie A
  - 🇩🇪 Bundesliga
  - 🇫🇷 Ligue 1
  - 🏆 Champions League, Libertadores e mais

### 🔬 Análise Manual
- Entrada manual de estatísticas de times
- Análise sem necessidade de API
- Cálculo de:
  - Probabilidades de vitória/empate/derrota
  - Expectativa de gols
  - Probabilidade Over/Under 2.5 gols
  - Probabilidade BTTS (Ambas as equipes marcam)
- Comparação com odds da casa de apostas
- Cálculo de **edge** (vantagem percentual)

### 🎰 Apostas Combinadas
- Gerador de múltiplas/acumuladas
- Cálculo de odd total
- Simulação de retorno potencial
- Perfis de risco (conservador/moderado/agressivo)

### 📊 Histórico (Em desenvolvimento)
- Tracking de sugestões
- Análise de performance
- Cálculo de ROI

---

## 📁 Estrutura do Projeto

```
My-Robo/
│
├── robo_onenation.py      # Aplicação principal Streamlit
├── requirements.txt       # Dependências do projeto
└── README.md             # Este arquivo
```

### Módulos do Código

#### 1. **Configuração e Login**
```python
# Linhas 1-58
- Configuração da página Streamlit
- Sistema de autenticação com hash
- Gerenciamento de sessões
```

#### 2. **Integração com APIs**
```python
# Linhas 59-138
- API-Football: dados de jogos, estatísticas, odds
- The Odds API: cotações em tempo real
- Funções de requisição e tratamento de erros
```

#### 3. **Análise Estatística**
```python
# Linhas 139-268
- Distribuição de Poisson para probabilidades
- Cálculo de expectativa de gols
- Análise de forma recente
- Força de ataque/defesa
- Geração de sugestões baseadas em edge
```

#### 4. **Interface do Usuário**
```python
# Linhas 269-754
- 4 abas principais:
  1. Jogos do Dia
  2. Análise Manual
  3. Apostas Combinadas
  4. Histórico
```

---

## 🛠 Tecnologias Utilizadas

- **Python 3.8+**
- **Streamlit** - Framework web para aplicações de dados
- **Pandas** - Manipulação e análise de dados
- **Requests** - Requisições HTTP para APIs
- **hashlib** - Criptografia de senhas

---

## 📦 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Conta nas APIs (opcional, mas recomendado):
  - [API-Football (RapidAPI)](https://rapidapi.com/api-sports/api/api-football)
  - [The Odds API](https://the-odds-api.com/)

---

## 🚀 Instalação

### 1. Clone ou baixe o repositório

```bash
cd "/Users/galbmorais/Merdas do Jobson/My-Robo"
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python3 -m venv venv
```

### 3. Ative o ambiente virtual

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Configuração

### Configurar APIs (Opcional)

Para usar as funcionalidades completas, configure as chaves de API no arquivo `.streamlit/secrets.toml`:

1. Crie a pasta `.streamlit` na raiz do projeto:
```bash
mkdir .streamlit
```

2. Crie o arquivo `secrets.toml`:
```bash
touch .streamlit/secrets.toml
```

3. Adicione suas chaves de API:
```toml
API_FOOTBALL_KEY = "sua_chave_aqui"
ODDS_API_KEY = "sua_chave_aqui"
```

**⚠️ Importante:** O arquivo `secrets.toml` não deve ser commitado no Git. Adicione ao `.gitignore`:
```
.streamlit/
```

### Modo sem API

O sistema funciona **sem APIs configuradas** usando a aba "Análise Manual", onde você pode inserir dados manualmente.

---

## ▶️ Como Executar

### 1. Certifique-se de que o ambiente virtual está ativado

```bash
source venv/bin/activate  # macOS/Linux
# ou
venv\Scripts\activate     # Windows
```

### 2. Execute o Streamlit

```bash
streamlit run robo_onenation.py
```

### 3. Acesse no navegador

O sistema abrirá automaticamente no navegador em:
```
http://localhost:8501
```

### 4. Faça login

Use uma das credenciais padrão:
- **Usuário:** admin | **Senha:** admin123
- **Usuário:** usuario | **Senha:** 123456

---

## 📖 Como Usar

### 🔬 Análise Manual (Modo Offline)

1. Acesse a aba **"Análise Manual"**
2. Preencha os dados do time da casa:
   - Nome, jogos, vitórias, empates, derrotas
   - Gols marcados/sofridos
   - Forma recente (ex: WWDWL)
3. Preencha os dados do time visitante
4. Insira as odds da casa de apostas OneNation
5. Clique em **"ANALISAR PARTIDA"**
6. Veja as sugestões com edge positivo

### 📅 Jogos do Dia (Requer API)

1. Acesse a aba **"Jogos do Dia"**
2. Selecione a liga desejada
3. Escolha a data
4. Clique em **"Buscar Jogos"**
5. Expanda um jogo para ver detalhes

### 🎰 Apostas Combinadas

1. Acesse a aba **"Apostas Combinadas"**
2. Adicione suas seleções (jogo + odd)
3. Defina o valor da aposta
4. Veja a odd total e retorno potencial
5. Escolha o perfil de risco desejado

---

## 🧮 Metodologia de Análise

### 1. Distribuição de Poisson

O sistema usa a distribuição de Poisson para calcular probabilidades de resultados:

```python
P(X = k) = (e^(-λ) * λ^k) / k!
```

Onde:
- λ = expectativa de gols
- k = número de gols

### 2. Expectativa de Gols

Calculada com base em:
- Força de ataque do time
- Força de defesa do adversário
- Fator casa/fora
- Forma recente (últimos 5 jogos)

### 3. Cálculo de Edge

```
Edge (%) = ((Odd Mercado / Odd Justa) - 1) × 100
```

**Edge positivo** indica valor na aposta.

### 4. Níveis de Sugestão

- 🟢 **FORTE** - Edge > 15%
- 🟡 **MODERADO** - Edge 10-15%
- 🔵 **LEVE** - Edge 5-10%

### 5. Confiança da Análise

- **Alta**: 10+ jogos por time na temporada
- **Média**: 5-9 jogos por time
- **Baixa**: < 5 jogos por time

---

## 🌐 APIs Utilizadas

### 1. API-Football (RapidAPI)

**O que fornece:**
- Jogos ao vivo e programados
- Estatísticas detalhadas de times
- Confrontos diretos (H2H)
- Odds de casas de apostas
- Ligas de todo o mundo

**Planos:**
- Gratuito: 100 requisições/dia
- Pago: A partir de $5/mês

**Como obter:**
1. Acesse [RapidAPI - API Football](https://rapidapi.com/api-sports/api/api-football)
2. Crie uma conta
3. Subscribe (plano gratuito ou pago)
4. Copie sua API Key

### 2. The Odds API

**O que fornece:**
- Odds em tempo real
- Múltiplas casas de apostas
- Diversos mercados (1X2, Over/Under, etc.)

**Planos:**
- Gratuito: 500 requisições/mês
- Pago: A partir de $10/mês

**Como obter:**
1. Acesse [The Odds API](https://the-odds-api.com/)
2. Faça Sign Up
3. Copie sua API Key do dashboard

---

## 🔑 Credenciais de Acesso

### Usuários Padrão

| Usuário | Senha | Permissões |
|---------|-------|------------|
| admin | admin123 | Completas |
| usuario | 123456 | Completas |

### Como Adicionar Novos Usuários

Edite o arquivo `robo_onenation.py` na linha 43:

```python
users = {
    "admin": hash_password("admin123"),
    "usuario": hash_password("123456"),
    "novouser": hash_password("suasenha")  # Adicione aqui
}
```

---

## 🗺 Roadmap

### ✅ Implementado
- [x] Sistema de login
- [x] Análise manual de partidas
- [x] Cálculo de probabilidades (Poisson)
- [x] Cálculo de edge
- [x] Gerador de combinadas
- [x] Integração com API-Football
- [x] Filtros por liga e data

### 🚧 Em Desenvolvimento
- [ ] Histórico de apostas
- [ ] Tracking de resultados
- [ ] Cálculo de ROI
- [ ] Gráficos de desempenho
- [ ] Basquete, Tênis, eSports
- [ ] Sistema de notificações
- [ ] Export de sugestões (PDF/Excel)

### 💡 Planejado
- [ ] Machine Learning para previsões
- [ ] Integração com mais casas de apostas
- [ ] App mobile
- [ ] Alertas de valor em tempo real
- [ ] Análise de cartões/escanteios
- [ ] Gestão de banca (bankroll)

---

## ⚠️ Avisos Importantes

1. **Este sistema é apenas para fins educacionais e de análise**
2. **Aposte com responsabilidade**
3. **Não há garantia de lucro em apostas**
4. **Use apenas dinheiro que você pode perder**
5. **Verifique a legalidade das apostas em sua região**

---

## 📝 Notas Técnicas

### Estrutura de Dados das APIs

**API-Football Response:**
```json
{
  "response": [
    {
      "fixture": {...},
      "teams": {
        "home": {...},
        "away": {...}
      },
      "goals": {...},
      "league": {...}
    }
  ]
}
```

### Melhorias Possíveis

1. **Banco de Dados**: Implementar SQLite/PostgreSQL para histórico
2. **Cache**: Usar Redis para cache de requisições API
3. **Testes**: Adicionar testes unitários (pytest)
4. **CI/CD**: Pipeline de deploy automatizado
5. **Docker**: Containerização da aplicação

---

## 🤝 Contribuindo

Para contribuir com o projeto:

1. Faça um fork
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto é para uso pessoal e educacional.

---

## 💬 Suporte

Para dúvidas ou sugestões, abra uma issue no repositório.

---

**Desenvolvido com 🎯 para apostadores inteligentes**
