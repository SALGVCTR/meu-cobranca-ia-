import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- 1. CONFIGURAÇÃO SEGURA DA IA ---
# Para rodar, você precisará configurar o segredo 'GOOGLE_API_KEY' no Streamlit Cloud
try:
    # Tenta pegar a chave configurada nos Segredos do Streamlit
    CHAVE_API = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=CHAVE_API)
    # Configura o modelo de IA mais rápido e eficiente
    model = genai.GenerativeModel('gemini-1.5-flash-latest') 
except Exception as e:
    st.error("Por favor, configure sua GOOGLE_API_KEY nos Segredos do Streamlit.")
    st.stop() # Interrompe a execução se não houver chave


# --- 2. CONFIGURAÇÃO E LAYOUT DA PÁGINA ---
st.set_page_config(page_title="ZAP-Cobre Fácil", layout="wide", page_icon="📲")
st.title("📲 ZAP-Cobre Fácil: Cobrança via WhatsApp")
st.markdown("---")

# Criamos duas colunas para separar entrada de dados e resultado
col1, col2 = st.columns([1, 1.2])


# --- 3. COLUNA 1: ENTRADA DE DADOS ---
with col1:
    st.subheader("📝 Dados do Cliente")
    nome = st.text_input("Nome do Cliente", placeholder="Ex: Maria Souza")
    
    # Organiza os campos de quantidade e valor em uma linha para economizar espaço
    c1, c2 = st.columns(2)
    quantidade_dia = c1.number_input("Qtd. no Dia", min_value=0, step=1, value=0)
    quantidade_mes = c2.number_input("Qtd. Mensal", min_value=0, step=1, value=0)
    
    c3, c4 = st.columns(2)
    valor_produto = c3.number_input("Valor do Produto (R$)", min_value=0.0, step=0.01, format="%.2f", value=0.00)
    data_vencimento = c4.date_input("Data de Vencimento")

    # Campo crucial para o envio, já pré-formata para facilitar
    telefone = st.text_input("WhatsApp (com DDD)", placeholder="Ex: 5511999999999")
    
    # Calcula o total para info extra
    total_dia = quantidade_dia * valor_produto
    st.info(f"Total desta cobrança (Qtd. Dia * Valor): R$ {total_dia:.2f}")


# --- 4. COLUNA 2: RESULTADO E ENVIO (A MAGIA DA IA) ---
with col2:
    st.subheader("📱 Preview da Cobrança")

    # Só processa se os campos essenciais estiverem preenchidos
    if nome and telefone and valor_produto > 0 and (quantidade_dia > 0 or quantidade_mes > 0):
        
        # PROMPT 1: Tom Amigável (para lembretes)
        prompt_amigavel = f"""
        Você é um assistente de cobrança amigável. Gere uma mensagem de WhatsApp para o cliente {nome}.
        A mensagem é um lembrete sobre o produto/serviço com valor unitário de R${valor_produto:.2f}.
        Hoje ele consumiu {quantidade_dia}, totalizando R${total_dia:.2f}.
        A quantidade mensal dele é {quantidade_mes}.
        A data de vencimento é {data_vencimento}.
        Use um tom educado, use emojis leves.
        Não inclua link, apenas o texto da cobrança.
        """
        
        # PROMPT 2: Tom Urgente (para atrasos)
        prompt_urgente = f"""
        Você é um assistente de cobrança profissional e direto. Gere uma mensagem de WhatsApp para o cliente {nome}.
        Notifique sobre pendência do produto/serviço com valor unitário de R${valor_produto:.2f}.
        O consumo acumulado é {quantidade_dia} hoje (total R${total_dia:.2f}) e {quantidade_mes} no mês.
        A data de vencimento foi/é {data_vencimento}.
        Use um tom firme e profissional, sem emojis.
        Solicite a regularização do pagamento.
        """

        # Gera as mensagens chamando a API (isso é rápido)
        with st.spinner('A IA está redigindo a mensagem...'):
            try:
                msg_amigavel = model.generate_content(prompt_amigavel).text
                msg_urgente = model.generate_content(prompt_urgente).text
            except Exception as e:
                st.error(f"Erro ao falar com a IA: {e}")
                st.stop()

        # Exibe a mensagem gerada com o tom Amigável por padrão
        st.write("**Texto da Cobrança (Tom Amigável):**")
        st.info(msg_amigavel)
        
        # Codifica o texto para que ele funcione corretamente dentro do link do WhatsApp
        msg_encoded_amigavel = urllib.parse.quote(msg_amigavel)
        msg_encoded_urgente = urllib.parse.quote(msg_urgente)
        
        # Cria os links que abrem o WhatsApp direto no celular ou PC
        link_zap_amigavel = f"https://api.whatsapp.com/send?phone={telefone}&text={msg_encoded_amigavel}"
        link_zap_urgente = f"https://api.whatsapp.com/send?phone={telefone}&text={msg_encoded_urgente}"
        
        st.markdown("---")
        st.write("**Escolha o tom e envie:**")
        
        # Cria as colunas para os dois botões de ação final
        b1, b2 = st.columns(2)
        
        # Botão Verde para o tom educado
        with b1:
            st.link_button("😊 Enviar Amigável", link_zap_amigavel, type="primary")
            st.caption("Para lembretes antes ou no dia.")
            
        # Botão Amarelo para o tom direto
        with b2:
            st.link_button("⚠️ Enviar Urgente", link_zap_urgente)
            st.caption("Para faturas já atrasadas.")

    else:
        # Mensagem de ajuda enquanto o usuário não preenche os dados
        st.warning("Preencha todos os dados obrigatórios (Nome, Telefone, Valor e Quantidades) para gerar o link de cobrança.")
        
# --- 5. RODAPÉ ---
st.markdown("---")
st.caption("ZAP-Cobre Fácil v1.0 - Desenvolvido para agilizar sua operação.")
