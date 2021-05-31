import abc
import codecs
import pickle

class BaseModel(abc.ABC):
    finetune_implemented = False

    def __init__(self, name):
        self.name = name
        self.finetuned = False

    def is_finetuned(self) -> bool:
        return self.finetuned

    def can_finetune(self) -> bool:
        return self.finetune_implemented

    @abc.abstractmethod
    def predict(self, file, cursor_index, use_finetune=True) -> list:
        # *** Abstract predict method *** 
        # Description: 
        #     Defines template that model subclasses should use for implementing their
        #     own prediction routine. All predict implementation will receive the `file` and 
        #     `cursor_index` parameters as inputs; the former is the raw working code file, 
        #     while the later is the cursor position within said file. Additionally, the 
        #     `use_fintune` parameter indicates whether the prediction routine should be called
        #     with the current finetuned model or not.

        raise NotImplementedError

    @abc.abstractmethod
    def finetune(self, files) -> None:
        # *** Abstract finetune method *** 
        # Description: 
        #     Defines template that model subclasses should use for implementing their
        #     own finetune routine. The method simply receives a collection of data files
        #     on which to finetune as input and is expected to internally finetune without
        #     returning the resulting model.

        raise NotImplementedError

    @staticmethod
    def save(obj):
        return codecs.encode(pickle.dumps(obj), 'base64').decode()

    @staticmethod
    def load(obj_serial):
        return pickle.loads(codecs.decode(obj_serial.encode(), 'base64'))

