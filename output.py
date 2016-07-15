
class DatabaseWrapper(object):

    def __init__(self, db_client, dump_sql=False, dry=False):
        self._db_client = db_client
        self._dump_sql = dump_sql
        self._dry = dry
        self._cursor = None

    def read(self, sql):
        """Execute a read-only SQL statement and return the result rows."""
        if self._dump_sql:
            print(sql)

        self._execute_sql(sql)

        return self._cursor.fetchall()

    def write(self, sql):
        """Execute a write SQL statement."""
        if self._dump_sql:
            if self._dry:
                print("# " + sql)
            else:
                print(sql)

        self._execute_sql(sql)

    def _execute_sql(self, sql):
        if not self._cursor:
            self._cursor = self._db_client.cursor()
        self._cursor.execute(sql)
