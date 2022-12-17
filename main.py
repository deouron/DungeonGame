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
    await message.answer(text=commands.create_stats_location_text(cursor))


@dp.message_handler(commands=["inventory"])
async def inventory(message: types.Message):
    await message.answer(text=commands.create_inventory_text(cursor, message))


@dp.message_handler(commands=["garments"])
async def garments(message: types.Message):
    await message.answer(text=commands.create_garments_text(cursor, message))


@dp.message_handler(commands=["put_on"])
async def put_on(message: types.Message):
    cursor.execute(f'select LocationID from person where UserID = {message.chat.id}')
    location_id = cursor.fetchall()[0][0]
    cursor.execute(f'select LocationType from locations where LocationID = {location_id}')
    location_type = cursor.fetchall()[0][0]
    if location_type == "dungeon":
        await message.answer(text=utils.FORBIDDEN_TEXT)
    else:
        cursor.execute(f'select ItemID from items_links where UserID = {message.chat.id} and IsActive = 0')
        user_items = list(cursor.fetchall())
        if len(user_items) == 0:
            await message.answer(text=utils.EMPTY_INVENTORY_TEXT + 'или все предметы используются')
        else:
            markup = types.InlineKeyboardMarkup(row_width=4)
            can_put_on = False
            for item in user_items:
                cursor.execute(f'select ItemType from items where ItemID = {item[0]}')
                cur_item = cursor.fetchall()[0][0]
                if cur_item[0] == 'potion':
                    continue
                can_put_on = True
                markup = types.InlineKeyboardMarkup(row_width=4)
                item = types.InlineKeyboardButton(f"{item[0]}", callback_data=f"use_{item[0]}")
                markup.row(item)
            if not can_put_on:
                await message.answer(text=utils.NO_GARMENTS_TEXT + 'или все предметы используются')
            else:
                await message.answer(text=commands.create_garments_text(cursor, message) + "\n" +
                                          'Выбери предмет, который хочешь использовать (старый предмет такого же '
                                          'типа станет неактивным)',
                                     reply_markup=markup)


@dp.callback_query_handler(text_contains=["use_"])
async def buy_item(call: types.CallbackQuery):
    item_id = call.data.replace('use_', '')
    await call.message.answer(text=commands.use_item(item_id, cursor, connect, call.message))


@dp.message_handler(commands=["items"])
async def inventory(message: types.Message):
    cursor.execute(f'select LocationID from person where UserID = {message.chat.id}')
    location_id = cursor.fetchall()[0][0]
    cursor.execute(f'select LocationName, LocationType from locations where LocationID = {location_id}')
    location_name, location_type = cursor.fetchall()[0]
    if location_type == "dungeon":
        await message.answer(text=utils.FORBIDDEN_TEXT)
    elif location_name == 'Kaer_Morhen':
        markup = types.InlineKeyboardMarkup(row_width=4)
        item = types.InlineKeyboardButton(f"Купить", callback_data=f"buy_item_Kaer_Morhen")
        markup.row(item)
        item = types.InlineKeyboardButton(f"Продать", callback_data=f"sell_item_Kaer_Morhen")
        markup.row(item)
        await message.answer(text=commands.create_items_text(cursor, message), reply_markup=markup)
    elif location_name == 'Novigrad':
        markup = types.InlineKeyboardMarkup(row_width=4)
        item = types.InlineKeyboardButton(f"Купить", callback_data=f"buy_item_Novigrad")
        markup.row(item)
        item = types.InlineKeyboardButton(f"Продать", callback_data=f"sell_item_Novigrad")
        markup.row(item)
        await message.answer(text=commands.create_items_text(cursor, message), reply_markup=markup)
    elif location_name == 'White_Orchard':
        markup = types.InlineKeyboardMarkup(row_width=4)
        item = types.InlineKeyboardButton(f"Купить", callback_data=f"buy_item_White_Orchard")
        markup.row(item)
        item = types.InlineKeyboardButton(f"Продать", callback_data=f"sell_item_White_Orchard")
        markup.row(item)
        await message.answer(text=commands.create_items_text(cursor, message), reply_markup=markup)


@dp.callback_query_handler(text_contains=["buy_item_Kaer_Morhen"])
async def buy_item_Kaer_Morhen(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"buy_1")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"buy_2")
    markup.row(item)
    await call.message.answer(text=commands.create_items_text(cursor, call.message) + "\nВыбери предмет для покупки",
                              reply_markup=markup)


@dp.callback_query_handler(text_contains=["sell_item_Kaer_Morhen"])
async def sell_item_Kaer_Morhen(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"sell_1")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"sell_2")
    markup.row(item)
    await call.message.answer(text=commands.create_items_text(cursor, call.message) + "\nВыбери предмет для продажи",
                              reply_markup=markup)


@dp.callback_query_handler(text_contains=["buy_item_Novigrad"])
async def buy_item_Novigrad(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"buy_8")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"buy_9")
    markup.row(item)
    await call.message.answer(text=commands.create_items_text(cursor, call.message) + "\nВыбери предмет для покупки",
                              reply_markup=markup)


@dp.callback_query_handler(text_contains=["sell_item_Novigrad"])
async def sell_item_Novigrad(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"sell_8")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"sell_9")
    markup.row(item)
    await call.message.answer(text=commands.create_items_text(cursor, call.message) + "\nВыбери предмет для продажи",
                              reply_markup=markup)


@dp.callback_query_handler(text_contains=["buy_item_White_Orchard"])
async def buy_item_White_Orchard(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"buy_3")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"buy_4")
    markup.row(item)
    item = types.InlineKeyboardButton(f"3", callback_data=f"buy_5")
    markup.row(item)
    item = types.InlineKeyboardButton(f"4", callback_data=f"buy_6")
    markup.row(item)
    item = types.InlineKeyboardButton(f"5", callback_data=f"buy_7")
    markup.row(item)
    item = types.InlineKeyboardButton(f"6", callback_data=f"buy_10")
    markup.row(item)
    await call.message.answer(text=commands.create_items_text(cursor, call.message) + "\nВыбери предмет для покупки",
                              reply_markup=markup)


@dp.callback_query_handler(text_contains=["sell_item_White_Orchard"])
async def sell_item_Novigrad(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"sell_3")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"sell_4")
    markup.row(item)
    item = types.InlineKeyboardButton(f"3", callback_data=f"sell_5")
    markup.row(item)
    item = types.InlineKeyboardButton(f"4", callback_data=f"sell_6")
    markup.row(item)
    item = types.InlineKeyboardButton(f"5", callback_data=f"sell_7")
    markup.row(item)
    await call.message.answer(text=commands.create_items_text(cursor, call.message) + "\nВыбери предмет для продажи",
                              reply_markup=markup)


@dp.callback_query_handler(text_contains=["buy_"])
async def buy_item(call: types.CallbackQuery):
    item_id = call.data.replace('buy_', '')
    await call.message.answer(text=commands.buy_item(item_id, cursor, connect, call.message))


@dp.callback_query_handler(text_contains=["sell_"])
async def sell_item(call: types.CallbackQuery):
    item_id = call.data.replace('sell_', '')
    await call.message.answer(text=commands.sell_item(item_id, cursor, connect, call.message))


@dp.message_handler(commands=["go"])
async def go(message: types.Message):
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
    await call.message.answer(text=f"Идём в Novigrad. Путь займёт {duration} секунд")
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
    await call.message.answer(text=f"Идём в White_Orchard. Путь займёт {duration} секунд")
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
    await call.message.answer(text=f"Идём в Kaer_Morhen. Псть займёт {duration} секунд")
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
