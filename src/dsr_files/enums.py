from enum import Flag, auto


class FileType(Flag):
    CSV = auto()
    JSON = auto()
    JOBLIB = auto()
    PDF = auto()
    EXCEL = auto()
