from bot.db_creation import create_locations_db, create_mobs_db, create_person_db, create_items_db, create_items_links_db, \
    create_locations_links_db, create_items_sellers_db
from bot.db_filling import fill_items, fill_locations, fill_location_reachability, fill_items_sellers, \
    fill_mobs

create_locations_db()
create_locations_links_db()
create_mobs_db()
create_person_db()
create_items_db()
create_items_links_db()
create_items_sellers_db()

fill_items()
fill_items_sellers()
fill_locations()
fill_location_reachability()
fill_mobs()