import util
import asana.error
import itertools

from asana2sql import fields

CREATE_TABLE_TEMPLATE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});""")

INSERT_TEMPLATE = (
        """INSERT INTO "{table_name}" ({columns}) VALUES ({values});""")

class NoSuchProjectException(Exception):
    def __init__(self, project_id):
        super(NoSuchProjectException, self).__init__(
                "No project with id {}".format(project_id))

class Project(object):
    # TODO: Make it all kwargs.
    def __init__(self, asana_client, project_id, table_name, fields):
        self._asana_client = asana_client
        self._project_id = project_id
        self._table_name = table_name
        self._fields = fields

        self._project_data_cache = None
        self._task_cache = None

    def _project_data(self):
        if self._project_data_cache is None:
            try:
                self._project_data_cache = (
                    self._asana_client.projects.find_by_id(self._project_id))
            except asana.error.NotFoundError:
                raise NoSuchProjectException(self._project_id)
        return self._project_data_cache

    def _tasks(self):
        if self._task_cache is None:
            required_fields = set(field_names for field in self._fields
                                              for field_names in field.required_fields())
            self._task_cache = self._asana_client.tasks.find_by_project(
                            self._project_id,
                            fields=",".join(required_fields))
        return self._task_cache

    def table_name(self):
        return util.sql_safe_name(self._table_name if self._table_name else self.project_name())

    def project_name(self):
        return self._project_data()["name"]

    def add_derived_fields(self):
        self._fields += [
                fields.TaskIdPrimaryKeyField(),
                fields.NameField(),
                fields.NotesField(),
                fields.CompletedField(),
                fields.CreatedAtField(),
                fields.NumHearts()]

    def create_table_sql(self):
        return CREATE_TABLE_TEMPLATE.format(
                table_name=self.table_name(),
                columns=",".join([
                        field.field_definition_sql() for field in self._fields]))

    def export_sql(self):
        return "".join(
            self.insert_sql(task) for task in self._tasks())

    def insert_sql(self, task):
        columns = ",".join(field.sql_name for field in self._fields)
        values = ",".join(field.get_data_from_task(task) for field in self._fields)
        return INSERT_TEMPLATE.format(
                table_name=self.table_name(),
                columns=columns,
                values=values)


