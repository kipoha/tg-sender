import io
import aiohttp
import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import Message, BotCommand, PhotoSize
from aiogram.filters import Command, CommandStart

from decouple import config as cfg


BOT_TOKEN = str(cfg("TELEGRAM_BOT_TOKEN"))
DJANGO_API_URL = "http://127.0.0.1:8000/api/v1/messages/create/"

dp = Dispatcher()
bot = Bot(BOT_TOKEN)


async def send_message_to_django(chat_id, sender, text, images):
    data = aiohttp.FormData()
    data.add_field("chat_id", str(chat_id))
    data.add_field("sender", sender)
    data.add_field("text", text)

    if images:
        for photo in images:
            if isinstance(photo, PhotoSize):
                photo_bytes = await bot.download(photo)
                photo_io = io.BytesIO(photo_bytes.read())
                data.add_field(
                    "images",
                    photo_io,
                    filename=f"{photo.file_id}.jpg",
                    content_type="image/jpeg"
                )

    async with aiohttp.ClientSession() as session:
        async with session.post(DJANGO_API_URL, data=data) as response:
            print(data.__dict__)
            return await response.json()

@dp.message(CommandStart())
async def root(message: Message):
    await message.answer("Hello")


@dp.message(Command("get_chat_id"))
async def get_chat_id(message: Message):
    await message.answer(
        f"Chat id: `{message.chat.id}`",
        parse_mode="Markdown"
    )


@dp.message()
async def message_handler(message: Message):
    chat_id = message.chat.id
    sender = message.from_user.username or "Неизвестный"
    text = message.text.lower() if message.text else "Нет текста"

    images = message.photo or []
    await send_message_to_django(chat_id, sender, text, images)


async def on_startup():
    print("Bot Started")
   

async def main() -> None:
    await bot.set_my_commands([
        BotCommand(command="get_chat_id", description="Get chat id")
    ])
    await on_startup()
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__": 
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
