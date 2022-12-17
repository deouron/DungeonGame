import sqlite3


def fill_items():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
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


def fill_locations():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute('INSERT INTO locations (LocationName) VALUES (?)', ['center'])
    connect.commit()
    cursor.execute('INSERT INTO locations (LocationName, XCoord, YCoord) VALUES (?, ?, ?)', ['Novigrad', 0, 2])
    connect.commit()