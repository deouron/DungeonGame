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

connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
cursor = connect.cursor()

cursor.execute('INSERT INTO locations (LocationName) VALUES (?)', ['center'])
connect.commit()
cursor.execute('INSERT INTO locations (LocationName, XCoord, YCoord) VALUES (?, ?, ?)', ['Novigrad', 0, 2])
connect.commit()

cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, HP, Mana, Attack, MagicAttack, Armour, '
               'MagicArmour, ReqLevel) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
               [10, 5, 'potion', 2, 0, 0, 0, 0, 0, 1])
connect.commit()  # зелье-здоровье
cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, HP, Mana, Attack, MagicAttack, Armour, '
               'MagicArmour, ReqLevel) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
               [10, 5, 'potion', 0, 2, 0, 0, 0, 0, 1])
connect.commit()  # зелье-мана
cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, HP, Mana, Attack, MagicAttack, Armour, '
               'MagicArmour, ReqLevel) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
               [20, 10, 'armour ', 0, 0, 0, 0, 3, 0, 1])
connect.commit()  # броня

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
    await message.answer(text=utils.create_stats_player_text(person_info, location_info))


@dp.message_handler(commands=["stats_locations"])
async def stats_locations(message: types.Message):
    cursor.execute(f'select LocationName, LocationType, XCoord, YCoord from locations '
                   f'where LocationType = city')
    locations = list(cursor.fetchall())
    await message.answer(text=utils.create_stats_location_text(locations))


@dp.message_handler(commands=["inventory"])
async def inventory(message: types.Message):
    cursor.execute(f'select ItemID, quantity, IsActive from items_links '
                   f'where UserID = {message.chat.id}')
    user_items = list(cursor.fetchall())
    if len(user_items) == 0:
        await message.answer(text="В инвентаре пусто")
    else:
        text = "Твой инвентарь:\n\n"
        for item in user_items:
            item = list(item)
            cursor.execute(
                f'select Cost, CostToSale, ItemType, HP, Mana, Attack, MagicAttack, Armour, MagicArmour, '
                f'ReqLevel from items where ItemID = {item[0]}')
            cur_item = list(cursor.fetchall()[0])
            cur_text = f"Тип: {cur_item[2]}\n" \
                       f"Количество: {item[1]}\n" \
                       f"Цена для покупки: {cur_item[0]} (для продажи {cur_item[1]})\n" \
                       f"Бонусы: здоровье +{cur_item[3]}, мана +{cur_item[4]}, атака +{cur_item[5]}, " \
                       f"магическая атака +{cur_item[6]}, броня +{cur_item[7]}, магическая броня +{cur_item[8]}\n" \
                       f"Нужный уровень для ношения предмета: {cur_item[9]}\n"
            if item[2] == 1:
                cur_text += "Статус: используется\n\n"
            else:
                cur_text += "Статус: не используется\n\n"
            text += cur_text
        await message.answer(text=text)


@dp.message_handler()
async def unknown_message(message: types.Message):
    """Ответ на любое неожидаемое сообщение"""
    await message.answer(text=utils.UNKNOWN_TEST)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
