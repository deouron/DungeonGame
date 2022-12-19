import random
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
import time
from db_creation import create_locations_db, create_mobs_db, create_person_db, create_items_db, create_items_links_db, \
    create_locations_links_db, create_items_sellers_db
from db_filling import fill_items, fill_locations, give_open_bonus, fill_location_reachability, fill_items_sellers, \
    fill_mobs
import utils
import commands
import secret

connect = sqlite3.connect('data.db', check_same_thread=False)
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
fill_mobs()

logging.basicConfig(level=logging.INFO)
bot = Bot(token=secret.TOKEN)
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


@dp.message_handler(commands=["potions"])
async def potions(message: types.Message):
    await message.answer(text=commands.create_potions_text(cursor, message))


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
            await message.answer(text=utils.EMPTY_INVENTORY_TEXT + " " + utils.OR_ALL_ITEMS_ARE_USED_TEXT)
        else:
            markup = types.InlineKeyboardMarkup(row_width=4)
            can_put_on = False
            for item in user_items:
                cursor.execute(f'select ItemType from items where ItemID = {item[0]}')
                ItemType = cursor.fetchall()[0][0]
                if ItemType == 'potion':
                    continue
                can_put_on = True
                item = types.InlineKeyboardButton(f"{item[0]}", callback_data=f"use_{item[0]}")
                markup.row(item)
            if not can_put_on:
                await message.answer(text=utils.NO_GARMENTS_TEXT + " " + utils.OR_ALL_ITEMS_ARE_USED_TEXT)
            else:
                await message.answer(
                    text=commands.create_garments_text(cursor, message) + "\n" + utils.CHOOSE_ITEM_TO_USE_TEXT,
                    reply_markup=markup)


@dp.callback_query_handler(text_contains=["use_"])
async def use_item(call: types.CallbackQuery):
    item_id = call.data.replace('use_', '')
    await call.message.answer(text=commands.use_item(item_id, cursor, connect, call.message))


@dp.message_handler(commands=["take_off"])
async def take_off(message: types.Message):
    cursor.execute(f'select LocationID from person where UserID = {message.chat.id}')
    location_id = cursor.fetchall()[0][0]
    cursor.execute(f'select LocationType from locations where LocationID = {location_id}')
    location_type = cursor.fetchall()[0][0]
    if location_type == "dungeon":
        await message.answer(text=utils.FORBIDDEN_TEXT)
    else:
        cursor.execute(f'select ItemID from items_links where UserID = {message.chat.id} and IsActive = 1')
        user_items = list(cursor.fetchall())
        if len(user_items) == 0:
            await message.answer(text=utils.EMPTY_INVENTORY_TEXT + " " + utils.OR_ALL_ITEMS_ARE_NOT_USED_TEXT)
        else:
            markup = types.InlineKeyboardMarkup(row_width=4)
            can_put_on = False
            for item in user_items:
                cursor.execute(f'select ItemType from items where ItemID = {item[0]}')
                ItemType = cursor.fetchall()[0][0]
                if ItemType == 'potion':
                    continue
                can_put_on = True
                item = types.InlineKeyboardButton(f"{item[0]}", callback_data=f"take_off_{item[0]}")
                markup.row(item)
            if not can_put_on:
                await message.answer(text=utils.NO_GARMENTS_TEXT + " " + utils.OR_ALL_ITEMS_ARE_NOT_USED_TEXT)
            else:
                await message.answer(
                    text=commands.create_garments_text(cursor, message) + "\n" + utils.CHOOSE_ITEM_TO_TAKE_OFF_TEXT,
                    reply_markup=markup)


@dp.callback_query_handler(text_contains=["take_off_"])
async def take_off_item(call: types.CallbackQuery):
    item_id = call.data.replace('take_off_', '')
    await call.message.answer(text=commands.take_off_item(item_id, cursor, connect, call.message))


