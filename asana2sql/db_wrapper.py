
class DatabaseWrapper(object):
    """A simple wrapper for a DB API 2.0 connection.

    It supports two additional options:
      dump_sql will print all SQL commands to STDOUT.
      dry will prevent any write commands from actuallye executing.
    """

    def __init__(self, db_conn, dump_sql=False, dry=False):
        self._db_conn = db_conn
        self._dump_sql = dump_sql
        self._dry = dry
        self._cursor = None

        self._num_reads = 0
        self._num_writes = 0
        self._num_executed = 0

    @property
    def num_reads(self):
        """Number of reads issued."""
        return self._num_reads

    @property
    def num_writes(self):
        """Number of writes issued."""
        return self._num_writes

    @property
    def num_executed(self):
        """Number of SQL commands executed."""
        return self._num_executed

    def read(self, sql, *params):
        """Execute a read-only SQL statement and return the result rows."""
        self._num_reads += 1

        if self._dump_sql:
            print(sql + " " + repr(params))

        self._execute_sql(sql, *params)

        return self._cursor.fetchall()

    def write(self, sql, *params):
        """Execute a write SQL statement."""
        self._num_writes += 1

        if self._dump_sql:
            if self._dry:
                print("# " + sql + " " + repr(params))
            else:
                print(sql + " " + repr(params))

        if not self._dry:
            self._execute_sql(sql, *params)

    def _execute_sql(self, sql, *params):
        if not self._cursor:
            self._cursor = self._db_conn.cursor()
        self._num_executed += 1
        self._cursor.execute(sql, *params)
