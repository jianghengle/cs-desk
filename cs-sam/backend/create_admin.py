#!/usr/bin/env python3
"""
Create an admin user directly in the CsUsers DynamoDB table.

The item layout mirrors UserModel.create() in backend/app/models/user_model.py:
uuid id, bcrypt-hashed password, 64-char alphanumeric token, epoch timestamps.

Usage:
    pip install boto3 bcrypt
    python create_admin.py --email admin@example.com --username admin --profile my-profile

The password is prompted interactively (not passed on the command line) so it
doesn't end up in shell history. Set CS_ADMIN_PASSWORD to run non-interactively.
"""
import argparse
import getpass
import os
import secrets
import string
import sys
import time
import uuid

import bcrypt
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Resolves because this script lives in backend/, next to the app package.
from app.models.user_model import UserModel

DEFAULT_REGION = 'us-west-2'
MIN_PASSWORD_LENGTH = 8


def parse_args():
    parser = argparse.ArgumentParser(description='Create an admin user in the CsUsers table.')
    parser.add_argument('--email', required=True, help='Admin email (must be unique)')
    parser.add_argument('--username', required=True, help='Admin username')
    parser.add_argument('--groups', nargs='*', default=[], help='Optional list of groups')
    parser.add_argument('--profile', help='AWS profile to use (default: default credential chain)')
    parser.add_argument('--region', default=DEFAULT_REGION, help=f'AWS region (default: {DEFAULT_REGION})')
    parser.add_argument('--table', help=f'Table name override (default: {UserModel.TableName})')
    parser.add_argument('--dry-run', action='store_true', help='Print the item without writing it')
    return parser.parse_args()


def read_password():
    password = os.environ.get('CS_ADMIN_PASSWORD')
    if password is None:
        password = getpass.getpass('Admin password: ')
        if password != getpass.getpass('Confirm password: '):
            sys.exit('Error: passwords do not match.')
    if len(password) < MIN_PASSWORD_LENGTH:
        sys.exit(f'Error: password must be at least {MIN_PASSWORD_LENGTH} characters.')
    return password


def build_item(email, username, password, groups):
    timestamp = int(time.time())
    alphabet = string.ascii_letters + string.digits
    return {
        'id': str(uuid.uuid4()),
        'email': email,
        'username': username,
        'encryptedPassword': bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'),
        'isAdmin': True,
        'groups': groups,
        'token': ''.join(secrets.choice(alphabet) for _ in range(64)),
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }


def main():
    args = parse_args()
    table_name = args.table or UserModel.TableName
    email = args.email.strip()
    password = read_password()
    item = build_item(email, args.username.strip(), password, args.groups)

    if args.dry_run:
        preview = {**item, 'encryptedPassword': '<bcrypt hash>', 'token': '<64-char token>'}
        print(f'Dry run, table {table_name}, item would be:')
        for k, v in preview.items():
            print(f'  {k}: {v!r}')
        return

    session = boto3.Session(profile_name=args.profile, region_name=args.region)
    account = session.client('sts').get_caller_identity()['Account']
    table = session.resource('dynamodb').Table(table_name)
    print(f'Account {account}, region {args.region}, table {table_name}')

    try:
        # Email uniqueness isn't enforced by DynamoDB, so check the GSI first.
        existing = table.query(IndexName='emailGSI', KeyConditionExpression=Key('email').eq(email), Limit=1)
        if existing.get('Items'):
            sys.exit(f'Error: a user with email {email} already exists (id={existing["Items"][0]["id"]}).')

        table.put_item(Item=item, ConditionExpression='attribute_not_exists(id)')
    except ClientError as e:
        sys.exit(f'Error: {e.response["Error"]["Code"]}: {e.response["Error"]["Message"]}')

    print(f'Created admin user {email} (id={item["id"]})')


if __name__ == '__main__':
    main()
