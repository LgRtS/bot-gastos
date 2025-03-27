import os
import datetime
import gspread
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# Banco de dados simples (memória)
lista_gastos = []
total_gastos = 0.0

# Configuração do Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"  # O arquivo que você baixou no Google Cloud
SHEET_NAME = "Controle de Gastos"  # Nome da sua planilha

# Autenticação
credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
client = gspread.authorize(credentials)

def registrar_gasto_planilha(nome, valor):
    # Nome da aba com o mês atual
    mes = datetime.datetime.now().strftime("%m-%Y")
    try:
        sheet = client.open(SHEET_NAME).worksheet(mes)
    except gspread.exceptions.WorksheetNotFound:
        # Cria a aba caso não exista
        sheet = client.open(SHEET_NAME).add_worksheet(title=mes, rows="1000", cols="2")
        sheet.append_row(["Gasto", "Valor"])

    # Registra o gasto
    sheet.append_row([nome, f"{valor:.2f}"])


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
            valor_removido = float(removido.split("R$ ")[1])
            total_gastos -= valor_removido
            response.message(f"Gasto removido: {removido} ❌\nTotal atual: R$ {total_gastos:.2f}")
        else:
            response.message("Nenhum gasto para remover! 🗑️")

    else:
        try:
            nome, valor = msg.rsplit(" - ", 1)
            valor = float(valor.replace(",", "."))
            lista_gastos.append(f"{nome} - R$ {valor:.2f}")
            total_gastos += valor

            # Registrar na planilha
            registrar_gasto_planilha(nome, valor)

            response.message(f"Gasto registrado: {nome} - R$ {valor:.2f} 💰\nTotal atual: R$ {total_gastos:.2f}")
        except ValueError:
            response.message("Formato inválido! Envie no formato: Nome - Valor\nEx: Uber - 15.57")

    return str(response)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
