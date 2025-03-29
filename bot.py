import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Banco de dados simples
lista_gastos = []
total_gastos = 0.0

@app.route("/", methods=["GET"])
def home():
    return "O BOT TÁ ON! 🚀"

@app.route("/bot", methods=["POST"])
def whatsapp_bot():
    global total_gastos
    msg = request.form.get("Body").strip()
    response = MessagingResponse()

    if msg.lower() in  ["resetar", "limpar"]:
        lista_gastos.clear()
        total_gastos = 0.0
        response.message("Todos os gastos foram resetados! ✅")

    elif msg.lower() == "lista":
        if not lista_gastos:
            response.message("Nenhum gasto registrado ainda! 📝")
        else:
            lista_texto = "\n".join([f"{i+1}⃣ {item}" for i, item in enumerate(lista_gastos)])
            response.message(f"\U0001F4DC Lista de Gastos:\n{lista_texto}\n\n\U0001F4B0 Total: R$ {total_gastos:.2f}")

    elif msg.lower() in ["remover","deletar"]:
        if lista_gastos:
            removido = lista_gastos.pop()
            valor_removido = float(removido.split("R$ ")[1])
            total_gastos -= valor_removido
            response.message(f"Gasto removido: {removido}\nTotal atual: R$ {total_gastos:.2f}")
        else:
            response.message("Nenhum gasto para remover! ❌")

    else:
        try:
            nome, valor = msg.rsplit(" - ", 1)
            valor = float(valor.replace(",", "."))
            lista_gastos.append(f"{nome} - R$ {valor:.2f}")
            total_gastos += valor
            response.message(f"Gasto registrado: {nome} - R$ {valor:.2f} 💰\nTotal atual: R$ {total_gastos:.2f}")
        except ValueError:
            response.message("Formato inválido! Envie no formato: Nome - Valor\nEx: Uber - 15.57")

    return str(response)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
