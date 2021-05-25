import abc
import codecs
import pickle

class BaseModel(abc.ABC):

    def __init__(self, name):
        self.name = name
        self.finetuned = False

    # Any implementations that override this predict method should return a list of
    # predictions, in order of their relevance
    @abc.abstractmethod
    def predict(self, file, cursor_index, use_finetune=True):
        raise NotImplementedError

    @abc.abstractmethod
    def finetune(self, files):
        raise NotImplementedError

    def is_finetuned(self):
        return self.finetuned

    @abc.abstractmethod
    def save(self):
        raise NotImplementedError

    @staticmethod
    def save(obj):
        return codecs.encode(pickle.dumps(obj), 'base64').decode()

    @staticmethod
    def load(obj_serial):
        return pickle.loads(codecs.decode(obj_serial.encode(), 'base64'))