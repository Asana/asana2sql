import util
import asana.error
import itertools

CREATE_TABLE_TEMPLATE = (
        """CREATE TABLE "{table_name}" (task_id BIGINT NOT NULL,"""
        """{columns}"""
        """PRIMARY KEY task_id)""")

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

    def _project_data(self):
        if self._project_data_cache is None:
            try:
                self._project_data_cache = (
                    self._asana_client.projects.find_by_id(self._project_id))
            except asana.error.NotFoundError:
                raise NoSuchProjectException(self._project_id)
        return self._project_data_cache

    def table_name(self):
        return util.sql_safe_name(self._table_name if self._table_name else self.project_name())

    def project_name(self):
        return self._project_data()["name"]

    def create_table_sql(self):
        return CREATE_TABLE_TEMPLATE.format(
                table_name=self.table_name(),
                columns="".join([
                    fragment for pair in zip(itertools.imap(
                        lambda f: f.field_definition_sql(),
                        self._fields), itertools.repeat(","))
                    for fragment in pair]))

