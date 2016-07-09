from enum import Enum
import util

FIELD_DEFINITION_TEMPLATE = """"{name}" {type}"""

class Field(object):
    def __init__(self, asana_name, sql_type, sql_name = None):
        self._asana_name = asana_name
        self._sql_name = sql_name
        self._sql_type = sql_type

    def sql_name(self):
        return util.sql_safe_name(self._sql_name if self._sql_name else self._asana_name)

    def asana_name(self):
        return self._asana_name

    def sql_type(self):
        return self._sql_type

    def get_data_from_task(self, task):
        """Get field data from the task object."""
        pass

    def field_definition_sql(self):
        return FIELD_DEFINITION_TEMPLATE.format(
                name=self.sql_name(),
                type=self.sql_type())
