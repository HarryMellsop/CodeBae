name = 'gunicorn-server'
bind = '0.0.0.0:8050'

workers = 1
threads = 8
timeout = 5

loglevel = 'info'
