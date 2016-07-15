import util
import asana.error
import itertools

from asana2sql import fields
from asana2sql import workspace


#TODO: parameterize commands.

CREATE_TABLE_TEMPLATE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});""")

INSERT_OR_REPLACE_TEMPLATE = (
        """INSERT OR REPLACE INTO "{table_name}" ({columns}) VALUES ({values});""")

SELECT_TEMPLATE = (
        """SELECT {columns} FROM "{table_name}";""")

DELETE_TEMPLATE = (
        """DELETE FROM "{table_name}" WHERE {id_column} = {id_value};""")

class CustomFieldType(object):
    TEXT = 0
    NUMBER = 1
    ENUM = 2

class NoSuchProjectException(Exception):
    def __init__(self, project_id):
        super(NoSuchProjectException, self).__init__(
                "No project with id {}".format(project_id))

class Project(object):
    # TODO: Make it all kwargs.
    def __init__(self, asana_client, db_client, config, fields):
        self._asana_client = asana_client
        self._db_client = db_client
        self._config = config
        self._fields = fields

        self._project_id = self._config.project_id
        self._table_name = self._config.table_name

        self._project_data_cache = None
        self._task_cache = None
        self._workspace = workspace.Workspace(asana_client, db_client, config)

    def _project_data(self):
        if self._project_data_cache is None:
            try:
                self._project_data_cache = (
                    self._asana_client.projects.find_by_id(self._project_id))
            except asana.error.NotFoundError:
                raise NoSuchProjectException(self._project_id)
        return self._project_data_cache

    def _required_fields(self):
        return set(field_names for field in self._fields
                               for field_names in field.required_fields())

    def _tasks(self):
        if self._task_cache is None:
            self._task_cache = list(self._asana_client.tasks.find_by_project(
                            self._project_id,
                            fields=",".join(self._required_fields())))
        return self._task_cache

    def table_name(self):
        return util.sql_safe_name(self._table_name if self._table_name else self.project_name())

    def project_name(self):
        return self._project_data()["name"]

    def add_derived_fields(self):
        self._fields += fields.default_fields(self._workspace)

    def create_table(self):
        sql = CREATE_TABLE_TEMPLATE.format(
                table_name=self.table_name(),
                columns=",".join([
                        field.field_definition_sql() for field in self._fields]))
        self._db_client.write(sql)

    def export(self):
        for task in self._tasks():
            self.insert_or_replace(task)

    def insert_or_replace(self, task):
        columns = ",".join(field.sql_name for field in self._fields)
        values = ",".join("?" for field in self._fields)
        params = [field.get_data_from_task(task) for field in self._fields]
        self._db_client.write(
                INSERT_OR_REPLACE_TEMPLATE.format(
                    table_name=self.table_name(),
                    columns=columns,
                    values=values),
                *params)

    def delete(self, task_id):
        id_field = self._id_field()
        self._db_client.write(
                DELETE_TEMPLATE.format(
                    table_name=self.table_name(),
                    id_column=id_field.sql_name,
                    id_value=task_id))

    def synchronize(self):
        db_task_ids = self.db_task_ids()
        asana_task_ids = self.asana_task_ids()

        ids_to_remove = db_task_ids.difference(asana_task_ids)

        for task in self._tasks():
            self.insert_or_replace(task)

        for id_to_remove in ids_to_remove:
            self.delete(id_to_remove)

    def asana_task_ids(self):
        return set(task.get("id") for task in self._tasks())

    def _id_field(self):
        return self._fields[0]  # TODO: make the id field special.

    def db_task_ids(self):
        id_field = self._id_field()
        return set(row[0] for row in self._db_client.read(
                SELECT_TEMPLATE.format(
                    table_name=self.table_name(),
                    columns=id_field.sql_name)))

