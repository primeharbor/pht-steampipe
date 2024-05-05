#!/bin/bash
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

curl -s -L https://github.com/turbot/steampipe/releases/latest/download/steampipe_linux_amd64.tar.gz | tar -xzvf -

echo -n "You are running "
./steampipe --version
./steampipe plugin install aws

mkdir  -p .aws

echo "Configuring Steampipe"
aws s3 cp s3://fooli-wtf-security-deploy/sp/generate_config.py generate_config.py
chmod 755 generate_config.py
./generate_config.py --rolename $ROLENAME --credential-source Environment

# Stupid GO SDK doesn't support the AWS_CONTAINER_CREDENTIALS_FULL_URI, so this shitty hack is needed.
curl -H "Authorization: $AWS_CONTAINER_AUTHORIZATION_TOKEN" $AWS_CONTAINER_CREDENTIALS_FULL_URI 2>/dev/null > /tmp/credentials
export AWS_ACCESS_KEY_ID=`cat /tmp/credentials| jq -r .AccessKeyId`
export AWS_SECRET_ACCESS_KEY=`cat /tmp/credentials| jq -r .SecretAccessKey`
export AWS_SESSION_TOKEN=`cat /tmp/credentials| jq -r .Token`
rm /tmp/credentials

echo "Starting Steampipe"
./steampipe query
