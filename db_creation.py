import sqlite3


def create_person_db():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute("drop table if exists person")
    connect.commit()
    cursor.execute("""create table person(
            UserID int DEFAULT 0,
            Nickname text DEFAULT "Character",
            LEVEL int DEFAULT 1,
            HP int DEFAULT 10,
            CurHP int DEFAULT 10,
            Money int DEFAULT 10,
            Attack int DEFAULT 5,
            MagicAttack int DEFAULT 3,
            XP int DEFAULT 0,
            Armour int DEFAULT 0,
            MagicArmour int DEFAULT 0,
            LocationID text DEFAULT 1
            );""")
    connect.commit()


def create_mobs_db():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute("drop table if exists mobs")
    connect.commit()
    cursor.execute("""create table mobs(
            MobID integer primary key autoincrement,
            HP int DEFAULT 10,
            XP int DEFAULT 0,
            ReqLevel int DEFAULT 1,
            AttackType text DEFAULT physical, 
            Attack int DEFAULT 0,
            Armour int DEFAULT 0,
            MagicArmour int DEFAULT 0
            );""")
    connect.commit()


def create_locations_db():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute("drop table if exists locations")
    connect.commit()
    cursor.execute("""create table locations(
            LocationID integer primary key autoincrement,
            XCoord int DEFAULT 0,
            YCoord int DEFAULT 0,
            LocationType text DEFAULT city,
            LocationName text DEFAULT center
            );""")
    connect.commit()


def create_locations_links_db():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute("drop table if exists locations_links")
    connect.commit()
    cursor.execute("""create table locations_links(
            LocationsLinkID integer primary key autoincrement,
            FirstLocationID int DEFAULT 0,
            SecondLocationID int DEFAULT 0
            );""")
    connect.commit()


def create_items_db():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute("drop table if exists items")
    connect.commit()
    cursor.execute("""create table items(
            ItemID integer primary key autoincrement,
            Cost int DEFAULT 0,
            CostToSale int DEFAULT 0,
            ItemType text DEFAULT weapon,
            HP int DEFAULT 0,
            Mana int DEFAULT 0,
            Attack int DEFAULT 0,
            MagicAttack int DEFAULT 0,
            Armour int DEFAULT 0,
            MagicArmour int DEFAULT 0,
            ReqLevel int DEFAULT 0
            );""")
    connect.commit()


def create_items_links_db():
    connect = sqlite3.connect('dbs/data.db', check_same_thread=False)
    cursor = connect.cursor()
    cursor.execute("drop table if exists items_links")
    connect.commit()
    cursor.execute("""create table items_links(
            ID integer primary key autoincrement,
            UserID int DEFAULT 0,
            ItemID int DEFAULT 0,
            quantity int DEFAULT 0,
            IsActive int DEFAULT 0
            );""")
    connect.commit()