import asyncio
import subprocess
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage


# Токен вашего бота
API_TOKEN = 'XXXX'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Определение состояний
class SearchCarState(StatesGroup):
    waiting_for_price_range = State()


# Клавиатура с кнопками
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚗 Найти машину")],
    ],
    resize_keyboard=True
)


# Хэндлер команды /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await bot.send_photo(
        chat_id=message.chat.id,
        photo="https://mir-s3-cdn-cf.behance.net/project_modules/1400_opt_1/b2b63a69331555.5b7d61c8a04d5.jpg",
        # Ссылка на изображение или файл
        caption="Привет! Я бот для поиска машин на основе сервиса drom.ru! Открывай меню!",
        reply_markup=main_keyboard
    )


# Хэндлер кнопки "🚗 Найти машину"
@dp.message(F.text == "🚗 Найти машину")
async def find_car_command(message: Message, state: FSMContext):
    await message.answer("""
        В каком ценовом диапозоне ищем?
        Напиши минимальную цену и максимальную
        В формате: 100000 200000
    """)
    # Устанавливаем состояние ожидания диапазона цен
    await state.set_state(SearchCarState.waiting_for_price_range)


# Обработка ввода диапазона цен
@dp.message(SearchCarState.waiting_for_price_range)
async def process_price_range(message: Message, state: FSMContext):
    try:
        # Парсим введенные данные
        min_price, max_price = map(int, message.text.split())

        # Вывод в чат
        await message.answer(f"Ищем машины в диапазоне от {min_price} до {max_price} рублей.")

        # Запуск Playwright скрипта
        subprocess.Popen(["python", "method2.py", str(min_price), str(max_price)])

        # Завершаем состояние
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите данные в правильном формате: 100000 200000")


# Асинхронный запуск бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