@dp.message_handler(commands=["items"])
async def items(message: types.Message):
    cursor.execute(f'select LocationID from person where UserID = {message.chat.id}')
    location_id = cursor.fetchall()[0][0]
    cursor.execute(f'select LocationName, LocationType from locations where LocationID = {location_id}')
    location_name, location_type = cursor.fetchall()[0]
    if location_type == "dungeon":
        await message.answer(text=utils.FORBIDDEN_TEXT)
    elif location_name == 'Kaer_Morhen':
        markup = types.InlineKeyboardMarkup(row_width=4)
        item = types.InlineKeyboardButton(utils.BUY_TEXT, callback_data=f"buy_item_Kaer_Morhen")
        markup.row(item)
        item = types.InlineKeyboardButton(utils.SELL_TEXT, callback_data=f"sell_item_Kaer_Morhen")
        markup.row(item)
        await message.answer(text=commands.create_items_text(cursor, message), reply_markup=markup)
    elif location_name == 'Novigrad':
        markup = types.InlineKeyboardMarkup(row_width=4)
        item = types.InlineKeyboardButton(utils.BUY_TEXT, callback_data=f"buy_item_Novigrad")
        markup.row(item)
        item = types.InlineKeyboardButton(utils.SELL_TEXT, callback_data=f"sell_item_Novigrad")
        markup.row(item)
        await message.answer(text=commands.create_items_text(cursor, message), reply_markup=markup)
    elif location_name == 'White_Orchard':
        markup = types.InlineKeyboardMarkup(row_width=4)
        item = types.InlineKeyboardButton(utils.BUY_TEXT, callback_data=f"buy_item_White_Orchard")
        markup.row(item)
        item = types.InlineKeyboardButton(utils.SELL_TEXT, callback_data=f"sell_item_White_Orchard")
        markup.row(item)
        await message.answer(text=commands.create_items_text(cursor, message), reply_markup=markup)


@dp.callback_query_handler(text_contains=["buy_item_Kaer_Morhen"])
async def buy_item_Kaer_Morhen(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"buy_1")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"buy_2")
    markup.row(item)
    await call.message.answer(
        text=commands.create_items_text(cursor, call.message) + "\n" + utils.CHOOSE_ITEM_TO_BUY_TEXT,
        reply_markup=markup)


@dp.callback_query_handler(text_contains=["sell_item_Kaer_Morhen"])
async def sell_item_Kaer_Morhen(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"sell_1")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"sell_2")
    markup.row(item)
    await call.message.answer(
        text=commands.create_items_text(cursor, call.message) + "\n" + utils.CHOOSE_ITEM_TO_SELL_TEXT,
        reply_markup=markup)


@dp.callback_query_handler(text_contains=["buy_item_Novigrad"])
async def buy_item_Novigrad(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"buy_8")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"buy_9")
    markup.row(item)
    item = types.InlineKeyboardButton(f"3", callback_data=f"buy_11")
    markup.row(item)
    item = types.InlineKeyboardButton(f"4", callback_data=f"buy_12")
    markup.row(item)
    await call.message.answer(
        text=commands.create_items_text(cursor, call.message) + "\n" + utils.CHOOSE_ITEM_TO_BUY_TEXT,
        reply_markup=markup)


