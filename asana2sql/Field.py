from enum import Enum


class SqlType(Enum):
    string = 1
    int = 2
    float = 3


class Field:
    def __init__(self):
        self.asana_name = ""
        self.sql_name = ""
        self.type = SqlType.string
