import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import gspread
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Dados em memória
lista_gastos = []
total_gastos = 0.0

# Configurar Google Sheets
gc = gspread.service_account(filename='credentials.json')
SHEET_NAME = "Controle de Gastos"
try:
    sh = gc.open(SHEET_NAME)
except:
    # Cria uma planilha caso não exista
    sh = gc.create(SHEET_NAME)
    sh.share(gc.auth.service_account_email, perm_type='user', role='writer')

def salvar_no_google_sheets(nome, valor):
    mes = datetime.now().strftime("%Y-%m")
    try:
        worksheet = sh.worksheet(mes)
    except:
        worksheet = sh.add_worksheet(title=mes, rows="1000", cols="2")
        worksheet.append_row(["Gasto", "Valor"])
    worksheet.append_row([nome, f"R$ {valor:.2f}"])

@app.route("/", methods=["GET"])
def home():
    return "Bot de Gastos está Online! 🚀"

@app.route("/bot", methods=["POST"])
def whatsapp_bot():
    global total_gastos
    msg = request.form.get("Body").strip()
    response = MessagingResponse()

    if msg.lower() == "reset":
        lista_gastos.clear()
        total_gastos = 0.0
        response.message("Todos os gastos foram resetados! ✅")

    elif msg.lower() == "list":
        if not lista_gastos:
            response.message("Nenhum gasto registrado ainda! 📝")
        else:
            lista_texto = "\n".join([f"{i+1}⃣ {item}" for i, item in enumerate(lista_gastos)])
            response.message(f"\U0001F4DC Lista de Gastos:\n{lista_texto}\n\n\U0001F4B0 Total: R$ {total_gastos:.2f}")

    elif msg.lower() == "delete":
        if lista_gastos:
            removido = lista_gastos.pop()
            valor = float(removido.split("R$ ")[1])
            total_gastos -= valor
            response.message(f"Gasto removido: {removido} ❌\nTotal atual: R$ {total_gastos:.2f}")
        else:
            response.message("Nenhum gasto para remover!")

    else:
        try:
            nome, valor = msg.rsplit(" - ", 1)
            valor = float(valor.replace(",", "."))
            lista_gastos.append(f"{nome} - R$ {valor:.2f}")
            total_gastos += valor
            salvar_no_google_sheets(nome, valor)
            response.message(f"Gasto registrado: {nome} - R$ {valor:.2f} 💰\nTotal atual: R$ {total_gastos:.2f}")
        except ValueError:
            response.message("Formato inválido! Envie no formato: Nome - Valor\nEx: Uber - 15.57")

    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
