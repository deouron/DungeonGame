# TheWitcherGame (@dungeon_game_bot)

## **[Видео](https://disk.yandex.ru/i/EJ8e6d_EAqgawQ)** с примером работы 

### Описание

   Во время боя за 1 ход можно либо получить информацию о монстре, либо выпить зелье, либо атаковать выбранным типом урона. Далее монстр атакует тебя. Если придёшь в город, то твоё здоровье восстановится (при этом зельями можно сделать текущее здоровье больше максимального, тогда здоровье не изменится), 
если придёшь в подземелье, то начнётся битва с монстром. Купить/продать/надеть доспехи и оружие можно только в городе.

Для повышения уровня нужно 100 XP. При повышении уровня максимальное здоровье повышается на 5, атака и броня повышаются на 3 (как физическая, так и магическая). Так же при повышении уровня даётся 10 монет. При победе над монстром рандомно выдаются монеты, опыт и один предмет (зависит от локации). После сражения ты отправишься в начальную локацию - Kaer_Morhen (в случае поражения игра начнется заново).

<b>Novigrad</b> - город-государство и самое большое человеческое поселение в Северных королевствах, расположенное в дельте реки Понтар на территории королевства Редания. Имеет статус «Вольного города» и не подчиняется реданским законам. Здесь можно купить оружие.

<b>White_Orchard</b> - состоятельная деревня славится фруктовыми деревьями, кроны которых по весне покрываются белыми цветами. Население состоит из кметов, в деревне также живёт кузнец-бронник и купец. Здесь можно купить броню, шлем, сапоги и наручи.

<b>Kaer_Morhen</b> - горная крепость, в которой на протяжении нескольких веков располагалась одна из шести известных ведьмачьих школ — Школа Волка. Здесь можно купить зелья.

<b>Skellige</b> - государство, расположенное на одноимённом архипелаге. Эти места окутывают древние легенды. Обитатели известны как грозные пираты и располагают сильным флотом — возможно, наилучшим среди всех Северных королевств. Придя сюда, будь готов к тяжёлым битвам, но и к большим наградам.

<b>Crones</b> - трио ведьм, управляющих Веленом, дочери Хозяйки Леса, унаследовавшие часть ее силы. Пряха, Шептуха и Кухарка безраздельно властвуют на Кривоуховых топях и контролируют весь Велен, повелевая здешними людьми, которые почитают их как божество. К счастью, Геральд убил их, поэтому иди сюда, если хочешь убить слабых гулей и получить лёгкую небольшую награду.

### Команды

`/help` - помощь

`/stats_player` - прислать статистику игрока

`/locations` - прислать описание локаций

`/inventory` - показать инвентарь

`/go` - отправиться в другую локацию

`/items` - купить/продать предмет

`/put_on` - надеть вещь

`/take_off` - снять вещь

`/garments` - показать одежду и оружие из инвентаря

`/potions` - показать зелья из инвентаря

`/start` - начать игру

---

## Задание

Будем делать небольшую асинхронную текстовую игру в Телеге!

Наша БД будет выглядеть следующим образом (которую необходимо создать):

**Person - персонаж (пользователь):**

* UserID - ID пользователя

* Nickname - никнейм персонажа

* Level - уровень

* HP - здоровье

* CurHP - текущее здоровье

* Money - число денег

* Attack - базовая атака персонажа

* Magic Attack - базовая магическая атака персонажа

* XP - опыт

* Armour - базовая броня персонажа

* Magic Armour - базовая магическая броня персонажа

* LocationID - в какой локации сейчас находится персонаж

**Mobs - монстры:**

* MobID - ID монстра

* HP - здоровье

* XP - опыт

* ReqLevel - необходимый уровень для появления у персонажа 

* AttackType - тип атаки (физический/магический)

* Attack - размер атаки

* Armour - броня монстра

* Magic Armour - магическая броня монстра

**Locations - места**

* LocationID - ID места

* XCoord - X координата

* YCoord - Y координата

* LocationType - тип локации (бывает город, бывает подземелье)

**Items - предметы**

* ItemID - ID товара

* Cost - цена товара

* CostToSale - цена продажи товара

* ItemType - тип товара (оружие, броня, шлем, сапоги, наручи, зелье)

* HP - Дополнительное HP (которое дает зелье-предмет)

* Mana - Дополнительная мана (которая дает зелье-предмет)

* Attack - дополнительная атака

* Magic Attack - дополнительная магическая атака

* Armour - дополнительная броня

* Magic Armour - дополнительная магическая броня

* ReqLevel - нужный уровень для ношения предмета




<h4> Так же: </h4>

0. Дефолтные значения HP, Mana etc можно задавать самостоятельно (как и все остальные константы для предметов). Уровень повышается при получении 100 XP.

1. Для каждого персонажа должны быть его предметы (отдельная таблица: связка UserID - ItemID - quantity - индиктор ношения). Пользователь может носить только 1 тип оружия-брони-шлема-сапогов-наручей, зелий сколько угодно (при этом любая вещь может быть в неограниченном кол-ве, хоть и носит только одну)

2. Пользователь может переходить по локациям, которые находятся на расстоянии по координатам не более 10 (лучше всего завести таблицу между локациями, откуда можно и куда, чтобы не считать это каждый раз). Время перемещения = расстояние в секундах (например, если от точки A до точки B расстояние по координатам по прямой = 10, то персонаж идет 10 секунд), во время перемещения персонаж ничего не может сделать

3. Внутри города пользователь восстанавливает полностью ману и здоровье, а также в городе можно прикупить вещей (стоит создать таблицу с товарами и городом, где их можно купить)

4. Внутри подземелий нападает монстр, рандомно генерурющийся по уровню персонажа (не может быть выше, чем уровень игрока). Бой происходит поэтапно:

    * Вначале действие игрока (получить информацию о монстре, выпить зелье, атаковать выбранным типом урона)

    * После действие монстра (атака минус броня персонажа по типу атаки)

    * И так далее до победы/поражения (HP <= 0)

    Ожидание ответа игрока длится 1 минуту. После этого он погибает и возрождается с нуля в самой первой локации
    
<h3> Итого: </h3>

* Персонаж появляется в первой локации (городе) с начальным числом денег. В городе он может что-то прикупить себе или продать, а также покопаться в инвентаре и примерить одежду и получить информацию по себе

* Далее он может отправиться в любое место, доступное в радиусе

* Внутри подземелья пользователь убивает монстра, получает XP, и затем может также покопаться в инвентаре, получить по себе статистику и пойти далее в любую доступную в радиусе локацию
