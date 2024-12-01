import telebot
from telebot.async_telebot import AsyncTeleBot
from telebot.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from config import BOT_TOKEN, BASE_URL

bot = AsyncTeleBot(BOT_TOKEN)

import aiohttp

async def on_startup():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"Error removing webhook: {e}")

@bot.message_handler(commands=['start'])
async def start(message):
    try:
        # Create user if doesn't exist
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{BASE_URL}/api/users", json={
                'telegram_id': str(message.from_user.id),
                'username': message.from_user.username or f"User {message.from_user.id}"
            }) as response:
                if response.status not in [200, 201]:
                    print(f"Error creating user: {await response.text()}")
                    return

        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        webapp_btn = KeyboardButton(
            text="📊 Открыть статистику", 
            web_app=WebAppInfo(url=f"{BASE_URL}/static/index.html")
        )
        markup.add(webapp_btn)
        
        start_param = message.text.split()
        if len(start_param) > 1 and start_param[1].startswith('ref'):
            try:
                referrer_id = start_param[1][3:]  # Remove 'ref' prefix
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{BASE_URL}/api/referral", json={
                        'referrer_id': referrer_id,
                        'referee_id': str(message.from_user.id)
                    }) as response:
                        result = await response.json()
                        if response.status == 200 and result.get('success'):
                            await bot.send_message(
                                message.chat.id,
                                "Добро пожаловать! Вы были приглашены другим пользователем. 🎉",
                                reply_markup=markup
                            )
                            if result.get('premium_earned'):
                                try:
                                    await bot.send_message(
                                        int(referrer_id),
                                        "🎉 Поздравляем! Вы пригласили 10 друзей и получили Premium статус!"
                                    )
                                except Exception as e:
                                    print(f"Error sending premium notification: {e}")
                            return
            except Exception as e:
                print(f"Error processing referral: {e}")
        
        await bot.send_message(
            message.chat.id,
            "Привет! 👋\nНажми на кнопку ниже, чтобы посмотреть свою статистику.",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Error in start handler: {e}")
        await bot.send_message(
            message.chat.id,
            "Произошла ошибка. Пожалуйста, попробуйте позже."
        )

@bot.message_handler(content_types=['web_app_data'])
async def web_app_handler(message):
    await bot.send_message(message.chat.id, f"Received data: {message.web_app_data.data}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(on_startup())
    asyncio.run(bot.polling(non_stop=True))
