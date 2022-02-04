from celery import Celery

app = Celery("tasks", broker="redis://cache:6379")
app.conf.update(
    task_serializer="msgpack",
    accept_content=["msgpack"],
    result_serializer="msgpack",
    include=["streambot.tasks"],
    beat_schedule={
        "update-cached-streams": {
            "task": "streambot.tasks.update_cached_streams",
            "schedule": 30.0,
            "args": (),
        },
    },
)
