from streambot import env
from peewee import SqliteDatabase

connection = SqliteDatabase(env("DB_LOCATION", default="/code/data.db"))
