# asana2sql

asana2sql is a utility for exporting Asana data to SQL databases.  It assumes a
one-to-one mapping between tasks in Asana and rows in the database.  It can
handle creating tables, exporting data, synchronizing data, mapping data
database types and more.

asana2sql uses PyODBC for database connectivity, so will work with any database
for which you have ODBC configured.  It uses very generic SQL commands to
provide maximum compatibility.

It is also very configurable.  While the project includes a script that uses a
default set of fields, new fields can be easily written to support custom
database types or compute data from one or more fields.

## Basic Usage

asana2sql comes out of the box with a script that will cover most use-cases.
Only a few options are truely required.

In the following examples assume that:

* Your database is an SQLite database and your ODBC driver is registered as
  `SQLite3`.
* You have an Asana API access token of `0/123456789abcdef`.
* The ID of your project is `1234567890`.

### Creating Tables

Tables can be automatically created.  This includes a table for the project and
the additional tables needed to normalize the data.  The tables will be in
third normal form.

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

## Advanced Usage

### Denormalized data

If your application requires the data be denormalized, this can be easily
achieved by writing custom fields.  For example, you could write a field that
stores the name of a custom-field enum value directly in the row instead of
joining through the `custom_field_values` table.


