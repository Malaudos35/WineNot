# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 1
worker_class = "sync"
