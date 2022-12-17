import random
import os
import sqlite3
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from secret import TOKEN
from create_db import create_locations_db, create_mobs_db, create_person_db, create_items_db

create_locations_db()
create_mobs_db()
create_person_db()
create_items_db()
