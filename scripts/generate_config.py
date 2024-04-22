#!/usr/bin/env python3
# Copyright 2024 Chris Farris <chrisf@primeharbor.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys, argparse, os
import boto3
from botocore.exceptions import ClientError
import json

def main(args):

    aws_config_file = f"""
[default]
region=us-east-1

"""

    # we need to create an aggregate of payers, by the payer names
    payer_names = []
    steampipe_connections = ""

    accounts = list_accounts()
    for a in accounts:
        sp_account_name = a['Name'].replace('-', '_').replace(' ', '_').lower()
        aws_account_name = a['Name'].replace(' ', '_').lower()

        aws_config_file += f"""
# {a['Name']}
[profile {aws_account_name}]
role_arn = arn:aws:iam::{a['Id']}:role/{args.rolename}
credential_source = {args.credential_source}
# source_profile = default
role_session_name = {args.role_session_name}
"""

        steampipe_connections += f"""
connection "aws_{sp_account_name}" {{
  plugin  = "aws"
  profile = "{aws_account_name}"
  regions = ["*"]
}}
"""

    steampipe_spc_file = f"""
# Create an aggregator of _all_ the accounts as the first entry in the search path.
connection "aws" {{
  plugin = "aws"
  type = "aggregator"
  connections = ["aws_*"]
}}

{steampipe_connections}

"""

    file = open(os.path.expanduser(args.aws_config_file), "w")
    file.write(aws_config_file)
    file.close()

    file = open(os.path.expanduser(args.steampipe_connection_file), "w")
    file.write(steampipe_spc_file)
    file.close()
    exit(0)


def list_accounts():
    try:
        # Doing this assumes you're in an account that is a Delegated Administrator for any service that supports Delegated Admin.
        org_client = boto3.client('organizations', region_name = "us-east-1")

        output = []
        response = org_client.list_accounts(MaxResults=20)
        while 'NextToken' in response:
            output = output + response['Accounts']
            response = org_client.list_accounts(MaxResults=20, NextToken=response['NextToken'])

        output = output + response['Accounts']
        return(output)
    except ClientError as e:
        if e.response['Error']['Code'] == 'AWSOrganizationsNotInUseException':
            print("AWS Organiations is not in use or this is not a payer account")
            return(None)
        else:
            raise


def do_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", help="print debugging info", action='store_true')
    parser.add_argument("--aws-config-file", help="Where to write the AWS config file", default="~/.aws/config")
    parser.add_argument("--steampipe-connection-file", help="Where to write the AWS config file", default="~/.steampipe/config/aws.spc")
    parser.add_argument("--rolename", help="Role Name to Assume", required=True)
    parser.add_argument("--role-session-name", help="Role Session Name to use", default="steampipe")
    parser.add_argument('--credential-source', choices=['Environment', 'Ec2InstanceMetadata', 'EcsContainer'], help='Choose the AWS credential source', default='EcsContainer')
    args = parser.parse_args()
    return(args)


if __name__ == '__main__':
    try:
        args = do_args()
        main(args)
        exit(0)
    except KeyboardInterrupt:
        exit(1)