from celery import Celery


def _task(name, schedule=10.0):
    return {
        name: {
            "task": f"streambot.worker.tasks.{name}.task",
            "schedule": schedule,
            "args": (),
        },
    }


_beat_schedule = {}

_task_names = [
    ("update_active_streams", 100.0),
    ("clear_unknown_messages", 120.0),
    ("clear_stale_streams", 240.0),
    ("get_streams", 60.0),
]

for task, schedule in _task_names:
    _beat_schedule.update(_task(task, schedule=schedule))


app = Celery("tasks", broker="redis://cache:6379")
app.conf.update(
    task_serializer="msgpack",
    accept_content=["msgpack"],
    result_serializer="msgpack",
    include=["streambot.worker.tasks"],
    beat_schedule=_beat_schedule,
    worker_concurrency=2,
)
