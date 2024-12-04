from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import psycopg2
import json
import openai

# Configuração do Flask
app = Flask(__name__)

# Configurações de Conexão com o PostgreSQL
DB_CONFIG = {
    "dbname": "clientes",
    "user": "postgres",
    "password": "lg99487330",
    "host": "clientes.ctwwgeq28qr7.us-east-1.rds.amazonaws.com",
    "port": "5432"  # Porta padrão do PostgreSQL
}

# Configuração da API do OpenAI
load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
# Função para buscar dados do cliente no PostgreSQL
def get_client_config(from_number):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Normaliza o número
        normalized_number = from_number.replace("whatsapp:", "")
        cursor.execute("SELECT mensagens FROM clientes WHERE telefone = %s", (normalized_number,))
        result = cursor.fetchone()
        if result:
            return json.loads(result[0])  # Retorna o JSON das mensagens
        return None
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Função para interagir com a API do OpenAI
def chat_with_openai(user_message):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=user_message,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Erro ao acessar a API OpenAI: {e}")
        return "Desculpe, não consegui processar sua solicitação agora."

# Webhook principal
@app.route("/webhook", methods=['POST'])
def webhook():
    incoming_msg = request.values.get('Body', '').strip()
    from_number = request.values.get('From', '')

    print(f"Mensagem recebida de {from_number}: {incoming_msg}")

    response = MessagingResponse()
    mensagens = get_client_config(from_number)

    if not mensagens:
        response.message("Desculpe, não reconhecemos sua empresa. Entre em contato com o suporte.")
        return str(response)

    # Respostas personalizadas
    if "oi" in incoming_msg.lower() or "olá" in incoming_msg.lower():
        response.message(mensagens["saudacao"])
    elif "sim" in incoming_msg.lower():
        response.message(mensagens["satisfacao"])
        response.message(mensagens["vantagens"])
        response.message(mensagens["audio"])
        response.message(mensagens["pergunta"])
    elif "call" in incoming_msg.lower() or "agendar" in incoming_msg.lower():
        response.message(mensagens["convite"])
    else:
        resposta_ia = chat_with_openai(incoming_msg)
        response.message(resposta_ia)

    return str(response)

# Iniciar o servidor Flask
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
