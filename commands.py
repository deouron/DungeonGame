import utils
import random


def create_stats_player_text(person_info, location_info):
    STATS_TEXT = f"Никнейм персонажа: {person_info[0]}\n" \
                 f"Уровень: {person_info[1]}\n" \
                 f"Максимальное здоровье: {person_info[2]}\n" \
                 f"Текущее здоровье: {person_info[3]}\n" \
                 f"Число монет: {person_info[4]}\n" \
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
                   f"Бонусы: \n" \
                   f"    здоровье +{cur_item[3]}, мана +{cur_item[4]},\n" \
                   f"    атака +{cur_item[5]}, магическая атака +{cur_item[6]},\n" \
                   f"    броня +{cur_item[7]}, магическая броня +{cur_item[8]}\n" \
                   f"Нужный уровень для ношения предмета: {cur_item[9]}\n"
        if item[2] == 1:
            cur_text += f"Статус: {utils.ITEM_IS_IN_USE_TEXT}\n\n"
        else:
            cur_text += f"Статус: {utils.ITEM_IS_NOT_IN_USE_TEXT}\n\n"
        text += cur_text
    return text


def create_garments_text(cursor, message):
    cursor.execute(f'select ItemID, quantity, IsActive from items_links where UserID = {message.chat.id}')
    user_items = list(cursor.fetchall())
    if len(user_items) == 0:
        return utils.EMPTY_INVENTORY_TEXT
    can_put_on = False
    text = "Твой инвентарь (одежда и оружия):\n\n"
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
                   f"Бонусы:\n" \
                   f"    здоровье +{cur_item[3]}, мана +{cur_item[4]},\n" \
                   f"    атака +{cur_item[5]}, магическая атака +{cur_item[6]},\n" \
                   f"    броня +{cur_item[7]}, магическая броня +{cur_item[8]}\n" \
                   f"Нужный уровень для ношения предмета: {cur_item[9]}\n"
        if item[2] == 1:
            cur_text += f"Статус: {utils.ITEM_IS_IN_USE_TEXT}\n\n"
        else:
            cur_text += f"Статус: {utils.ITEM_IS_NOT_IN_USE_TEXT}\n\n"
        text += cur_text
    if can_put_on:
        return text
    return utils.NO_GARMENTS_TEXT


def create_potions_text(cursor, message):
    cursor.execute(f'select ItemID, quantity, IsActive from items_links where UserID = {message.chat.id}')
    user_items = list(cursor.fetchall())
    if len(user_items) == 0:
        return utils.EMPTY_INVENTORY_TEXT
    can_put_on = False
    text = "Твой инвентарь (зелья):\n\n"
    for item in user_items:
        item = list(item)
        cursor.execute(
            f'select Cost, CostToSale, ItemType, HP, Mana, Attack, MagicAttack, Armour, MagicArmour, '
            f'ReqLevel from items where ItemID = {item[0]}')
        cur_item = list(cursor.fetchall()[0])
        if cur_item[2] != 'potion':
            continue
        can_put_on = True
        cur_text = f"Id: {item[0]}\n" \
                   f"Тип: {cur_item[2]}\n" \
                   f"Количество: {item[1]}\n" \
                   f"Бонусы: здоровье +{cur_item[3]}, мана +{cur_item[4]}\n\n"
        text += cur_text
    if can_put_on:
        return text
    return utils.NO_POTION_TEXT


def create_items_text(cursor, message):
    cursor.execute(f'select LocationID, Money from person where UserID = {message.chat.id}')
    location_id, money = cursor.fetchall()[0]
    cursor.execute(f'select LocationName from locations where LocationID = {location_id}')
    location_name = cursor.fetchall()[0][0]
    text = f"Ты находишься в {location_name}, твой баланс: {money}\n" \
           f"Здесь можно купить/продать:\n\n"
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
        cur_text = f"№{str(cnt)} (id {item[0]})\n" \
                   f"Тип: {cur_item[0]}\n" \
                   f"Цена покупки: {cur_item[1]} (продажи {cur_item[2]})\n" \
                   f"Бонусы:\n" \
                   f"    здоровье +{cur_item[3]}, мана +{cur_item[4]},\n" \
                   f"    атака +{cur_item[5]}, магическая атака +{cur_item[6]},\n" \
                   f"    броня +{cur_item[7]}, магическая броня +{cur_item[8]}\n" \
                   f"Нужный уровень для ношения предмета: {cur_item[9]}\n" \
                   f"В инвентаре: {quantity}\n\n"
        text += cur_text
        cnt += 1
    return text


