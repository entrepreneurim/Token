from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import requests
import os
import json

# Token from environment variable
BOT_TOKEN = os.getenv("8006068020:AAEvGfxyMtv7wBA-Bq4r7o_W890FylJ05cc")

async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if len(context.args) != 2:
            await update.message.reply_text("Usage: /gen <uid> <password>")
            return

        uid, password = context.args
        url = f"https://alone-jwt-api.vercel.app/token?uid={uid}&password={password}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                # Format JSON output
                token_json = {
                    "token": data['token']
                }
                formatted = json.dumps(token_json, indent=4)
                await update.message.reply_text(f"<pre>{formatted}</pre>", parse_mode="HTML")
            else:
                await update.message.reply_text("❌ Token not found in response.")
        else:
            await update.message.reply_text("❌ API request failed. Check UID/Password.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {e}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("gen", gen_command))
    app.run_polling()
