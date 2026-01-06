from abc import ABC, abstractmethod


class BaseAIProvider(ABC):

    @abstractmethod
    def extract(self, text: str) -> dict:
        """
        Takes raw text and returns structured JSON
        """
        pass