def add_item(cursor, connect, message, item_id):
    cursor.execute(f'select Cost, ReqLevel, ItemType from items where ItemID = {item_id}')
    item_cost, ReqLevel, ItemType = cursor.fetchall()[0]
    cursor.execute(f'select quantity from items_links where UserID = {message.chat.id} and ItemID = {item_id}')
    quantity = cursor.fetchall()
    if len(quantity) != 0:
        cursor.execute(f'update items_links set quantity = {quantity[0][0] + 1} where UserID = {message.chat.id} and '
                       f'ItemID = {item_id}')
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


def buy_item(item_id, cursor, connect, message):
    cursor.execute(f'select Money, Level from person where UserID = {message.chat.id}')
    money, Level = cursor.fetchall()[0]
    cursor.execute(f'select Cost, ReqLevel, ItemType from items where ItemID = {item_id}')
    item_cost, ReqLevel, ItemType = cursor.fetchall()[0]
    if ReqLevel > Level:
        return utils.NOT_ENOUGH_LEVEL_TEXT
    if item_cost > money:
        return utils.NOT_ENOUGH_MONEY_TEXT
    cursor.execute(f'update person set Money = {money - item_cost} where UserID = {message.chat.id}')
    connect.commit()
    add_item(cursor, connect, message, item_id)
    return utils.SUCCESSFUL_PURCHASE_TEXT


def sell_item(item_id, cursor, connect, message):
    cursor.execute(f'select quantity from items_links where UserID = {message.chat.id} and ItemID = {item_id}')
    quantity = cursor.fetchall()
    if len(quantity) != 0 and quantity[0][0] > 0:
        cursor.execute(f'select IsActive from items_links where UserID = {message.chat.id} and ItemID = {item_id}')
        IsActive = cursor.fetchall()[0][0]
        if IsActive == 1 and quantity[0][0] == 1:
            return utils.TAKE_OFF_ITEM_TEXT
        cursor.execute(f'select Money from person where UserID = {message.chat.id}')
        money = cursor.fetchall()[0][0]
        cursor.execute(f'select CostToSale from items where ItemID = {item_id}')
        item_cost = cursor.fetchall()[0][0]
        remain = quantity[0][0] - 1
        if remain > 0:
            cursor.execute(f'update items_links set quantity = {remain} where UserID = {message.chat.id} and '
                           f'ItemID = {item_id}')
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
    cursor.execute(f'update items_links set IsActive = 1 where UserID = {message.chat.id} and ItemID = {item_id}')
    connect.commit()
    if not is_exist:
        return utils.ITEM_IS_IN_USE_TEXT
    cursor.execute(f'update items_links set IsActive = 0 where UserID = {message.chat.id} and ItemID = {active}')
    connect.commit()
    return utils.ITEM_IS_IN_USE_TEXT


def create_mob_info_text(message, cursor):
    cursor.execute(f'select MobId from person where UserID = {message.chat.id}')
    mob_id = cursor.fetchall()[0][0]
    cursor.execute(f'select HP, XP, ReqLevel, AttackType, Attack, Armour, MagicArmour from mobs where MobID = {mob_id}')
    HP, XP, ReqLevel, AttackType, Attack, Armour, MagicArmour = cursor.fetchall()[0]
    text = f"Информация о монстре:\n\n" \
           f"Здоровье: {HP}\n" \
           f"Тип атака: {AttackType}\n" \
           f"Сила атаки: {Attack}\n" \
           f"Броня: {Armour}\n" \
           f"Магическая броня: {MagicArmour}\n\n" \
           f"Опыт за победу: {XP}\n" \
           f"Необходимый уровень для появления у персонажа: {ReqLevel}\n"
    return text


def create_bonuses(message, cursor):
    cursor.execute(f'select ItemID from items_links where UserID = {message.chat.id} and IsActive = 1')
    active_items = cursor.fetchall()
    bonuses = [0, 0, 0, 0]
    for item_id in active_items:
        cursor.execute(f'select ItemType, Attack, MagicAttack, Armour, MagicArmour from items where '
                       f'ItemID = {item_id[0]}')
        ItemType, Attack, MagicAttack, Armour, MagicArmour = cursor.fetchall()[0]
        if ItemType == 'potion':
            continue
        bonuses[0] += Attack
        bonuses[1] += MagicAttack
        bonuses[2] += Armour
        bonuses[3] += MagicArmour
    return bonuses


def attack_mob(message, cursor):
    bonuses = create_bonuses(message, cursor)
    cursor.execute(f'select MobId, CurHP from person where UserID = {message.chat.id}')
    mob_id, CurHP = cursor.fetchall()[0]
    cursor.execute(f'select AttackType, Attack from mobs where MobID = {mob_id}')
    AttackType, Attack = cursor.fetchall()[0]
    if AttackType == "physical":
        Attack = max(0, Attack - bonuses[2])
    else:
        Attack = max(0, Attack - bonuses[3])
    new_hp = CurHP - Attack
    if new_hp <= 0:
        return utils.END_TEXT
    cursor.execute(f'update person set CurHP = {new_hp} where UserID = {message.chat.id}')
    return new_hp


