from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime
import json
import os

from fpdf import FPDF  # PDF генерация

API_TOKEN = os.getenv("API_TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Загрузка данных Арканов
with open('data/arcanes.json', 'r', encoding='utf-8') as f:
    ARCANES = json.load(f)

def calculate_arcanes(date_str):
    digits = [int(d) for d in date_str if d.isdigit()]
    s1 = sum(digits)
    ar1 = s1 % 22 or 22
    ar2 = sum([int(d) for d in str(s1)]) % 22 or 22
    ar3 = (ar1 + ar2) % 22 or 22
    return [ar1, ar2, ar3]

def generate_pdf(name, birth_date, arcanes):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Матрица Судьбы", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Имя: {name}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Дата рождения: {birth_date}", ln=True, align='L')
    pdf.ln(10)

    for arc in arcanes:
        name = ARCANES[str(arc)]['name']
        desc = ARCANES[str(arc)]['description']
        pdf.multi_cell(0, 10, txt=f"Аркан {arc}: {name}\n{desc}\n")
        pdf.ln(2)

    path = f"output_{birth_date.replace('.', '-')}.pdf"
    pdf.output(path)
    return path

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton('🧮 Рассчитать Матрицу'))
    await message.answer("👋 Привет! Я бот по Матрице Судьбы. Нажми кнопку ниже, чтобы начать:", reply_markup=kb)

@dp.message_handler(lambda msg: msg.text == '🧮 Рассчитать Матрицу')
async def ask_date(message: types.Message):
    await message.answer("Введите дату рождения в формате ДД.ММ.ГГГГ (например, 12.07.1991):")

@dp.message_handler()
async def handle_date(message: types.Message):
    try:
        date_obj = datetime.strptime(message.text, '%d.%m.%Y')
        arcs = calculate_arcanes(message.text)
        text = "\n".join([f"Аркан {arc}: {ARCANES[str(arc)]['name']} — {ARCANES[str(arc)]['description']}" for arc in arcs])
        await message.answer(f"✨ Твоя Матрица Судьбы:\n{text}")

        # PDF генерация и отправка
        pdf_path = generate_pdf(message.from_user.full_name, message.text, arcs)
        with open(pdf_path, 'rb') as doc:
            await message.answer_document(doc)
        os.remove(pdf_path)

    except Exception as e:
        await message.answer("⚠️ Ошибка! Убедитесь, что дата введена в формате ДД.ММ.ГГГГ")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
