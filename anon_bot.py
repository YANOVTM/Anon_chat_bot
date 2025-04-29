from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext
import asyncio

TOKEN = '7638265327:AAFdjpelQuZlw3_fD41keJEEf6gdzHvHn9o'
OWNER_ID = 5067997681  # Твой Telegram ID
ADMIN_IDS = [987654321]  # Список ID админов

# Словари для пользователей
users = {}
chats = {}

# Панель для владельца
owner_keyboard = ReplyKeyboardMarkup(
    [['Рассылка', 'Статистика'], ['Выход']], resize_keyboard=True)

# Панель для админа
admin_keyboard = ReplyKeyboardMarkup(
    [['Рассылка'], ['Выход']], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text("Добро пожаловать в анонимный чат знакомств!\nНапиши 'Поиск', чтобы найти собеседника.")
    users[user_id] = {'state': 'idle'}

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if user_id == OWNER_ID:
        await owner_panel(update, context, text)
    elif user_id in ADMIN_IDS:
        await admin_panel(update, context, text)
    else:
        await user_message(update, context, text)

async def owner_panel(update, context, text):
    if text == '/panel':
        await update.message.reply_text("Владельческая панель.", reply_markup=owner_keyboard)
    elif text == 'Рассылка':
        await update.message.reply_text("Напиши текст рассылки:")
        users[update.effective_user.id]['state'] = 'broadcast_owner'
    elif users[update.effective_user.id].get('state') == 'broadcast_owner':
        message = text
        for uid in users:
            if uid != OWNER_ID:
                try:
                    await context.bot.send_message(uid, f"Рассылка от владельца:\n\n{message}")
                except:
                    pass
        await update.message.reply_text("Рассылка отправлена.", reply_markup=owner_keyboard)
        users[update.effective_user.id]['state'] = 'idle'
    elif text == 'Статистика':
        await update.message.reply_text(f"Всего пользователей: {len(users)}", reply_markup=owner_keyboard)
    elif text == 'Выход':
        await update.message.reply_text("Выход из панели.", reply_markup=None)
        users[update.effective_user.id]['state'] = 'idle'

async def admin_panel(update, context, text):
    if text == '/panel':
        await update.message.reply_text("Админ-панель.", reply_markup=admin_keyboard)
    elif text == 'Рассылка':
        await update.message.reply_text("Напиши текст рассылки:")
        users[update.effective_user.id]['state'] = 'broadcast_admin'
    elif users[update.effective_user.id].get('state') == 'broadcast_admin':
        message = text
        for uid in users:
            if uid != update.effective_user.id:
                try:
                    await context.bot.send_message(uid, f"Рассылка от администратора:\n\n{message}")
                except:
                    pass
        await update.message.reply_text("Рассылка отправлена.", reply_markup=admin_keyboard)
        users[update.effective_user.id]['state'] = 'idle'
    elif text == 'Выход':
        await update.message.reply_text("Выход из панели.", reply_markup=None)
        users[update.effective_user.id]['state'] = 'idle'

async def user_message(update, context, text):
    user_id = update.effective_user.id
    if text.lower() == 'поиск':
        partner_id = None
        for uid, data in users.items():
            if data.get('state') == 'search' and uid != user_id:
                partner_id = uid
                break
        if partner_id:
            chats[user_id] = partner_id
            chats[partner_id] = user_id
            users[user_id]['state'] = 'chat'
            users[partner_id]['state'] = 'chat'
            await context.bot.send_message(partner_id, "Собеседник найден! Пиши сюда.")
            await update.message.reply_text("Собеседник найден! Пиши сюда.")
        else:
            users[user_id]['state'] = 'search'
            await update.message.reply_text("Ищем собеседника...")
    elif text.lower() == 'стоп':
        if user_id in chats:
            partner_id = chats[user_id]
            await context.bot.send_message(partner_id, "Собеседник отключился.")
            await update.message.reply_text("Чат завершён.")
            del chats[user_id]
            del chats[partner_id]
            users[user_id]['state'] = 'idle'
            users[partner_id]['state'] = 'idle'
        else:
            await update.message.reply_text("Вы не в чате.")
    elif users[user_id].get('state') == 'chat':
        partner_id = chats.get(user_id)
        if partner_id:
            await context.bot.send_message(partner_id, text)
    else:
        await update.message.reply_text("Напиши 'Поиск' чтобы начать поиск собеседника.")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('panel', message_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

    print("Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
