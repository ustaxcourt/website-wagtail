from abc import ABC, abstractmethod


class PageInitializer(ABC):
    @abstractmethod
    def create(self):
        pass
