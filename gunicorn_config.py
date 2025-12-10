# gunicorn_config.py
import os
from dotenv import load_dotenv

load_dotenv()

bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
loglevel = "info"
accesslog = "-"
errorlog = "-"
timeout = 30

# Кастомное имя сервера для скрытия информации
def on_starting(server):
    server.log.info("Starting protected server...")

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def when_ready(server):
    server.log.info("Server is ready. Serving on %s", bind)

def pre_fork(server, worker):
    pass

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")