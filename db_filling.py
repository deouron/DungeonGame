import sqlite3


def fill_items():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, HP, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?)',
                   [1, 5, 'potion', 2, 1])
    connect.commit()  # зелье-здоровье id=1
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, Mana, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?)',
                   [1, 5, 'potion', 2, 1])
    connect.commit()  # зелье-мана id=2
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, Armour, MagicArmour, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?, ?)',
                   [20, 10, 'armour',  3, 2, 1])
    connect.commit()  # броня1 id=3
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, Armour, MagicArmour, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?, ?)',
                   [25, 15, 'armour', 5, 3, 2])
    connect.commit()  # броня2 id=4
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, Armour,MagicArmour, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?, ?)',
                   [10, 7, 'helmet', 2, 1, 1])
    connect.commit()  # шлем id=5
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, Armour,MagicArmour, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?, ?)',
                   [5, 3, 'boots', 2, 1, 1])
    connect.commit()  # сапоги id=6
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, Armour,MagicArmour, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?, ?)',
                   [5, 3, 'bracers', 2, 1, 1])
    connect.commit()  # наручи id=7
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, MagicAttack, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?)',
                   [3, 2, 'weapon', 10, 1])
    connect.commit()  # оружие1 id=8
    cursor.execute('INSERT INTO items (Cost, CostToSale, ItemType, Attack, ReqLevel) '
                   'VALUES (?, ?, ?, ?, ?)',
                   [3, 2, 'weapon', 10, 1])
    connect.commit()  # оружие2 id=9


def fill_items_sellers():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    # зелья
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [1, 1])
    connect.commit()
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [1, 2])
    connect.commit()
    # броня
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [3, 3])
    connect.commit()
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [3, 4])
    connect.commit()
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [3, 5])
    connect.commit()
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [3, 6])
    connect.commit()
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [3, 7])
    connect.commit()
    # оружие
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [2, 8])
    connect.commit()
    cursor.execute('INSERT INTO items_sellers (LocationID, ItemID) VALUES (?, ?)', [2, 9])
    connect.commit()


def fill_locations():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute('INSERT INTO locations (LocationName) VALUES (?)', ['Kaer_Morhen'])
    connect.commit()  # id=1
    cursor.execute('INSERT INTO locations (LocationName, XCoord, YCoord) VALUES (?, ?, ?)', ['Novigrad', 0, 10])
    connect.commit()  # id=2
    cursor.execute('INSERT INTO locations (LocationName, XCoord, YCoord) VALUES (?, ?, ?)', ['White_Orchard', -5, -5])
    connect.commit()  # id=3
    cursor.execute('INSERT INTO locations (LocationName, LocationType, XCoord, YCoord) VALUES (?, ?, ?, ?)',
                   ['Crones', 'dungeon', 8, 1])
    connect.commit()  # id=4
    cursor.execute('INSERT INTO locations (LocationName, LocationType, XCoord, YCoord) VALUES (?, ?, ?, ?)',
                   ['Skellige', 'dungeon', 4, 0])
    connect.commit()  # id=5


def fill_location_reachability():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute(f'select LocationID, XCoord, YCoord from locations')
    locations = list(cursor.fetchall())
    for i in range(len(locations)):
        for j in range(i, len(locations)):
            if i == j:
                cursor.execute(
                    'INSERT INTO locations_links (FirstLocationID, SecondLocationID, MoveDuration) VALUES (?, ?, ?)',
                    [locations[i][0], locations[j][0], 0])
                connect.commit()
                continue
            distance = ((locations[i][1] - locations[j][1])**2 + (locations[i][2] - locations[j][2])**2)**0.5
            if distance <= 10.01:
                cursor.execute('INSERT INTO locations_links (FirstLocationID, SecondLocationID, MoveDuration) VALUES (?, ?, ?)',
                               [locations[i][0], locations[j][0], round(distance)])
                connect.commit()
                cursor.execute('INSERT INTO locations_links (FirstLocationID, SecondLocationID, MoveDuration) VALUES (?, ?, ?)',
                               [locations[j][0], locations[i][0], round(distance)])
                connect.commit()


def give_open_bonus(message):
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute('INSERT INTO items_links (UserID, ItemID, quantity, IsActive)'
                   'values (?, ?, ?, ?)',
                   [message.chat.id, 1, 2, 1])
    connect.commit()  # бонусное зелье-здоровье
    cursor.execute('INSERT INTO items_links (UserID, ItemID, quantity, IsActive)'
                   'values (?, ?, ?, ?)',
                   [message.chat.id, 2, 1, 1])
    connect.commit()  # бонусное зелье-мана
    cursor.execute('INSERT INTO items_links (UserID, ItemID, quantity, IsActive)'
                   'values (?, ?, ?, ?)',
                   [message.chat.id, 3, 1, 1])
    connect.commit()  # бонусная броня