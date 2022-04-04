from .connection import connection

from .reservation import Reservation
from .stream import Stream
from .twitch_stream import TwitchStream

connection.connect()
connection.create_tables([Reservation, Stream, TwitchStream])
