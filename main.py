import random
import os
import sqlite3
import asyncio
from aiogram.utils import executor
import logging
from aiogram import Bot, Dispatcher, types
import time
from secret import TOKEN
from db_creation import create_locations_db, create_mobs_db, create_person_db, create_items_db, create_items_links_db, \
    create_locations_links_db, create_items_sellers_db
from db_filling import fill_items, fill_locations, give_open_bonus, fill_location_reachability, fill_items_sellers
import utils
import commands

connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
cursor = connect.cursor()

create_locations_db()
create_locations_links_db()
create_mobs_db()
create_person_db()
create_items_db()
create_items_links_db()
create_items_sellers_db()

fill_items()
fill_items_sellers()
fill_locations()
fill_location_reachability()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    await message.answer(text=utils.HELPER_TEXT)


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    cursor.execute(f'DELETE from person where UserId = {message.chat.id}')
    cursor.execute(f'DELETE from items_links where UserId = {message.chat.id}')
    cursor.execute('INSERT INTO person (UserId, Nickname) VALUES (?, ?)',
                   [message.chat.id, message.from_user.username])
    connect.commit()
    give_open_bonus(message)
    await message.answer(text=utils.HELLO_TEXT)


@dp.message_handler(commands=["stats_player"])
async def stats_player(message: types.Message):
    cursor.execute(f"select Nickname, LEVEL, HP, CurHP, Money, Attack, MagicAttack, XP, Armour, MagicArmour, "
                   f"LocationID from person where UserId = {message.chat.id}")
    person_info = list(cursor.fetchall()[0])
    cursor.execute(f'select LocationName, LocationType from locations where LocationID = {person_info[10]}')
    location_info = list(cursor.fetchall()[0])
    await message.answer(text=commands.create_stats_player_text(person_info, location_info))


@dp.message_handler(commands=["locations"])
async def stats_locations(message: types.Message):
    cursor.execute(f'select LocationName, LocationType, XCoord, YCoord from locations')
    locations = list(cursor.fetchall())
    await message.answer(text=commands.create_stats_location_text(locations))


@dp.message_handler(commands=["inventory"])
async def inventory(message: types.Message):
    await message.answer(text=commands.create_inventory_text(cursor, message))


@dp.message_handler(commands=["items"])
async def inventory(message: types.Message):
    cursor.execute(f'select LocationID from person where UserID = {message.chat.id}')
    location_id = cursor.fetchall()[0][0]
    cursor.execute(f'select LocationName, LocationType from locations where LocationID = {location_id}')
    location_name, location_type = cursor.fetchall()[0]
    if location_type == "dungeon":
        await message.answer(text=utils.FORBIDDEN_TEXT)
    else:
        await message.answer(text=commands.create_seller_text(cursor, message))


@dp.message_handler(commands=["go"])
async def inventory(message: types.Message):
    cursor.execute(f'select LocationID from person where UserID = {message.chat.id}')
    cur_location = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select SecondLocationID, MoveDuration from locations_links where FirstLocationID = {cur_location}')
    to = list(cursor.fetchall())
    markup = types.InlineKeyboardMarkup(row_width=4)
    for location in to:
        cursor.execute(f'select LocationName from locations where LocationID = {location[0]}')
        location_name = list(cursor.fetchall()[0])[0]
        item = types.InlineKeyboardButton(f"{location_name}", callback_data=f"move_to_{location_name}")
        markup.row(item)
    await message.answer(text="В какой город отправляемся?", reply_markup=markup)


@dp.callback_query_handler(text_contains=["move_to_Novigrad"])
async def move_to_Novigrad(call: types.CallbackQuery):
    cursor.execute(f'select LocationID from person where UserID = {call.message.chat.id}')
    cur_location = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select LocationID from locations where LocationName = "Novigrad"')
    novigrad_id = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select MoveDuration from locations_links where FirstLocationID = {cur_location} and '
                   f'SecondLocationID = {novigrad_id}')
    duration = list(cursor.fetchall()[0])[0]
    await call.message.answer(text=f"Идём в Novigrad. Пусть займёт {duration} секунд")
    await call.message.answer(text=str(duration))
    for i in range(duration - 1, -1, -1):
        time.sleep(1)
        await call.message.answer(text=str(i))
    cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
    max_hp, cur_hp = cursor.fetchall()[0]
    cursor.execute(f'update person set LocationID = {novigrad_id}, CurHP = {max(max_hp, cur_hp)} '
                   f'where UserID = {call.message.chat.id}')
    connect.commit()
    await call.message.answer(text="Пришли в Novigrad, здесь можно купить оружие. Здоровье восстановлено!")


@dp.callback_query_handler(text_contains=["move_to_White_Orchard"])
async def move_to_White_Orchard(call: types.CallbackQuery):
    cursor.execute(f'select LocationID from person where UserID = {call.message.chat.id}')
    cur_location = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select LocationID from locations where LocationName = "White_Orchard"')
    White_Orchard_id = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select MoveDuration from locations_links where FirstLocationID = {cur_location} and '
                   f'SecondLocationID = {White_Orchard_id}')
    duration = list(cursor.fetchall()[0])[0]
    await call.message.answer(text=f"Идём в White_Orchard. Пусть займёт {duration} секунд")
    await call.message.answer(text=str(duration))
    for i in range(duration - 1, -1, -1):
        time.sleep(1)
        await call.message.answer(text=str(i))
    cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
    max_hp, cur_hp = cursor.fetchall()[0]
    cursor.execute(f'update person set LocationID = {White_Orchard_id}, CurHP = {max(max_hp, cur_hp)} '
                   f'where UserID = {call.message.chat.id}')
    connect.commit()
    await call.message.answer(text="Пришли в White_Orchard, здесь можно купить броню, шлем, сапоги и наручи. "
                                   "Здоровье восстановлено!")


@dp.callback_query_handler(text_contains=["move_to_Kaer_Morhen"])
async def move_to_Kaer_Morhen(call: types.CallbackQuery):
    cursor.execute(f'select LocationID from person where UserID = {call.message.chat.id}')
    cur_location = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select LocationID from locations where LocationName = "Kaer_Morhen"')
    center_id = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select MoveDuration from locations_links where FirstLocationID = {cur_location} and '
                   f'SecondLocationID = {center_id}')
    duration = list(cursor.fetchall()[0])[0]
    await call.message.answer(text=f"Идём в Kaer_Morhen. Пусть займёт {duration} секунд")
    await call.message.answer(text=str(duration))
    for i in range(duration - 1, -1, -1):
        time.sleep(1)
        await call.message.answer(text=str(i))
    cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
    max_hp, cur_hp = cursor.fetchall()[0]
    cursor.execute(f'update person set LocationID = {center_id}, CurHP = {max(max_hp, cur_hp)} '
                   f'where UserID = {call.message.chat.id}')
    connect.commit()
    await call.message.answer(text="Пришли в Kaer_Morhen, здесь можно купить зелья. Здоровье восстановлено!")


@dp.message_handler()
async def unknown_message(message: types.Message):
    """Ответ на любое неожидаемое сообщение"""
    await message.answer(text=utils.UNKNOWN_TEST)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())