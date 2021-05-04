from werkzeug.exceptions import HTTPException 
import flask

class GenericError(HTTPException):
    
    def __init__(self, description, code):
        super().__init__()
        self.code = code
        self.description = description