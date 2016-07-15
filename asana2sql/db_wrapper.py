
class DatabaseWrapper(object):

    def __init__(self, db_client, dump_sql=False, dry=False):
        self._db_client = db_client
        self._dump_sql = dump_sql
        self._dry = dry
        self._cursor = None

    def read(self, sql, *params):
        """Execute a read-only SQL statement and return the result rows."""
        if self._dump_sql:
            print(sql + " " + repr(params))

        self._execute_sql(sql, *params)

        return self._cursor.fetchall()

    def write(self, sql, *params):
        """Execute a write SQL statement."""
        if self._dump_sql:
            if self._dry:
                print("# " + sql + " " + repr(params))
            else:
                print(sql + " " + repr(params))

        self._execute_sql(sql, *params)

    def _execute_sql(self, sql, *params):
        if not self._cursor:
            self._cursor = self._db_client.cursor()
        self._cursor.execute(sql, *params)
