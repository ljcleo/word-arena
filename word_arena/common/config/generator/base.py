from abc import ABC, abstractmethod
from random import Random


class BaseConfigGenerator[MT, UT, CT](ABC):
    @abstractmethod
    def __call__(self, *, meta_config: MT, mutable_meta_config: UT, rng: Random) -> CT: ...
