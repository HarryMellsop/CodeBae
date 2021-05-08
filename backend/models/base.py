import abc

class BaseModel(abc.ABC):

    def __init__(self, name):
        self.name = name

    @abc.abstractmethod
    def predict(self, file, cursor_index):
        raise NotImplementedError
