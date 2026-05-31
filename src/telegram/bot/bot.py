import asyncio
import logging
import os
import sys
from pathlib import Path

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Update

logging.basicConfig(level=logging.INFO)


# ==================== ЗАГРУЗКА ТОКЕНА ====================
def load_token():
    # Пробуем разные пути для токена
    possible_paths = [
        Path("token.env"),
        Path("tgconfig/token.env"),
        Path("/home/murat/avito-monitor/src/telegram/tgconfig/token.env"),
        Path(os.path.expanduser("~/avito_bot/token.env"))
    ]

    for token_path in possible_paths:
        try:
            if token_path.exists():
                with open(token_path, 'r') as f:
                    content = f.read().strip()
                    if '=' in content:
                        token = content.split('=')[1].strip().strip('"').strip("'")
                    else:
                        token = content
                    print(f"✅ Токен загружен из {token_path}")
                    return token
        except Exception as e:
            continue

    # Если не нашли - используем жестко заданный (временно)
    print("⚠️ Токен не найден в файлах, использую резервный")
    return "8985132326:AAGBEEsTNrOINbiKlLxGZ_gdG_w14cI_U98"


BOT_TOKEN = load_token()

# ==================== СОЗДАНИЕ БОТА ====================
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# ==================== КЛАВИАТУРА ====================
def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔍 Парсинг")],
            [KeyboardButton(text="📊 Мониторинг")]
        ],
        resize_keyboard=True
    )


# ==================== ГОРОДА ДЛЯ ПАРСИНГА ====================
CITIES = {
    'москва': 'moskva',
    'мск': 'moskva',
    'спб': 'sankt-peterburg',
    'санкт-петербург': 'sankt-peterburg',
    'питер': 'sankt-peterburg',
    'екатеринбург': 'ekaterinburg',
    'новосибирск': 'novosibirsk',
    'казань': 'kazan',
    'нижний новгород': 'nizhniy-novgorod',
    'челябинск': 'chelyabinsk',
    'самара': 'samara',
    'омск': 'omsk',
    'ростов-на-дону': 'rostov-na-donu',
    'уфа': 'ufa',
    'красноярск': 'krasnoyarsk',
    'пермь': 'perm',
    'воронеж': 'voronezh',
    'волгоград': 'volgograd'
}


# ==================== FSM СОСТОЯНИЯ ====================
class ParserStates(StatesGroup):
    waiting_for_product = State()
    waiting_for_city = State()


# ==================== ОБРАБОТЧИКИ КОМАНД ====================
@dp.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я бот для парсинга Avito.\n\n"
        "📌 Что я умею:\n"
        "• Парсинг объявлений по товару и городу\n"
        "• Мониторинг (в разработке)\n\n"
        "👇 Выбери действие в меню ниже:",
        reply_markup=get_main_keyboard()
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📖 Помощь:\n\n"
        "🔍 Парсинг - поиск объявлений на Avito\n"
        "📊 Мониторинг - скоро появится\n\n"
        "Команды:\n"
        "/start - Главное меню\n"
        "/help - Эта справка\n"
        "отмена - Отменить текущую операцию",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "📊 Мониторинг")
async def monitoring_button(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "⏳ Мониторинг в разработке.\n\n"
        "Функция будет доступна в следующем обновлении!",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "🔍 Парсинг")
