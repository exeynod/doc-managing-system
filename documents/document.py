from abc import ABC, abstractmethod

class Document(ABC):

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
