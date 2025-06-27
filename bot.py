import telebot
import requests
import os
from bs4 import BeautifulSoup
from db import init_db, salvar_consulta, obter_historico
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "🔍 Bot OSINT Brasil Ativo!\n\nComandos disponíveis:\n/cnpj 00000000000191\n/nome João da Silva\n/telefone 11999999999\n/servidor CPF ou nome\n/historico (últimas consultas)")

def log_busca(message, comando, termo):
    salvar_consulta(message.from_user.id, message.from_user.username or "Desconhecido", comando, termo)

@bot.message_handler(commands=['cnpj'])
def consulta_cnpj(message):
    try:
        cnpj = message.text.split()[1]
        r = requests.get(f"https://receitaws.com.br/v1/cnpj/{cnpj}")
        data = r.json()
        if 'nome' in data:
            resposta = f"📄 Empresa: {data['nome']}\n📍 {data['logradouro']} - {data['municipio']}/{data['uf']}\n📞 {data['telefone']}"
        else:
            resposta = "❌ CNPJ não encontrado ou limite da API atingido."
        log_busca(message, 'cnpj', cnpj)
        bot.reply_to(message, resposta)
    except:
        bot.reply_to(message, "⚠️ Use o comando assim: /cnpj 00000000000191")

@bot.message_handler(commands=['nome'])
def consulta_nome(message):
    nome = " ".join(message.text.split()[1:])
    if not nome:
        bot.reply_to(message, "⚠️ Envie um nome completo: /nome João da Silva")
        return
    link = f"https://www.jusbrasil.com.br/busca?q={nome.replace(' ', '+')}"
    log_busca(message, 'nome', nome)
    bot.reply_to(message, f"🔎 Resultados públicos para *{nome}*:\n➡️ {link}", parse_mode="Markdown")

@bot.message_handler(commands=['telefone'])
def consulta_telefone(message):
    tel = message.text.split()[1]
    link = f"https://www.google.com/search?q={tel}"
    log_busca(message, 'telefone', tel)
    bot.reply_to(message, f"📞 Resultados para telefone:\n➡️ {link}")

@bot.message_handler(commands=['servidor'])
def consulta_servidor(message):
    termo = " ".join(message.text.split()[1:])
    link = f"https://portaldatransparencia.gov.br/pessoa-fisica/busca?termo={termo.replace(' ', '+')}"
    log_busca(message, 'servidor', termo)
    bot.reply_to(message, f"👨‍💼 Consulta no Portal da Transparência:\n➡️ {link}")

@bot.message_handler(commands=['historico'])
def historico(message):
    rows = obter_historico()
    resposta = "\n".join([f"{row[0]} • {row[1]} • {row[2]} • {row[3][:16]}" for row in rows])
    bot.reply_to(message, f"📜 Últimas buscas:\n\n{resposta}" if rows else "Nenhum histórico registrado.")



@bot.message_handler(commands=['email'])
def consulta_email(message):
    email = message.text.split()[1]
    link = f"https://www.google.com/search?q={email}"
    log_busca(message, 'email', email)
    bot.reply_to(message, f"📧 Resultados públicos para e-mail:
➡️ {link}")

@bot.message_handler(commands=['cep'])
def consulta_cep(message):
    cep = message.text.split()[1].replace("-", "")
    r = requests.get(f"https://viacep.com.br/ws/{cep}/json/")
    if r.status_code == 200 and 'logradouro' in r.json():
        data = r.json()
        resposta = f"🏠 CEP {cep}:
{data['logradouro']}, {data['bairro']}, {data['localidade']}-{data['uf']}"
    else:
        resposta = "❌ CEP não encontrado."
    log_busca(message, 'cep', cep)
    bot.reply_to(message, resposta)


bot.infinity_polling()
