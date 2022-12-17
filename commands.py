import utils


def create_stats_player_text(person_info, location_info):
    STATS_TEXT = f"Никнейм персонажа: {person_info[0]}\n" \
                 f"Уровень: {person_info[1]}\n" \
                 f"Максимальное здоровье: {person_info[2]}\n" \
                 f"Текущее здоровье: {person_info[3]}\n" \
                 f"Число денег: {person_info[4]}\n" \
                 f"Базовая атака персонажа: {person_info[5]}\n" \
                 f"Базовая магическая атака персонажа: {person_info[6]}\n" \
                 f"Опыт: {person_info[7]}/100\n" \
                 f"Базовая броня персонажа: {person_info[8]}\n" \
                 f"Базовая магическая броня персонажа: {person_info[9]}\n" \
                 f"Текущая локация: {location_info[0]} (тип {location_info[1]})"
    return STATS_TEXT


def create_stats_location_text(cursor):
    cursor.execute(f'select LocationName, LocationType, XCoord, YCoord, Info from locations')
    locations = list(cursor.fetchall())
    STATS_TEXT = ""
    for location in locations:
        cur_location_text = f"Название: {location[0]}\n" \
                            f"Тип: {location[1]}\n" \
                            f"Описание: {location[4]}\n" \
                            f"Координата: ({location[2]}, {location[3]}) \n\n"
        STATS_TEXT += cur_location_text
    return STATS_TEXT


def create_inventory_text(cursor, message):
    cursor.execute(f'select ItemID, quantity, IsActive from items_links where UserID = {message.chat.id}')
    user_items = list(cursor.fetchall())
    if len(user_items) == 0:
        return utils.EMPTY_INVENTORY_TEXT
    text = "Твой инвентарь:\n\n"
    for item in user_items:
        item = list(item)
        cursor.execute(
            f'select Cost, CostToSale, ItemType, HP, Mana, Attack, MagicAttack, Armour, MagicArmour, '
            f'ReqLevel from items where ItemID = {item[0]}')
        cur_item = list(cursor.fetchall()[0])
        cur_text = f"Тип: {cur_item[2]}\n" \
                   f"Количество: {item[1]}\n" \
                   f"Цена покупки: {cur_item[0]} (продажи {cur_item[1]})\n" \
                   f"Бонусы: здоровье +{cur_item[3]}, мана +{cur_item[4]}, атака +{cur_item[5]}, " \
                   f"магическая атака +{cur_item[6]}, броня +{cur_item[7]}, магическая броня +{cur_item[8]}\n" \
                   f"Нужный уровень для ношения предмета: {cur_item[9]}\n"
        if item[2] == 1:
            cur_text += "Статус: используется\n\n"
        else:
            cur_text += f"Статус: {utils.ITEM_IS_IN_USE_TEXT}\n\n"
        text += cur_text
    return text


def create_garments_text(cursor, message):
    cursor.execute(f'select ItemID, quantity, IsActive from items_links where UserID = {message.chat.id}')
    user_items = list(cursor.fetchall())
    if len(user_items) == 0:
        return utils.EMPTY_INVENTORY_TEXT
    can_put_on = False
    text = "Твой инвентарь:\n\n"
    for item in user_items:
        item = list(item)
        cursor.execute(
            f'select Cost, CostToSale, ItemType, HP, Mana, Attack, MagicAttack, Armour, MagicArmour, '
            f'ReqLevel from items where ItemID = {item[0]}')
        cur_item = list(cursor.fetchall()[0])
        if cur_item[2] == 'potion':
            continue
        can_put_on = True
        cur_text = f"Id: {item[0]}\n" \
                   f"Тип: {cur_item[2]}\n" \
                   f"Количество: {item[1]}\n" \
                   f"Цена покупки: {cur_item[0]} (продажи {cur_item[1]})\n" \
                   f"Бонусы: здоровье +{cur_item[3]}, мана +{cur_item[4]}, атака +{cur_item[5]}, " \
                   f"магическая атака +{cur_item[6]}, броня +{cur_item[7]}, магическая броня +{cur_item[8]}\n" \
                   f"Нужный уровень для ношения предмета: {cur_item[9]}\n"
        if item[2] == 1:
            cur_text += "Статус: используется\n\n"
        else:
            cur_text += f"Статус: {utils.ITEM_IS_IN_USE_TEXT}\n\n"
        text += cur_text
    if can_put_on:
        return text
    return utils.NO_GARMENTS_TEXT