@dp.callback_query_handler(text_contains=["sell_item_Novigrad"])
async def sell_item_Novigrad(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"1", callback_data=f"sell_8")
    markup.row(item)
    item = types.InlineKeyboardButton(f"2", callback_data=f"sell_9")
    markup.row(item)
    item = types.InlineKeyboardButton(f"3", callback_data=f"buy_11")
    markup.row(item)
    item = types.InlineKeyboardButton(f"4", callback_data=f"buy_12")
    markup.row(item)
    await call.message.answer(
        text=commands.create_items_text(cursor, call.message) + "\n" + utils.CHOOSE_ITEM_TO_SELL_TEXT,
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
    await call.message.answer(
        text=commands.create_items_text(cursor, call.message) + "\n" + utils.CHOOSE_ITEM_TO_BUY_TEXT,
        reply_markup=markup)


@dp.callback_query_handler(text_contains=["sell_item_White_Orchard"])
async def sell_item_White_Orchard(call: types.CallbackQuery):
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
    item = types.InlineKeyboardButton(f"6", callback_data=f"sell_10")
    markup.row(item)
    await call.message.answer(
        text=commands.create_items_text(cursor, call.message) + "\n" + utils.CHOOSE_ITEM_TO_SELL_TEXT,
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
    cur_location = cursor.fetchall()[0][0]
    cursor.execute(f'select LocationName, LocationType from locations where LocationID = {cur_location}')
    location_name, location_type = cursor.fetchall()[0]
    if location_type == "dungeon":
        await message.answer(text=utils.FORBIDDEN_TEXT)
    else:
        cursor.execute(
            f'select SecondLocationID, MoveDuration from locations_links where FirstLocationID = {cur_location}')
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
    await call.message.answer(text=utils.create_duration_text("Novigrad", duration))
    await call.message.answer(text=str(duration))
    for i in range(duration - 1, -1, -1):
        time.sleep(1)
        await call.message.answer(text=str(i))
    cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
    max_hp, cur_hp = cursor.fetchall()[0]
    cursor.execute(f'update person set LocationID = {novigrad_id}, CurHP = {max(max_hp, cur_hp)} '
                   f'where UserID = {call.message.chat.id}')
    connect.commit()
    await call.message.answer(text=utils.Novigrad_ARRIVAL_TEXT)


@dp.callback_query_handler(text_contains=["move_to_White_Orchard"])
async def move_to_White_Orchard(call: types.CallbackQuery):
    cursor.execute(f'select LocationID from person where UserID = {call.message.chat.id}')
    cur_location = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select LocationID from locations where LocationName = "White_Orchard"')
    White_Orchard_id = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select MoveDuration from locations_links where FirstLocationID = {cur_location} and '
                   f'SecondLocationID = {White_Orchard_id}')
    duration = list(cursor.fetchall()[0])[0]
    await call.message.answer(text=utils.create_duration_text("White_Orchard", duration))
    await call.message.answer(text=str(duration))
    for i in range(duration - 1, -1, -1):
        time.sleep(1)
        await call.message.answer(text=str(i))
    cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
    max_hp, cur_hp = cursor.fetchall()[0]
    cursor.execute(f'update person set LocationID = {White_Orchard_id}, CurHP = {max(max_hp, cur_hp)} '
                   f'where UserID = {call.message.chat.id}')
    connect.commit()
    await call.message.answer(text=utils.White_Orchard_ARRIVAL_TEXT)


@dp.callback_query_handler(text_contains=["move_to_Kaer_Morhen"])
async def move_to_Kaer_Morhen(call: types.CallbackQuery):
    cursor.execute(f'select LocationID from person where UserID = {call.message.chat.id}')
    cur_location = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select LocationID from locations where LocationName = "Kaer_Morhen"')
    Kaer_Morhen_id = list(cursor.fetchall()[0])[0]
    cursor.execute(f'select MoveDuration from locations_links where FirstLocationID = {cur_location} and '
                   f'SecondLocationID = {Kaer_Morhen_id}')
    duration = list(cursor.fetchall()[0])[0]
    await call.message.answer(text=utils.create_duration_text("Kaer_Morhen", duration))
    await call.message.answer(text=str(duration))
    for i in range(duration - 1, -1, -1):
        time.sleep(1)
        await call.message.answer(text=str(i))
    cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
    max_hp, cur_hp = cursor.fetchall()[0]
    cursor.execute(f'update person set LocationID = {Kaer_Morhen_id}, CurHP = {max(max_hp, cur_hp)} '
                   f'where UserID = {call.message.chat.id}')
    connect.commit()
    await call.message.answer(text=utils.Kaer_Morhen_ARRIVAL_TEXT)


@dp.callback_query_handler(text_contains=["move_to_Skellige"])
async def move_to_Skellige(call: types.CallbackQuery):
    cursor.execute(f'select LocationID from person where UserID = {call.message.chat.id}')
    cur_location = cursor.fetchall()[0][0]
    cursor.execute(f'select LocationID from locations where LocationName = "Skellige"')
    Skellige_id = cursor.fetchall()[0][0]
    cursor.execute(f'select MoveDuration from locations_links where FirstLocationID = {cur_location} and '
                   f'SecondLocationID = {Skellige_id}')
    duration = cursor.fetchall()[0][0]
    await call.message.answer(text=utils.create_duration_text("Skellige", duration))
    await call.message.answer(text=str(duration))
    for i in range(duration - 1, -1, -1):
        time.sleep(1)
        await call.message.answer(text=str(i))
    cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
    max_hp, cur_hp = cursor.fetchall()[0]
    cursor.execute(f'update person set LocationID = {Skellige_id}, CurHP = {max(max_hp, cur_hp)} '
                   f'where UserID = {call.message.chat.id}')
    connect.commit()
    await call.message.answer(text=utils.Skellige_ARRIVAL_TEXT)

    cursor.execute(f'select MobID from mobs where ReqLevel <= '
                   f'(select Level from person where UserID = {call.message.chat.id})')
    all_req_mobs = cursor.fetchall()
    Skellige_mobs = []
    for mob in all_req_mobs:
        if mob[0] in utils.Skellige_mobs:
            Skellige_mobs.append(mob[0])
    mob_id = Skellige_mobs[random.randrange(0, len(Skellige_mobs))]
    cursor.execute(f'select HP from mobs where MobID = {mob_id}')
    mob_hp = cursor.fetchall()[0][0]
    cursor.execute(f'update person set MobId = {mob_id}, MobHP = {mob_hp} where UserID = {call.message.chat.id}')
    await call.message.answer(text=commands.create_bonuses_text(call.message, cursor))

    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(utils.GET_MOB_INFO_TEXT, callback_data=f"mob_info")
    markup.row(item)
    item = types.InlineKeyboardButton(utils.DRINK_POTION_TEXT, callback_data=f"drink_potion")
    markup.row(item)
    item = types.InlineKeyboardButton(utils.ATTACK_TEXT, callback_data=f"attack")
    markup.row(item)
    await call.message.answer(text=utils.TURN_TEXT, reply_markup=markup)


@dp.callback_query_handler(text_contains=["move_to_Crones"])
async def move_to_Crones(call: types.CallbackQuery):
    cursor.execute(f'select LocationID from person where UserID = {call.message.chat.id}')
    cur_location = cursor.fetchall()[0][0]
    cursor.execute(f'select LocationID from locations where LocationName = "Crones"')
    Crones_id = cursor.fetchall()[0][0]
    cursor.execute(f'select MoveDuration from locations_links where FirstLocationID = {cur_location} and '
                   f'SecondLocationID = {Crones_id}')
    duration = cursor.fetchall()[0][0]
    await call.message.answer(text=utils.create_duration_text("Crones", duration))
    await call.message.answer(text=str(duration))
    for i in range(duration - 1, -1, -1):
        time.sleep(1)
        await call.message.answer(text=str(i))
    cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
    max_hp, cur_hp = cursor.fetchall()[0]
    cursor.execute(f'update person set LocationID = {Crones_id}, CurHP = {max(max_hp, cur_hp)} '
                   f'where UserID = {call.message.chat.id}')
    connect.commit()
    await call.message.answer(text=utils.Crones_ARRIVAL_TEXT)

    cursor.execute(f'select MobID from mobs where ReqLevel <= '
                   f'(select Level from person where UserID = {call.message.chat.id})')
    all_req_mobs = cursor.fetchall()
    Crones_mobs = []
    for mob in all_req_mobs:
        if mob[0] in utils.Crones_mobs:
            Crones_mobs.append(mob[0])
    mob_id = Crones_mobs[random.randrange(0, len(Crones_mobs))]
    cursor.execute(f'select HP from mobs where MobID = {mob_id}')
    mob_hp = cursor.fetchall()[0][0]
    cursor.execute(f'update person set MobId = {mob_id}, MobHP = {mob_hp} where UserID = {call.message.chat.id}')
    await call.message.answer(text=commands.create_bonuses_text(call.message, cursor))

    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(utils.GET_MOB_INFO_TEXT, callback_data=f"mob_info")
    markup.row(item)
    item = types.InlineKeyboardButton(utils.DRINK_POTION_TEXT, callback_data=f"drink_potion")
    markup.row(item)
    item = types.InlineKeyboardButton(utils.ATTACK_TEXT, callback_data=f"attack")
    markup.row(item)
    await call.message.answer(text=utils.TURN_TEXT, reply_markup=markup)


async def attack_mod(call):
    action_result = commands.attack_mob(call.message, cursor)
    if action_result == utils.END_TEXT:
        await call.message.answer(text=utils.END_TEXT)
        cursor.execute(f'DELETE from person where UserId = {call.message.chat.id}')
        cursor.execute(f'DELETE from items_links where UserId = {call.message.chat.id}')
        cursor.execute('INSERT INTO person (UserId, Nickname) VALUES (?, ?)',
                       [call.message.chat.id, call.message.from_user.username])
        connect.commit()
        give_open_bonus(call.message)
        await call.message.answer(text=utils.HELLO_TEXT)
    else:
        await call.message.answer(text=utils.NEW_HP_TEXT + " " + str(action_result))
        markup = types.InlineKeyboardMarkup(row_width=4)
        item = types.InlineKeyboardButton(utils.GET_MOB_INFO_TEXT, callback_data=f"mob_info")
        markup.row(item)
        item = types.InlineKeyboardButton(utils.DRINK_POTION_TEXT, callback_data=f"drink_potion")
        markup.row(item)
        item = types.InlineKeyboardButton(utils.ATTACK_TEXT, callback_data=f"attack")
        markup.row(item)
        await call.message.answer(text=utils.TURN_TEXT, reply_markup=markup)


@dp.callback_query_handler(text_contains=["mob_info"])
async def mob_info(call: types.CallbackQuery):
    await call.message.answer(text=commands.create_mob_info_text(call.message, cursor))
    await attack_mod(call)


@dp.callback_query_handler(text_contains=["drink_potion"])
async def drink_potion(call: types.CallbackQuery):
    potions_text = commands.create_potions_text(cursor, call.message)
    if potions_text == utils.NO_POTION_TEXT or potions_text == utils.EMPTY_INVENTORY_TEXT:
        await call.message.answer(text=utils.MISS_TURN_TEXT)
    else:
        await call.message.answer(text=potions_text)
        cursor.execute(f"select ItemID from items_links where IsActive = 1 and UserID = {call.message.chat.id}")
        active_items = cursor.fetchall()
        markup = types.InlineKeyboardMarkup(row_width=4)
        for item in active_items:
            cursor.execute(f"select ItemType from items where ItemID = {item[0]}")
            ItemType = cursor.fetchall()[0][0]
            if ItemType != 'potion':
                continue
            item = types.InlineKeyboardButton(f"{item[0]}", callback_data=f"potion_{item[0]}")
            markup.row(item)
        await call.message.answer(text=utils.WHAT_POTION_TO_USE_TEXT, reply_markup=markup)


@dp.callback_query_handler(text_contains=["potion"])
async def potion(call: types.CallbackQuery):
    item_id = call.data.replace('potion_', '')
    await call.message.answer(text=commands.drink_potion(item_id, cursor, connect, call.message))
    await attack_mod(call)


@dp.callback_query_handler(text_contains=["attack"])
async def attack(call: types.CallbackQuery):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item = types.InlineKeyboardButton(f"physical", callback_data=f"physical")
    markup.row(item)
    item = types.InlineKeyboardButton(f"magical", callback_data=f"magical")
    markup.row(item)
    await call.message.answer(text=utils.CHOOSE_ATTACK_TYPE_TEXT, reply_markup=markup)


@dp.callback_query_handler(text_contains=["physical"])
async def physical(call: types.CallbackQuery):
    action_result = commands.attack_user(call.message, cursor, connect, "physical")
    if not action_result[0]:
        await call.message.answer(text=utils.MOB_REMAIN_HP_TEXT + " " + str(action_result[1]))
        await attack_mod(call)
    else:
        await call.message.answer(text=utils.WIN_TEXT)
        if action_result[1] > 0:
            await call.message.answer(text=utils.UPDATE_LEVEL_TEXT + " " + str(action_result[1]))
        await call.message.answer(text=utils.WIN_ITEM_ID_TEXT + " " + str(action_result[2]))
        await call.message.answer(text=utils.WIN_MONEY_TEXT + " " + str(action_result[3]))
        cursor.execute(f"update person set LocationID = 1 where UserID = {call.message.chat.id}")
        connect.commit()
        await call.message.answer(text=utils.Kaer_Morhen_ARRIVAL_TEXT)


@dp.callback_query_handler(text_contains=["magical"])
async def magical(call: types.CallbackQuery):
    action_result = commands.attack_user(call.message, cursor, connect, "magical")
    if not action_result[0]:
        await call.message.answer(text=utils.MOB_REMAIN_HP_TEXT + " " + str(action_result[1]))
        await attack_mod(call)
    else:
        await call.message.answer(text=utils.WIN_TEXT)
        if action_result[1] > 0:
            await call.message.answer(text=utils.UPDATE_LEVEL_TEXT + " " + str(action_result[1]))
        await call.message.answer(text=utils.WIN_ITEM_ID_TEXT + " " + str(action_result[2]))
        await call.message.answer(text=utils.WIN_MONEY_TEXT + " " + str(action_result[3]))
        cursor.execute(f'select HP, CurHP from person where UserID = {call.message.chat.id}')
        max_hp, cur_hp = cursor.fetchall()[0]
        cursor.execute(f'update person set LocationID = 1, CurHP = {max(max_hp, cur_hp)} '
                       f'where UserID = {call.message.chat.id}')
        connect.commit()
        await call.message.answer(text=utils.Kaer_Morhen_ARRIVAL_TEXT)


@dp.message_handler()
async def unknown_message(message: types.Message):
    await message.answer(text=utils.UNKNOWN_TEST)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())