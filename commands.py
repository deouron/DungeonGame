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
                 f"Текущая локация: {location_info[0]}, тип: {location_info[1]}"
    return STATS_TEXT


def create_stats_location_text(locations):
    STATS_TEXT = ""
    for location in locations:
        cur_location_text = f"Название: {location[0]}\n" \
                            f"Тип: {location[1]}\n" \
                            f"Координата: ({location[2]}, {location[3]}) \n\n"
        STATS_TEXT += cur_location_text
    return STATS_TEXT


def create_inventory_text(cursor, message):
    cursor.execute(f'select ItemID, quantity, IsActive from items_links '
                   f'where UserID = {message.chat.id}')
    user_items = list(cursor.fetchall())
    if len(user_items) == 0:
        text = "В инвентаре пусто"
        return text
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
    return text