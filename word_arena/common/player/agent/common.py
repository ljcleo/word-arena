import enum


@enum.unique
class TrialMode(enum.Enum):
    NONE = enum.auto()
    SINGLE = enum.auto()
    MULTIPLE = enum.auto()
