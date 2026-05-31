import sys
import asyncio
from pathlib import Path

from flask import Flask, request, jsonify
from aiogram.types import Update

# Добавляем путь к боту
sys.path.insert(0, '/home/ТВОЙ_ЛОГИН/bot')

from bot import bot, dp

app = Flask(__name__)

# Хранилище для вебхука
WEBHOOK_URL = None


@app.route('/webhook', methods=['POST'])
def webhook():
    """Принимает обновления от Telegram"""
    try:
        update_data = request.get_json()
        update = Update(**update_data)
        asyncio.run(dp.feed_update(bot, update))
        return 'OK', 200
    except Exception as e:
        print(f"Ошибка: {e}")
        return 'Error', 500


@app.route('/')
def index():
    return '🤖 Бот работает!'


@app.route('/set_webhook')
def set_webhook():
    """Установка вебхука (вызови один раз вручную)"""
    global WEBHOOK_URL
    WEBHOOK_URL = f'https://{request.host}/webhook'

    async def _set():
        await bot.set_webhook(url=WEBHOOK_URL)
        return 'OK'

    try:
        asyncio.run(_set())
        return f'✅ Вебхук установлен: {WEBHOOK_URL}'
    except Exception as e:
        return f'❌ Ошибка: {e}'


if __name__ == '__main__':
    app.run()