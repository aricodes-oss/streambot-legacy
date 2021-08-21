from .connection import connection

from .reservation import Reservation
from .stream import Stream

connection.connect()
connection.create_tables([Reservation, Stream])
