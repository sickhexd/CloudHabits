import multiprocessing
bind = "127.0.0.1:5000"
backlog = 2048
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 500
timeout = 30
keepalive = 2
accesslog = "-"  
errorlog = "-"   
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
proc_name = "habit_tracker"
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

