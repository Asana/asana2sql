import util

from asana2sql.cache import Cache

PROJECTS_TABLE_NAME = "projects"
CREATE_PROJECTS_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(1024));
        """)
SELECT_PROJECTS = """SELECT * FROM "{table_name}";"""
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
SELECT_USERS = 'SELECT * FROM "{table_name}";';
INSERT_USER = (
        """INSERT OR REPLACE INTO "{table_name}" VALUES (?, ?);""")

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
        type INTEGER NOT NULL);
        """)
INSERT_CUSTOM_FIELD = (
        """INSERT OR REPLACE INTO "{table_name}" VALUES (?, ?, ?);""")

CUSTOM_FIELD_ENUM_VALUES_TABLE_NAME = "custom_field_enum_values"
CREATE_CUSTOM_FIELD_ENUM_VALUES_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        custom_field_id INTEGER NOT NULL,
        id INTEGER NOT NULL,
        name VARCHAR(1024),
        enabled BOOLEAN NOT NULL,
        color VARCHAR(64) NOT NULL,
        PRIMARY KEY (custom_field_id, id));
        """)
SELECT_CUSTOM_FIELD_ENUM_VALUES = """SELECT * FROM {table_name};"""
SELECT_CUSTOM_FIELD_ENUM_VALUES_FOR_CUSTOM_FIELD = (
        """SELECT * FROM {table_name} WHERE custom_field_id = ?;""")
INSERT_CUSTOM_FIELD_ENUM_VALUE = (
        """INSERT OR REPLACE INTO "{table_name}" VALUES (?, ?, ?, ?, ?);""")
DELETE_CUSTOM_FIELD_ENUM_VALUE = (
        """DELETE FROM "{table_name}" WHERE id = ?;""")

CUSTOM_FIELD_VALUES_TABLE_NAME = "custom_field_values"
CREATE_CUSTOM_FIELD_VALUES_TABLE = (
        """CREATE TABLE IF NOT EXISTS "{table_name}" (
        task_id INTEGER NOT NULL,
        custom_field_id INTEGER NOT NULL,
        text_value TEXT,
        number_value FLOAT,
        enum_value INTEGER,
        PRIMARY KEY (task_id, custom_field_id));
        """)
SELECT_CUSTOM_FIELD_VALUES_FOR_TASK = (
        "SELECT * FROM {table_name} WHERE task_id = ?;")
INSERT_CUSTOM_FIELD_VALUE = (
        "INSERT OR REPLACE INTO {table_name} VALUES (?, ?, ?, ?, ?);")
DELETE_CUSTOM_FIELD_VALUE = (
        "DELETE FROM {table_name} WHERE task_id = ? AND custom_field_id = ?;")

class Workspace(object):
    """Abstraction around all the supporting values for a project that are
    global to the workspace, such as users and custom fields."""

    # TODO: Read and cache the database values so we know what needs updates
    # and can avoid unnecessary database calls.

    def __init__(self, asana_client, db_client, config):
        self._asana_client = asana_client
        self._db_client = db_client
        self._config = config
        self._cache = {}
        self._custom_fields_written = set()

        self.projects = Cache(
                self._fetch_all_fn(SELECT_PROJECTS, self.projects_table_name()),
                self._insert_fn(INSERT_PROJECT, self.projects_table_name(),
                    ["id", "name"]))
        self.users = Cache(
                self._fetch_all_fn(SELECT_USERS, self.users_table_name()),
                self._insert_fn(INSERT_USER, self.users_table_name(),
                    ["id", "name"]))
        self.custom_field_enum_values = Cache(
                self._fetch_all_fn(SELECT_CUSTOM_FIELD_ENUM_VALUES,
                    self.custom_field_enum_values_table_name()),
                self._insert_fn(INSERT_CUSTOM_FIELD_ENUM_VALUE,
                    self.custom_field_enum_values_table_name(),
                    ["custom_field_id", "id", "name", "enabled", "color"]))

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

    def _fetch_all_fn(self, SQL, table_name):
        return lambda: self._db_client.read(SQL.format(table_name=table_name))

    def _insert_fn(self, SQL, table_name, column_keys):
        return lambda obj: self._db_client.write(
                SQL.format(table_name=table_name),
                *[obj[key] for key in column_keys])

    def add_user(self, user):
        self.users.add(user)

    def add_project(self, project):
        self.projects.add(project);

    # Task Membership
    def task_memberships(self, task_id):
        return [row[0] for row in self._db_client.read(
                SELECT_PROJECT_MEMBERSHIPS.format(
                    table_name=self.project_memberships_table_name()),
                task_id)]

    def add_task_to_project(self, task_id, project):
        self.add_project(project)
        self._db_client.write(
                INSERT_PROJECT_MEMBERSHIP.format(
                    table_name=self.project_memberships_table_name()),
                (task_id, project["id"]))

    def remove_task_from_project(self, task_id, project_id):
        self._db_client.write(
                DELETE_PROJECT_MEMBERSHIP.format(
                    table_name=self.project_memberships_table_name()),
                (task_id, project_id))

    # Custom fields
    def add_custom_field(self, custom_field_value):
        """Adds a custom field to the database.

        NB: This depends on the data for the custom field being available in
        the custom_field_value parameter, which is true if custom_fields are
        fetched via the task API.
        """
        if custom_field_value["id"] in self._custom_fields_written:
            return

        self._db_client.write(
                INSERT_CUSTOM_FIELD.format(
                    table_name=self.custom_fields_table_name()),
                custom_field_value["id"],
                custom_field_value["name"],
                custom_field_value["type"]);

        if custom_field_value["type"] == "enum":
            self.add_custom_field_enum_values(custom_field_value["id"])

        self._custom_fields_written.add(custom_field_value["id"])

    def get_custom_field(self, custom_field_id):
        # NB: The python client doesn't support custom fields yet, so we have
        # to fetch manually.
        return self._asana_client.get("/custom_fields/{}".format(custom_field_id), "")

    # Custom field enum values
    def add_custom_field_enum_values(self, custom_field_id):
        custom_field_def = self.get_custom_field(custom_field_id)
        new_enum_options = custom_field_def.get("enum_options", [])

        old_enum_options = {row.id: row
                for row in self.custom_field_enum_values.get(custom_field_id) or []}

        for enum_option in new_enum_options:
            if enum_option["id"] in old_enum_options:
                old_option = old_enum_options[enum_option["id"]]
                del(old_enum_options[enum_option["id"]])
                if (old_option.name == enum_option["name"] and
                    old_option.enabled == enum_option["enabled"] and
                    old_option.color == enum_option["color"]):
                        continue;

            self._db_client.write(
                    INSERT_CUSTOM_FIELD_ENUM_VALUE.format(
                        table_name=self.custom_field_enum_values_table_name()),
                    custom_field_id,
                    enum_option["id"],
                    enum_option["name"],
                    enum_option["enabled"],
                    enum_option["color"])

        for id in old_enum_options.iterkeys():
            self._db_client.write(
                    DELETE_CUSTOM_FIELD_ENUM_VALUE.format(
                        table_name=self.custom_field_enum_values_table_name()),
                    id)

    # Custom field values
    def task_custom_field_values(self, task_id):
        return self._db_client.read(
                    SELECT_CUSTOM_FIELD_VALUES_FOR_TASK.format(
                        table_name=self.custom_field_values_table_name()),
                    task_id)

    def add_custom_field_value(self, task_id, custom_field):
        self.add_custom_field(custom_field)
        self._db_client.write(
                INSERT_CUSTOM_FIELD_VALUE.format(
                    table_name=self.custom_field_values_table_name()),
                task_id,
                custom_field["id"],
                custom_field.get("text_value"),
                custom_field.get("number_value"),
                custom_field.get("enum_value") and
                    custom_field.get("enum_value").get("id"))


    def remove_custom_field_value(self, task_id, custom_field_id):
        self._db_client.write(
                DELETE_CUSTOM_FIELD_VALUE.format(
                    table_name=self.custom_field_values_table_name()),
                task_id,
                custom_field_id)

