from abc import ABC, abstractmethod


class BaseConfigReader[MT, CT](ABC):
    @abstractmethod
    def __call__(self, *, meta_config: MT) -> CT: ...
