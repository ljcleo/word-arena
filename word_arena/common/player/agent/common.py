import enum


@enum.unique
class TrialMode(enum.Enum):
    NONE = enum.auto()
    SINGLE = enum.auto()
    MULTIPLE = enum.auto()


@enum.unique
class PromptMode(enum.Enum):
    SIMPLE = enum.auto()
    DIRECT = enum.auto()
    MULTI_TURN = enum.auto()
