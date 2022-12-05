import os
import time

from celery import Celery

app = Celery(
    "Streamlit",
    broker=os.environ.get(
        "CELERY_BROKER_URL", "redis://:redis-stack@localhost:6379"),
    backend=os.environ.get(
        "CELERY_RESULT_BACKEND", "redis://:redis-stack@localhost:6379"),
)
app.conf.update(
    timezone='Asia/Kolkata',
    result_serializer='json',
    accept_content=['json'],
    task_serializer='json',
)


@app.task(name="create_task")
def create_task(task_type):
    time.sleep(int(task_type))
    return f"Waited for {task_type}"


@app.task(name="create_task1")
def create_task1(task_type):
    time.sleep(int(task_type))
    return True