async def start_parsing(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(ParserStates.waiting_for_product)
    await message.answer(
        "🔍 Введите название товара для поиска:\n\n"
        "Примеры: iphone 13, ноутбук, велосипед, шкаф",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(ParserStates.waiting_for_product)
async def get_product_name(message: Message, state: FSMContext):
    product = message.text.strip()

    if product.lower() == "отмена":
        await state.clear()
        await message.answer("❌ Поиск отменён.", reply_markup=get_main_keyboard())
        return

    if len(product) < 2:
        await message.answer("❌ Слишком короткое название (минимум 2 символа). Попробуйте ещё раз:")
        return

    await state.update_data(product=product)

    cities_list = "\n".join([f"• {city.title()}" for city in list(CITIES.keys())[:15]])
    await message.answer(
        f"✅ Товар: {product}\n\n"
        f"🏙 Теперь введите город:\n\n"
        f"Доступные города:\n{cities_list}\n\n"
        f"Примеры: Москва, СПб, Екатеринбург, Казань",
    )
    await state.set_state(ParserStates.waiting_for_city)


@dp.message(ParserStates.waiting_for_city)
async def get_city_and_parse(message: Message, state: FSMContext):
    city_input = message.text.lower().strip()

    if city_input == "отмена":
        await state.clear()
        await message.answer("❌ Поиск отменён.", reply_markup=get_main_keyboard())
        return

    # Поиск города в словаре
    city_slug = CITIES.get(city_input)
    city_name = city_input.title()

    if not city_slug:
        for key, value in CITIES.items():
            if city_input in key or key in city_input:
                city_slug = value
                city_name = key.title()
                break

    if not city_slug:
        await message.answer(
            "❌ Город не найден.\n\n"
            "Попробуйте один из этих:\n" +
            ", ".join(list(CITIES.keys())[:10]) +
            "\n\nИли напишите 'отмена' чтобы вернуться в меню"
        )
        return

    data = await state.get_data()
    product = data.get('product')

    # Имитация парсинга (реальный парсинг добавишь позже)
    await message.answer(
        f"🔎 Ищу '{product}' в городе {city_name}...\n\n"
        f"🔄 Парсинг запущен.\n"
        f"⏱ Ожидайте результаты через несколько секунд.\n\n"
        f"📌 Город: {city_name}\n"
        f"📌 Товар: {product}",
        reply_markup=get_main_keyboard()
    )

    await state.clear()


@dp.message(F.text.lower() == "отмена")
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()
        await message.answer("❌ Операция отменена.", reply_markup=get_main_keyboard())
    else:
        await message.answer("❌ Нет активных операций для отмены.", reply_markup=get_main_keyboard())


@dp.message()
async def unknown_message(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == ParserStates.waiting_for_product:
        await message.answer("🔍 Введите название товара (или напишите 'отмена'):")
    elif current_state == ParserStates.waiting_for_city:
        await message.answer("🏙 Введите город (или напишите 'отмена'):")
    else:
        await message.answer(
            "❓ Неизвестная команда.\n\n"
            "Используйте кнопки меню или команду /start",
            reply_markup=get_main_keyboard()
        )


# ==================== ЗАПУСК ПОЛЛИНГА (для локального теста) ====================
async def start_polling():
    """Запуск бота в режиме polling (для локального тестирования)"""
    print("🤖 Бот запущен в режиме polling...")
    try:
        me = await bot.get_me()
        print(f"✅ Бот подключен: @{me.username}")
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return
    await dp.start_polling(bot)


# ==================== FLASK ДЛЯ PYTHONANYWHERE ====================
# Переменная application нужна для PythonAnywhere
application = None


def init_flask():
    """Инициализация Flask-приложения для вебхука"""
    from flask import Flask, request, jsonify

    flask_app = Flask(__name__)

    @flask_app.route(f'/webhook/{BOT_TOKEN}', methods=['POST'])
    async def webhook():
        """Обработка вебхука от Telegram"""
        try:
            update_data = request.get_json()
            update = Update(**update_data)
            await dp.feed_update(bot, update)
            return 'OK', 200
        except Exception as e:
            logging.error(f"Ошибка вебхука: {e}")
            return 'Error', 500

    @flask_app.route('/')
    def index():
        return '🤖 Бот для парсинга Avito работает!'

    @flask_app.route('/health')
    def health():
        return jsonify({"status": "ok", "bot": "running"})

    @flask_app.route('/set_webhook')
    def set_webhook_route():
        """Установка вебхука (вызвать один раз в браузере)"""
        from urllib.parse import urljoin

        webhook_url = urljoin(f'https://{request.host}', f'/webhook/{BOT_TOKEN}')

        async def _set():
            return await bot.set_webhook(url=webhook_url)

        try:
            result = asyncio.run(_set())
            return f'✅ Вебхук установлен: {webhook_url}<br>Результат: {result}'
        except Exception as e:
            return f'❌ Ошибка: {e}'

    @flask_app.route('/delete_webhook')
    def delete_webhook_route():
        """Удаление вебхука"""

        async def _delete():
            return await bot.delete_webhook()

        try:
            result = asyncio.run(_delete())
            return f'✅ Вебхук удалён: {result}'
        except Exception as e:
            return f'❌ Ошибка: {e}'

    return flask_app


# Создаём Flask-приложение для PythonAnywhere
try:
    application = init_flask()
    print("✅ Flask-приложение создано, вебхук готов к работе")
except Exception as e:
    print(f"⚠️ Ошибка создания Flask-приложения: {e}")

# ==================== ТОЧКА ВХОДА ====================
if __name__ == "__main__":
    # При локальном запуске используем polling
    asyncio.run(start_polling())