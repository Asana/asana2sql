# asana2sql

asana2sql is a utility for exporting Asana data to SQL databases.  It assumes a
one-to-one mapping between tasks in Asana and rows in the database.  It can
handle creating tables, exporting data, synchronizing data, mapping to various
database types and more.

The asana2sql script uses [PyODBC](https://github.com/mkleehammer/pyodbc) for
database connectivity, so will work with any database for which you have ODBC
configured.  It uses very generic SQL commands to provide maximum
compatibility.  As a library it is compatible with any
[PEP 249 (DB API 2.0)](https://www.python.org/dev/peps/pep-0249/) object.

It is very configurable.  While the project includes a script that uses a
default set of fields that should cover most needs, new fields can be easily
written to support custom database types or compute data from one or more fields.

## The asana2sql Script

### Basic Usage

asana2sql comes out of the box with a script that will cover most use-cases.

In the following examples assume that:

* Your database is an SQLite database and your ODBC driver is registered as
  `SQLite3`.
* You have an Asana API access token of `0/123456789abcdef`.
* The ID of your project is `1234567890` and it's name is `Project Name`.

Most options are self-explanatory and limited help can be found by passing
either the `-h` or `--help` option.

The only required options are the `api-token` and `command`.

### Creating Tables

Tables can be generated using the `create` command.  This includes a table for
the project and the additional tables needed to normalize the data.  The tables
will be in third normal form.

```
asana2sql.py --access_token 0/123456789abcdef --project_id 1234567890 \
    --odbc_string 'DRIVER={SQLite3};DATABASE=test.sqlite;BigInt=yes' create
```

This will create the following tables:

* `Project Name` - A table for tasks in the project, named after the project.
* `projects` - IDs and names of projects that tasks are members of.
* `project_memberships` - A join-table between projects and tasks.
* `users` - Additional IDs and names of users assigned two or owning tasks.
* `followers` - A join-table between tasks and users for the "following"
  attribute.
* `custom_fields` - Definitions of any custom fields the tasks have.
* `custom_field_enum_values` - Definitions of any custom field enum values the
  tasks may have.
* `custom_field_values` - A join-table between tasks and custom fields with
  the values of those fields.

### Exporting or Synchronizing Data

Data can be exported in a one-way dump of data using the `export` or
`synchronize` commands.  The difference between these two commands is that
`export` does not delete rows for tasks that are no longer present in Asana.
`synchronize` will ensure that removed tasks are also removed from the output.
Both commands will automatically manage the supporting values and join tables.

```
asana2sql.py --access_token 0/123456789abcdef --project_id 1234567890 \
    --odbc_string 'DRIVER={SQLite3};DATABASE=test.sqlite;BigInt=yes' synchronize
```

## As a Library

### Defining fields

A field definition maps to at most one column in the tasks table.  If you need
multiple columns you will need to implement one field per column.

Each field needs to provide three things:

* The name of the field, which will be used in SELECT and INSERT commands.
* The column definition SQL, which is used in CREATE TABLE commands.  This
  should output the entire column definition including any column options.
* A method for extracting data from a task object.  The entire task is available
  to the field, so it is simple to synthesize data from multiple fields.  The
  Workspace or Database Client can also be passed to the field on construction
  if join tables or other supporting data needs to be updated.

Fields are then passed to the Project which manages the synchronization.  Note
that the first field is assumed to be the unique key, most likely the task ID.

### Denormalized data

If your application requires the data be denormalized, this can be easily
achieved by writing custom field definitions.  For example, you could write a
field that stores the name of a custom-field enum value directly in the row
instead of joining through the `custom_field_values` table.
