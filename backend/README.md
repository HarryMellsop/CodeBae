![CodeBae Logo](https://i.imgur.com/IvPQXGI.png)

## Startup Team Assignment
https://github.com/StanfordCS194/Team11/wiki/Team-Home-Page/

## Backend Commands

### Start Server

To start the Flask server, we will first create or attach to a tmux session. First, check to see if there is an existing tmux server session using the following command:

```bash
tmux list-sessions
```

If there are no sessions running, we will start a new tmux server session as follows:

```bash
tmux new -s server
```

If there is already a session running, we can connect to it directly:

```bash
tmux attach-session -t server
```

Once inside the tmux server session, we will want to enter our virtual environment containing dependencies for running the web server. If a local virtual environment hasn't yet been set up, the following commands can be used at the root `backend` directory to do so:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

This virtual environment can be released at any time by using the following command:

```bash
deactivate
```

Finally, we will initialize the Flask web server application by using Gunicorn, a portable WSGI (Web Server Gateway Interface). The Gunicorn launcher will automatically import configuration settings from the `conf/gunicorn.conf.py` file and spool up the Flask application in `main.py`. This can be done with the following command (inside tmux and within the virtual environment from above):

```bash
gunicorn main:app -c conf/gunicorn.conf.py
```

### Stop Server 

Safely shutting down the web server can be done by simply attaching to the tmux session as illustrated above and entering CTRL+C. Note that the tmux server should not be externally shut down or killed as this will result in the  background Gunicorn workers being orphaned (which can only be cleared out by restarting the instance or manually sending a SIGKILL to the worker PIDs).