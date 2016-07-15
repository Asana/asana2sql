from enum import Enum
import re
import util

FIELD_DEFINITION_TEMPLATE = """"{name}" {type}"""
PRIMARY_KEY_DEFINITION_TEMPLATE = """"{name}" {type} NOT NULL PRIMARY KEY"""

class SqlType(object):
    STRING = "VARCHAR(1024)"
    TEXT = "TEXT"
    INTEGER = "INTEGER"
    DATETIME = "DATETIME"
    DATE = "DATE"
    BOOLEAN = "BOOLEAN"


class Field(object):
    def __init__(self, sql_name, sql_type):
        self.sql_name = sql_name
        self.sql_type = sql_type

    def required_fields(self):
        return set()

    def get_data_from_task(self, task):
        """Get field data from the task object."""
        raise MethodNotImplementedError()

    def field_definition_sql(self):
        """Return the SQL required to define this field."""
        return FIELD_DEFINITION_TEMPLATE.format(
                name=self.sql_name,
                type=self.sql_type)


class SimpleField(Field):
    def __init__(self, name, type, default=None, primary_key=False):
        super(SimpleField, self).__init__(name, type)
        self.name = name
        self.sql_type = type
        self._default = default
        self._primary_key = primary_key

    def required_fields(self):
        return set([self.name])

    def get_data_from_task(self, task):
        data = task.get(self.name)

        if data is None:
            data = self._default

        if self.sql_type == SqlType.BOOLEAN:
            return "1" if data else "0"
        else:
            return data

    def field_definition_sql(self):
        if (self._primary_key):
            return PRIMARY_KEY_DEFINITION_TEMPLATE.format(
                    name=self.sql_name,
                    type=self.sql_type)
        else:
            return FIELD_DEFINITION_TEMPLATE.format(
                    name=self.sql_name,
                    type=self.sql_type)

