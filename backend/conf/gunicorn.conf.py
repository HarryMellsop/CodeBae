name = 'gunicorn-server'
bind = '0.0.0.0:80'

workers = 1
threads = 1
timeout = 120

loglevel = 'info'
