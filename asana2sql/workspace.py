import util

PROJECTS_TABLE_NAME = "projects"
CREATE_PROJECTS_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(1024));
        """)
INSERT_PROJECT = (
        """INSERT OR REPLACE INTO "{table_name}" VALUES (?, ?);""")

PROJECT_MEMBERSHIPS_TABLE_NAME = "project_memberships"
CREATE_PROJECT_MEMBERSHIPS_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        task_id INTEGER NOT NULL,
        project_id INTEGER NOT NULL,
        PRIMARY KEY (task_id, project_id));
        """)
SELECT_PROJECT_MEMBERSHIPS = (
        """SELECT project_id FROM "{table_name}" WHERE task_id = ?;""")
INSERT_PROJECT_MEMBERSHIP = (
        """INSERT OR REPLACE INTO "{table_name}" VALUES (?, ?);""")
DELETE_PROJECT_MEMBERSHIP = (
        """DELETE FROM "{table_name}" WHERE task_id = ? and project_id = ?;""")

USERS_TABLE_NAME = "users"
CREATE_USERS_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(1024));
        """)
INSERT_USER = (
        """INSERT OR REPLACE INTO "{table_name}" VALUES (?, ?)""")

FOLLOWERS_TABLE_NAME = "followers"
CREATE_FOLLOWERS_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        task_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        PRIMARY KEY (task_id, user_id));
        """)

CUSTOM_FIELDS_TABLE_NAME = "custom_fields"
CREATE_CUSTOM_FIELDS_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(1024),
        type INTEGER NOT NULL)
        """)

CUSTOM_FIELD_ENUM_VALUES_TABLE_NAME = "custom_field_enum_values"
CREATE_CUSTOM_FIELD_ENUM_VALUES_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(1024),
        enabled BOOLEAN NOT NULL,
        color VARCHAR(64) NOT NULL)
        """)

CUSTOM_FIELD_VALUES_TABLE_NAME = "custom_field_values"
CREATE_CUSTOM_FIELD_VALUES_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER NOT NULL,
        task_id INTEGER NOT NULL,
        text_value TEXT,
        number_value FLOAT,
        enum_value INTEGER,
        PRIMARY KEY (id, task_id))
        """)

class Workspace(object):
    """Abstraction around all the supporting values for a project that are
    global to the workspace, such as users and custom fields."""

    # TODO: Read and cache the database values so we know what needs updates
    # and can avoid unnecessary database calls.

    def __init__(self, asana_client, db_client, config):
        self._asana_client = asana_client
        self._db_client = db_client
        self._config = config

    def projects_table_name(self):
        return self._config.projects_table_name or PROJECTS_TABLE_NAME

    def project_memberships_table_name(self):
        return self._config.project_memberships_table_name or PROJECT_MEMBERSHIPS_TABLE_NAME

    def users_table_name(self):
        return self._config.users_table_name or USERS_TABLE_NAME

    def followers_table_name(self):
        return self._config.followers_table_name or FOLLOWERS_TABLE_NAME

    def custom_fields_table_name(self):
        return self._config.custom_fields_table_name or CUSTOM_FIELDS_TABLE_NAME

    def custom_field_enum_values_table_name(self):
        return self._config.custom_field_enum_values_table_name or CUSTOM_FIELD_ENUM_VALUES_TABLE_NAME

    def custom_field_values_table_name(self):
        return self._config.custom_field_values_table_name or CUSTOM_FIELD_VALUES_TABLE_NAME

    def create_tables(self):
        self._db_client.write(
                CREATE_PROJECTS_TABLE.format(
                    table_name=self.projects_table_name()))
        self._db_client.write(
                CREATE_PROJECT_MEMBERSHIPS_TABLE.format(
                    table_name=self.project_memberships_table_name()))
        self._db_client.write(
                CREATE_USERS_TABLE.format(
                    table_name=self.users_table_name()))
        self._db_client.write(
                CREATE_FOLLOWERS_TABLE.format(
                    table_name=self.followers_table_name()))
        self._db_client.write(
                CREATE_CUSTOM_FIELDS_TABLE.format(
                    table_name=self.custom_fields_table_name()))
        self._db_client.write(
                CREATE_CUSTOM_FIELD_ENUM_VALUES_TABLE.format(
                    table_name=self.custom_field_enum_values_table_name()))
        self._db_client.write(
                CREATE_CUSTOM_FIELD_VALUES_TABLE.format(
                    table_name=self.custom_field_values_table_name()))

    def ensure_user_exists(self, user):
        self._db_client.write(
                INSERT_USER.format(
                    table_name=self.users_table_name()),
                (user["id"], user["name"]))

    def ensure_project_exists(self, project):
        self._db_client.write(
                INSERT_PROJECT.format(
                    table_name=self.projects_table_name()),
                (project["id"], project["name"]))

    def task_memberships(self, task_id):
        return [row[0] for row in self._db_client.read(
                SELECT_PROJECT_MEMBERSHIPS.format(
                    table_name=self.project_memberships_table_name()),
                task_id)]

    def add_task_to_project(self, task_id, project):
        self.ensure_project_exists(project)
        self._db_client.write(
                INSERT_PROJECT_MEMBERSHIP.format(
                    table_name=self.project_memberships_table_name()),
                (task_id, project["id"]))

    def remove_task_from_project(self, task_id, project_id):
        self._db_client.write(
                DELETE_PROJECT_MEMBERSHIP.format(
                    table_name=self.project_memberships_table_name()),
                (task_id, project_id))

