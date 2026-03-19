from abc import ABC, abstractmethod


class BaseConfigReader[MT, CT](ABC):
    @abstractmethod
    def read_config(self, *, meta_config: MT) -> CT: ...
