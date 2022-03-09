from .connection import connection

from .reservation import Reservation, MemberReservation
from .stream import Stream, MemberStream

connection.connect()
connection.create_tables([Reservation, MemberReservation, Stream, MemberStream])
