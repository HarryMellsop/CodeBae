from flask_caching import Cache

class SessionCache():

    def __init__(self, app):
        self.cache = Cache(app, config={
            'CACHE_TYPE': 'SimpleCache'
        })
    
    def get(self, session_id):
        try:
            result = self.cache.get(session_id)
            return result
        except Exception as e:
            print('Error loading session cache: ' + str(e), flush=True)
            return None

    def set(self, session_id, data, timeout=None):
        try:
            self.cache.set(session_id, data, timeout=timeout)
        except Exception as e:
            print('Error setting session cache: ' + str(e), flush=True)