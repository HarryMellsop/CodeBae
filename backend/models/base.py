import abc

class BaseModel(abc.ABC):

    def __init__(self, name):
        self.name = name

    # Any implementations that override this predict method should return a list of
    # predictions, in order of their relevance
    @abc.abstractmethod
    def predict(self, file, cursor_index):
        raise NotImplementedError