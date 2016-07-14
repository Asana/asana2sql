#!/usr/bin/env python

import argparse
import pyodbc
import requests

from asana2sql.project import Project
from output import DatabaseWrapper
from asana import Client, session

def arg_parser():
    parser = argparse.ArgumentParser()

    # Global options
    parser.add_argument('--project_id',
            type=int,
            required=True,
            help="Asana project ID.")

    parser.add_argument('--table_name',
            help=("Name of the SQL table to use."
                  "If not specified it will be derived from the project name."))

    parser.add_argument("--derive_fields",
            action='store_true',
            help="Adds default columns, e.g. created_at, completed, all custom fields.");

    # Asana Client options
    asana_args = parser.add_argument_group('Asana Client Options')

    auth_args = asana_args.add_mutually_exclusive_group(required=True)
    auth_args.add_argument(
            "--api_key",
            help="Asana API Key (deprecated).")

    auth_args.add_argument(
            "--access_token",
            help="Asana Personal Access Token for authentication.")

    asana_args.add_argument(
            "--base_url",
            default="https://app.asana.com/api/1.0",
            help="URL of the Asana API server.")

    asana_args.add_argument(
            "--no_verify",
            dest="verify",
            default=True,
            action="store_false",
            help="Turn off HTTPS verification.")

    # DB options
    db_args = parser.add_argument_group('Database Options')

    db_args.add_argument(
            "--odbc_string",
            help="ODBC connection string.")

    db_args.add_argument(
            "--dump_sql",
            action="store_true",
            default=False,
            help="Dump SQL commands to STDOUT.")

    db_args.add_argument(
            "--dry",
            action="store_true",
            default=False,
            help="Dry run.  Do not actually run any writes to the database.")

    # Commands
    subparsers = parser.add_subparsers(
            title="Commands",
            dest="command")

    create_table_parser = subparsers.add_parser(
            'create',
            help="Create tables for the project.")

    export_parser = subparsers.add_parser(
            'export',
            help="Export the tasks in the project, "
                 "not deleting deleted tasks from the database.")

    """
    export_parser.add_argument("--include-complete",
            dest="include_complete",
            action='store_true',
            help="Include completed tasks.")
    export_parser.add_argument("--no-include-complete",
            dest="include_complete",
            action='store_false',
            help="Exclude completed tasks.")
            """

    return parser

def build_asana_client(args):
    options = {}
    if args.base_url:
        options['base_url'] = args.base_url
    if args.api_key:
        options['auth'] = requests.auth.HTTPBasicAuth(args.api_key, '')
    if args.access_token:
        options['session'] = session.AsanaOAuth2Session(
                token={'access_token': args.access_token})
    if args.verify is not None:
        # urllib3.disable_warnings()
        options['verify'] = args.verify

    return Client(**options);

def main():
    args = arg_parser().parse_args()

    client = build_asana_client(args)

    project = Project(client, args.project_id, args.table_name, [])

    db_client = None
    if args.odbc_string:
        print("Connecting to database.")
        db_client = pyodbc.connect(args.odbc_string)

    db_wrapper = DatabaseWrapper(db_client, dump_sql=args.dump_sql, dry=args.dry)

    if args.derive_fields:
        project.add_derived_fields()

    if args.command == 'create':
        project.create_table(db_wrapper)
    elif args.command == 'export':
        project.export(db_wrapper)

    db_wrapper.commit()


if __name__ == '__main__':
    main()