def update_level(message, cursor, connect, cur_xp):
    while cur_xp >= 100:
        cur_xp -= 100
        cursor.execute(f'select Level, XP, Money, HP, Attack, MagicAttack, Armour, MagicArmour from person '
                       f'where UserID = {message.chat.id}')
        Level, XP, Money, HP, Attack, MagicAttack, Armour, MagicArmour = cursor.fetchall()[0]
        cursor.execute(f'update person set Level = {Level + 1}, HP = {HP + 3}, Attack = {Attack + 3}, '
                       f'MagicAttack = {MagicAttack + 3}, XP = {cur_xp}, Money = {Money + 10}, Armour = {Armour + 3},'
                       f' MagicArmour = {MagicArmour + 3} where UserID = {message.chat.id}')
        connect.commit()


def attack_user(message, cursor, connect, attack_type):
    win_money, win_item_id = 0, 0
    bonuses = create_bonuses(message, cursor)
    cursor.execute(f'select LocationID, MobId, MobHP, Attack, MagicAttack, Money, XP from person where '
                   f'UserID = {message.chat.id}')
    LocationID, mob_id, MobHP, Attack, MagicAttack, Money, XP = cursor.fetchall()[0]
    cursor.execute(f'select Armour, MagicArmour, XP from mobs where MobID = {mob_id}')
    Armour, MagicArmour, MobXP = cursor.fetchall()[0]
    if attack_type == "physical":
        MobHP -= Attack + bonuses[0] - Armour
    elif attack_type == "magic":
        MobHP -= MagicAttack + bonuses[1] - MagicArmour
    cursor.execute(f'update person set MobHP = {MobHP} where UserID = {message.chat.id}')
    connect.commit()
    if MobHP > 0:
        return [False, MobHP]
    XP += MobXP
    level_up = XP // 100
    if XP >= 100:
        update_level(message, cursor, connect, XP)
    if LocationID == 5:
        win_item_id = utils.Skellige_items[random.randrange(0, len(utils.Skellige_items))]
        win_money = random.randint(utils.Skellige_money[0], utils.Skellige_money[1])
    elif LocationID == 4:
        win_item_id = utils.Crones_items[random.randrange(0, len(utils.Crones_items))]
        win_money = random.randint(utils.Crones_money[0], utils.Crones_money[1])
    cursor.execute(f'select Money from person where UserID = {message.chat.id}')
    cursor.execute(f'update person set Money = {Money + win_money} where UserID = {message.chat.id}')
    connect.commit()
    cursor.execute(f'update person set Money = {Money + win_money} where UserID = {message.chat.id}')
    connect.commit()
    add_item(cursor, connect, message, win_item_id)
    return [True, level_up, win_item_id, win_money]


def create_bonuses_text(message, cursor):
    bonuses = create_bonuses(message, cursor)
    cursor.execute(f"select CurHP, Attack, MagicAttack, Armour, MagicArmour from person where UserID = {message.chat.id}")
    CurHP, Attack, MagicAttack, Armour, MagicArmour = cursor.fetchall()[0]
    text = f"Твои показатели:\n" \
           f"Текущее здоровье: {CurHP}\n" \
           f"Атака: {Attack} + {bonuses[0]} = {Attack + bonuses[0]}\n" \
           f"Магическая атака: {MagicAttack} + {bonuses[1]} = {MagicAttack + bonuses[1]}\n" \
           f"Броня: {Armour} + {bonuses[2]} = {Armour + bonuses[2]}\n" \
           f"Магическая броня: {MagicArmour} + {bonuses[3]} = {MagicArmour + bonuses[3]}\n"
    return text


def drink_potion(item_id, cursor, connect, message):
    cursor.execute(f"select HP, Mana from items where ItemID = {item_id}")
    HP, Mana = cursor.fetchall()[0]
    cursor.execute(f"select CurHP from person where UserID = {message.chat.id}")
    CurHP = cursor.fetchall()[0][0]
    cursor.execute(f"select quantity from items_links where UserID = {message.chat.id} and ItemID = {item_id}")
    quantity = cursor.fetchall()[0][0]
    cursor.execute(f"update person set CurHP = {CurHP + HP} where UserID = {message.chat.id}")
    connect.commit()
    if quantity == 1:
        cursor.execute(f"DELETE from items_links where UserID = {message.chat.id} and ItemID = {item_id}")
        connect.commit()
    else:
        cursor.execute(f"update items_links set quantity = {quantity - 1} where UserID = {message.chat.id} "
                       f"and ItemID = {item_id}")
    return utils.SUCCESSFUL_POTION_USE_TEXT
