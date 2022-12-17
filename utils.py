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


UNKNOWN_TEST = 'Я не знаю такую команду'
HELPER_TEXT = '/help - помощь\n' \
              '/stats_player - прислать статистику игрока\n' \
              '/stats_cities - прислать описание городов\n'
HELLO_TEXT = 'Привет!\n' \
             'Подробности: /help\n'