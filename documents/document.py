from abc import ABC, abstractmethod
from documents.logging_dir.logging_decorators import init_logger
import zlib


class Document(ABC):

    @staticmethod
    def get_control_sum(text):
        return str(hex(zlib.crc32(str.encode(text)) & 0xffffffff))

    @init_logger
    def __init__(self, user_id, path, primary=False):
        self.user_id = user_id
        self.path = path
        self.primary = primary
        if primary:
            self.set_up_file()
        else:
            self.validate()

    @abstractmethod
    def set_up_file(self) -> None:
        pass

    @abstractmethod
    def validate(self) -> bool:
        pass

    @abstractmethod
    def who_signed(self) -> list:
        pass

    @abstractmethod
    def sign(self) -> None:
        pass

    @abstractmethod
    def is_signed_by(self) -> bool:
        pass
