import random
import os
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from secret import TOKEN
from create_db import create_locations_db, create_mobs_db, create_person_db, create_items_db, create_items_links_db
import utils

create_locations_db()
create_mobs_db()
create_person_db()
create_items_db()
create_items_links_db()

connect_locations = sqlite3.connect('dbs/locations.db', check_same_thread=False)
cursor_locations = connect_locations.cursor()
connect_mobs = sqlite3.connect('dbs/mobs.db', check_same_thread=False)
cursor_mobs = connect_mobs.cursor()
connect_person = sqlite3.connect('dbs/person.db', check_same_thread=False)
cursor_person = connect_person.cursor()
connect_items = sqlite3.connect('dbs/items.db', check_same_thread=False)
cursor_items = connect_items.cursor()
connect_items_links = sqlite3.connect('dbs/items_links.db', check_same_thread=False)
cursor_items_links = connect_items_links.cursor()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["help"])
async def start(message: types.Message):
    await message.answer(text=utils.HELPER_TEXT)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    cursor_person.execute('INSERT INTO person (ChatId, Nickname) VALUES (?, ?);',
                          [message.chat.id, message.from_user.username])
    connect_person.commit()
    await message.answer(text=utils.HELLO_TEXT)


@dp.message_handler()
async def unknown_message(message: types.Message):
    """Ответ на любое неожидаемое сообщение"""
    await message.answer(text=utils.UNKNOWN_TEST)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())