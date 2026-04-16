from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from app import save_financial_entry, handle_query
from parser import detect_intent
from storage import ensure_storage

TOKEN = "8771757393:AAGPkSFDnSQsNawmicy_SXMOExZq4uADD4o"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Seu agente financeiro está pronto 💰")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None or update.message.text is None:
        return

    text = update.message.text
    intent = detect_intent(text)

    if intent in {"registrar_despesa", "registrar_receita"}:
        response = save_financial_entry(text)
    else:
        response = handle_query(text)

    await update.message.reply_text(response)


def main():
    ensure_storage()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot rodando...")
    app.run_polling()


if __name__ == "__main__":
    main()