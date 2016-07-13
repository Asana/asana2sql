#!/usr/bin/env python

import argparse
import requests

from asana2sql.project import Project
from asana import Client

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

    # Commands
    subparsers = parser.add_subparsers(
            title="Commands",
            dest="command")


    create_table_parser = subparsers.add_parser(
            'create',
            help="Create tables for the project.")

    export_parser = subparsers.add_parser(
            'export',
            help="Export the tasks in the project to SQL.")
    export_parser.add_argument("--include-complete",
            dest="include_complete",
            action='store_true',
            help="Include completed tasks.")
    export_parser.add_argument("--no-include-complete",
            dest="include_complete",
            action='store_false',
            help="Exclude completed tasks.")

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

    if args.derive_fields:
        project.add_derived_fields()

    if args.command == 'create':
        print(project.create_table_sql())

    if args.command == 'export':
        print(project.export_sql())


if __name__ == '__main__':
    main()

