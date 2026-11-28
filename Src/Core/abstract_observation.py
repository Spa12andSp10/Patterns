from abc import ABC, abstractmethod
from Src.Core.event_type import event_types

"""Абстрактны наблюдатель"""

class abstract_observation(ABC):

    @abstractmethod
    def handler(self, event_type: event_types, params: object = None) -> None:
        pass