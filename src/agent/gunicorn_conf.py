import os
from distutils.util import strtobool

# -------------------------- Server Socket -------------------------- #
bind = f'{os.getenv("HOST", "0.0.0.0")}:{os.getenv("PORT", "8001")}'
backlog = int(os.getenv("GUNICORN_BACKLOG", "512"))

# ----------------------------- Logging ----------------------------- #
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = os.getenv("ACCESS_LOG", "-") or None
errorlog = os.getenv("ERROR_LOG", "-") or None

# ------------------------ Worker Processes ------------------------- #
workers = int(os.getenv("WEB_CONCURRENCY", "2"))
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "1000"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "500"))

# Timeouts
graceful_timeout = int(os.getenv("GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("KEEP_ALIVE", "30"))
timeout = int(os.getenv("TIMEOUT", "120"))

# ------------------------ Server Mechanics ------------------------- #
preload_app = bool(strtobool(os.getenv("GUNICORN_PRELOAD_APP", "true")))
worker_tmp_dir = "/dev/shm"
