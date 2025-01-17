from abc import ABC, abstractmethod


class PageInitializer(ABC):
    def __init__(self, logger):
        self.logger = logger

    @abstractmethod
    def create(self):
        pass
