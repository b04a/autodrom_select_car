import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

# Токен вашего бота
API_TOKEN = 'XXX'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Хэндлер команды /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    await message.answer("""
        Привет! Почекаем тачки?
        /help - Узнать о способности бота
    """)

@dp.message(Command("help"))
async def help(message: Message):
    await message.answer("/help - Узнать о способности бота\n"
                         "/search_car - Поиск машины по запросу")

@dp.message(Command("search_car"))
async def search_car(message: Message):
    await message.answer("""
        Давай я подберу тебе машину!
        В какой цене искать?
        
        1 число - минимальная цена
        2 число - максимальная цена 
        Напиши в формате:
        (100000 300000)
        
        Где 1 число 
    """)


# Асинхронный запуск бота
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())