def create_stats_text(person_info, location_info):
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


UNKNOWN_TEST = 'Я не знаю такую команду'
HELPER_TEXT = '/help - помощь\n'
HELLO_TEXT = 'Привет!\n' \
             'Подробности: /help\n'