def create_items_text(cursor, message):
    cursor.execute(f'select LocationID, Money from person where UserID = {message.chat.id}')
    location_id, money = cursor.fetchall()[0]
    cursor.execute(f'select LocationName from locations where LocationID = {location_id}')
    location_name = cursor.fetchall()[0][0]
    text = f"Ты находишься в {location_name}, твой баланс: {money}\n" \
           f"Тут можно купить/продать:\n\n"
    cursor.execute(f'select ItemID from items_sellers where LocationID = {location_id}')
    items = list(cursor.fetchall())
    cnt = 1
    for item in items:
        cursor.execute(f'select quantity from items_links where ItemID = {item[0]} and UserID = {message.chat.id}')
        quantity = cursor.fetchall()
        if len(quantity) == 0:
            quantity = 0
        else:
            quantity = quantity[0][0]
        cursor.execute(f'select ItemType, Cost, CostToSale, HP, Mana,  Attack, MagicAttack, Armour, MagicArmour, '
                       f'ReqLevel from items where ItemID = {item[0]}')
        cur_item = list(cursor.fetchall()[0])
        cur_text = f"№{str(cnt)}\n" \
                   f"Тип: {cur_item[0]}\n" \
                   f"Цена покупки: {cur_item[1]} (продажи {cur_item[2]})\n" \
                   f"Бонусы: здоровье +{cur_item[3]}, мана +{cur_item[4]}, атака +{cur_item[5]}, " \
                   f"магическая атака +{cur_item[6]}, броня +{cur_item[7]}, магическая броня +{cur_item[8]}\n" \
                   f"Нужный уровень для ношения предмета: {cur_item[9]}\n" \
                   f"В инвентаре: {quantity}\n\n"
        text += cur_text
        cnt += 1
    return text


def buy_item(item_id, cursor, connect, message):
    cursor.execute(f'select Money, Level from person where UserID = {message.chat.id}')
    money, Level = cursor.fetchall()[0]
    cursor.execute(f'select Cost, ReqLevel, ItemType from items where ItemID = {item_id}')
    item_cost, ReqLevel, ItemType = cursor.fetchall()[0]
    if ReqLevel > Level:
        return utils.NOT_ENOUGH_LEVEL_TEXT
    if item_cost > money:
        return utils.NOT_ENOUGH_MONEY_TEXT
    cursor.execute(f'update person set Money = {money - item_cost} '
                   f'where UserID = {message.chat.id}')
    connect.commit()
    cursor.execute(f'select quantity from items_links where UserID = {message.chat.id} and ItemID = {item_id}')
    quantity = cursor.fetchall()
    if len(quantity) != 0:
        cursor.execute(f'update items_links set quantity = {quantity[0][0] + 1} '
                       f'where UserID = {message.chat.id} and ItemID = {item_id}')
        connect.commit()
    else:
        if ItemType == 'potion':
            cursor.execute('INSERT INTO items_links (UserID, ItemID, quantity, IsActive)'
                           'values (?, ?, ?, ?)',
                           [message.chat.id, item_id, 1, 1])  # зелья сразу используем, остальное надо надеть
        else:
            cursor.execute('INSERT INTO items_links (UserID, ItemID, quantity, IsActive)'
                           'values (?, ?, ?, ?)',
                           [message.chat.id, item_id, 1, 0])
        connect.commit()
    return utils.SUCCESSFUL_PURCHASE_TEXT


def sell_item(item_id, cursor, connect, message):
    cursor.execute(f'select quantity from items_links where UserID = {message.chat.id} and ItemID = {item_id}')
    quantity = cursor.fetchall()
    if len(quantity) != 0 and quantity[0][0] > 0:
        cursor.execute(f'select IsActive from items_links where UserID = {message.chat.id} and ItemID = {item_id}')
        IsActive = cursor.fetchall()[0][0]
        if IsActive == 1:
            return utils.TAKE_OFF_ITEM_TEXT
        cursor.execute(f'select Money from person where UserID = {message.chat.id}')
        money = cursor.fetchall()[0][0]
        cursor.execute(f'select CostToSale from items where ItemID = {item_id}')
        item_cost = cursor.fetchall()[0][0]
        remain = quantity[0][0] - 1
        if remain > 0:
            cursor.execute(f'update items_links set quantity = {remain} '
                           f'where UserID = {message.chat.id} and ItemID = {item_id}')
            connect.commit()
        else:
            cursor.execute(f'DELETE from items_links where UserId = {message.chat.id} and ItemID = {item_id}')
        cursor.execute(f'update person set Money = {money + item_cost} '
                       f'where UserID = {message.chat.id}')
        connect.commit()
    else:
        return utils.NO_ITEMS_FOR_SALE_TEXT
    return utils.SUCCESSFUL_SALE_TEXT


def use_item(item_id, cursor, connect, message):
    cursor.execute(f'select ItemType from items where ItemID = {item_id}')
    ItemType = cursor.fetchall()[0][0]
    cursor.execute(f'select ItemID from items_links where UserID = {message.chat.id} and IsActive = 1')
    active = cursor.fetchall()
    is_exist = False
    for item in active:
        cursor.execute(f'select ItemType from items where ItemID = {item[0]}')
        if cursor.fetchall()[0][0] == ItemType:
            active = item[0]
            is_exist = True
            break
    cursor.execute(f'update items_links set IsActive = 1 where UserID = {message.chat.id} and '
                   f'ItemID = {item_id}')
    connect.commit()
    if not is_exist:
        return utils.ITEM_IS_IN_USE_TEXT
    cursor.execute(f'update items_links set IsActive = 0 where UserID = {message.chat.id} and '
                   f'ItemID = {active}')
    connect.commit()
    return utils.ITEM_IS_IN_USE_TEXT
