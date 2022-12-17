import random
import os
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from secret import TOKEN
from db_creation import create_locations_db, create_mobs_db, create_person_db, create_items_db, create_items_links_db
from db_filling import fill_items, fill_locations
import utils
import commands

connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
cursor = connect.cursor()

create_locations_db()
create_mobs_db()
create_person_db()
create_items_db()
create_items_links_db()

fill_items()
fill_locations()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["help"])
async def start(message: types.Message):
    await message.answer(text=utils.HELPER_TEXT)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    connect.execute('INSERT INTO person (UserId, Nickname) VALUES (?, ?)',
                    [message.chat.id, message.from_user.username])
    connect.commit()
    cursor.execute('INSERT INTO items_links (UserID, ItemID, quantity, IsActive)'
                   'values (?, ?, ?, ?)',
                   [message.chat.id, 1, 1, 1])
    connect.commit()  # бонусное зелье-здоровье
    cursor.execute('INSERT INTO items_links (UserID, ItemID, quantity, IsActive)'
                   'values (?, ?, ?, ?)',
                   [message.chat.id, 2, 1, 1])
    connect.commit()  # бонусное зелье-мана
    await message.answer(text=utils.HELLO_TEXT)


@dp.message_handler(commands=["stats_player"])
async def stats_player(message: types.Message):
    cursor.execute(f"select Nickname, LEVEL, HP, CurHP, Money, Attack, MagicAttack, XP, Armour, MagicArmour, "
                   f"LocationID from person where UserId = {message.chat.id}")
    person_info = list(cursor.fetchall()[0])
    cursor.execute(f'select LocationName, LocationType from locations where LocationID = {person_info[10]}')
    location_info = list(cursor.fetchall()[0])
    await message.answer(text=commands.create_stats_player_text(person_info, location_info))


@dp.message_handler(commands=["stats_locations"])
async def stats_locations(message: types.Message):
    cursor.execute(f'select LocationName, LocationType, XCoord, YCoord from locations '
                   f'where LocationType = city')
    locations = list(cursor.fetchall())
    await message.answer(text=commands.create_stats_location_text(locations))


@dp.message_handler(commands=["inventory"])
async def inventory(message: types.Message):
    await message.answer(text=commands.create_inventory_text(cursor, message))


@dp.message_handler()
async def unknown_message(message: types.Message):
    """Ответ на любое неожидаемое сообщение"""
    await message.answer(text=utils.UNKNOWN_TEST)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
