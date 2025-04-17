import os
import json
import requests
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

BOT_TOKEN = os.getenv("BOT_TOKEN", "7344541156:AAHPKHq-d4zJs2XQS2TbfyAQeK8jyx4txBo")
FORCE_JOIN_CHANNEL = "AxomBotz"

# Check if user is a member of the channel
async def is_member(user_id, bot):
    try:
        chat_member = await bot.get_chat_member(f"@{FORCE_JOIN_CHANNEL}", user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except:
        return False

# Force join checker
async def check_force_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    bot = context.bot

    if not await is_member(user_id, bot):
        await update.message.reply_text(
            f"🚨 To use this bot, please join first!\n\n"
            "🔹 After joining, click check.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔥 Join Channel 🔥", url=f"https://t.me/{FORCE_JOIN_CHANNEL}")],
                [InlineKeyboardButton("Check", callback_data="check")]
            ])
        )
        return False
    return True

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return
    await update.message.reply_text("👋 Welcome! Use /gen <uid> <password> to generate token.")

# /gen command
async def gen_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_force_join(update, context):
        return

    try:
        if len(context.args) != 2:
            await update.message.reply_text("Usage: /gen <uid> <password>")
            return

        uid, password = context.args
        url = f"https://alone-jwt-api.vercel.app/token?uid={uid}&password={password}"
        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
                if 'token' in data:
                    formatted = json.dumps({"token": data['token']}, indent=4)
                    await update.message.reply_text(f"<pre>{formatted}</pre>", parse_mode="HTML")
                else:
                    await update.message.reply_text("❌ Token not found in response.")
            except json.JSONDecodeError:
                await update.message.reply_text("❌ Failed to parse JSON response.")
        else:
            await update.message.reply_text("❌ API request failed. Check UID/Password.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Error: {str(e)}")

# Check button callback
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    bot = context.bot

    if query.data == "check":
        if await is_member(user_id, bot):
            await query.message.delete()
            await bot.send_message(chat_id=user_id, text="✅ You have joined! Use /gen <uid> <password> to generate token.")
        else:
            await query.answer("❌ You have not joined the channel yet.", show_alert=True)

# Main
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen_command))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("✅ Bot is running...")
    app.run_polling()
