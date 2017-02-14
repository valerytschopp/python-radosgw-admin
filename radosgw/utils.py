# Copyright (c) 2013, SWITCH - http://www.switch.ch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# @author: Valery Tschopp <valery.tshopp@switch.ch>

"""Utilities"""

import os

def get_access_key(default=None):
    """Get the S3 access key from env[AWS_ACCESS_KEY_ID], env[EC2_ACCESS_KEY] or default"""
    if 'AWS_ACCESS_KEY_ID' in os.environ:
        access_key = os.environ['AWS_ACCESS_KEY_ID']
    elif 'EC2_ACCESS_KEY' in os.environ:
        access_key = os.environ['EC2_ACCESS_KEY']
    else:
        access_key = default
    return access_key

def get_secret_key(default=None):
    """Get the S3 secret key from env[AWS_SECRET_ACCESS_KEY], env[EC2_SECRET_KEY] or default"""
    if 'AWS_SECRET_ACCESS_KEY' in os.environ:
        secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
    elif 'EC2_SECRET_KEY' in os.environ:
        secret_key = os.environ['EC2_SECRET_KEY']
    else:
        secret_key = default
    return secret_key
