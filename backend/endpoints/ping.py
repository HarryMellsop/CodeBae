from main import app


@app.route('/ping', methods=['GET'])
def ping_endpoint():
    return 'pong'