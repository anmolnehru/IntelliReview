from abc import ABC, abstractmethod

class LLMBase(ABC):
    @abstractmethod
    def invoke(self, input: dict) -> str:
        pass