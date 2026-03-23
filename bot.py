import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, LabeledPrice

TOKEN = "8632469190:AAH-h0nxeHHW_zd2S9C64VcLTJ9D1-3qPFc"
ADMIN_ID = 6160381202  # твой Telegram ID

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===== ХРАНЕНИЕ =====
user_data = {}

# ===== КНОПКИ =====

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Докс - 150⭐")],
        [KeyboardButton(text="Снос - 250⭐")],
        [KeyboardButton(text="Деф")]
    ],
    resize_keyboard=True
)

tariff_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="1 неделя - 100⭐")],
        [KeyboardButton(text="1 месяц - 250⭐")],
        [KeyboardButton(text="Навсегда - 400⭐")],
        [KeyboardButton(text="Назад")]
    ],
    resize_keyboard=True
)

# ===== СТАРТ =====

@dp.message(Command("start"))
async def start(msg: types.Message):
    await msg.answer("Выберите услугу:", reply_markup=main_kb)

# ===== ДЕФ =====

@dp.message(lambda msg: msg.text == "Деф")
async def subscription(msg: types.Message):
    await msg.answer("Выберите тариф:", reply_markup=tariff_kb)

# ===== НАЗАД =====

@dp.message(lambda msg: msg.text == "Назад")
async def back(msg: types.Message):
    await msg.answer("Главное меню:", reply_markup=main_kb)

# ===== ОПЛАТА =====

@dp.message(lambda msg: msg.text and "⭐" in msg.text)
async def buy(msg: types.Message):
    price_text = msg.text

    # сохраняем услугу
    user_data[msg.from_user.id] = {"service": price_text}

    # реальные цены
    if "150" in price_text:
        amount = 150
    elif "250" in price_text:
        amount = 250
    elif "100" in price_text:
        amount = 100
    elif "400" in price_text:
        amount = 400
    else:
        return await msg.answer("Ошибка цены")

    prices = [LabeledPrice(label=price_text, amount=amount)]

    await bot.send_invoice(
        chat_id=msg.chat.id,
        title="Оплата услуги",
        description=f"Вы выбрали: {price_text}",
        payload=price_text,
        provider_token="",
        currency="XTR",
        prices=prices
    )

# ===== ПОДТВЕРЖДЕНИЕ =====

@dp.pre_checkout_query()
async def process_pre_checkout(pre_checkout_query):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# ===== УСПЕШНАЯ ОПЛАТА =====

@dp.message(lambda msg: msg.successful_payment is not None)
async def success_payment(msg: types.Message):
    user_id = msg.from_user.id
    service = user_data.get(user_id, {}).get("service", "")

    # сообщение пользователю
    if "1 - 150" in service or "2 - 250" in service:
        await msg.answer(
            "✅ Оплата прошла успешно!\n\n"
            "Введите @username для услуги:\n"
            "Пример: @paveldurov"
        )
        user_data[user_id]["step"] = "get_username_service"
    else:
        await msg.answer(
            "✅ Оплата прошла успешно!\n\n"
            "Для какого аккаунта нужна защита?\n"
            "Пример: @paveldurov"
        )
        user_data[user_id]["step"] = "get_username_def"

    # сообщение админу
    await bot.send_message(
        ADMIN_ID,
        f"💰 Оплата\n\n"
        f"👤 @{msg.from_user.username}\n"
        f"🆔 {msg.from_user.id}\n"
        f"📦 {service}"
    )

# ===== ПОЛУЧЕНИЕ USERNAME =====

@dp.message()
async def handle_username(msg: types.Message):
    user_id = msg.from_user.id
    step = user_data.get(user_id, {}).get("step")

    if step in ["get_username_service", "get_username_def"]:
        username = msg.text

        await msg.answer("✅ Заявка принята!")

        # админу
        await bot.send_message(
            ADMIN_ID,
            f"📩 Новая заявка\n\n"
            f"👤 @{msg.from_user.username}\n"
            f"🆔 {msg.from_user.id}\n"
            f"📦 {user_data[user_id]['service']}\n"
            f"🎯 Username: {username}"
        )

        # очистка
        user_data[user_id] = {}

# ===== ЗАПУСК =====

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
