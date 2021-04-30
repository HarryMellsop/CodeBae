from main import app

@app.route('/ping')
def ping_endpoint():
    return 'pong'