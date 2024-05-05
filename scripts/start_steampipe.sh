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

echo -n "You are running "
steampipe --version

echo "Configuring Steampipe"
./bin/generate_config.py --rolename $ROLENAME
steampipe plugin update --all

cat <<EOF > /home/steampipe/.steampipe/config/default.spc
#
# For detailed descriptions, see the reference documentation
# at https://steampipe.io/docs/reference/cli-args
#

options "database" {
  port               = 9193                  # any valid, open port number
  listen             = "network"               # local (alias for localhost), network (alias for *), or a comma separated list of hosts and/or IP addresses , or any valid combination of hosts and/or IP addresses
#   search_path        = "aws,aws2,gcp,gcp2"   # comma-separated string; an exact search_path
#   search_path_prefix = "aws"                 # comma-separated string; a search_path prefix
  start_timeout      = 30                    # maximum time (in seconds) to wait for the database to start up
  cache              = true                  # true, false
  cache_max_ttl      = 900                   # max expiration (TTL) in seconds
  cache_max_size_mb  = 4096                  # max total size of cache across all plugins
}
EOF

echo "Starting Steampipe"
steampipe query