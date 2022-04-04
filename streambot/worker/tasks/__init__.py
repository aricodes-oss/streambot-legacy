from streambot.celery import app

from . import update_active_streams, clear_unknown_messages, clear_stale_streams, get_streams

_imported = [update_active_streams, clear_unknown_messages, clear_stale_streams, get_streams]

for f in _imported:
    app.task(f.task)
