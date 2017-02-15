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

import argparse

import radosgw

##
# S3 RADOS GW (admin: cap: users=*)
##
# tschopp@os:~$ radosgw-admin user info --uid admin
# {
#     "user_id": "admin",
#     "display_name": "radosgw admin",
#     "email": "valery.tschopp@switch.ch",
#     "suspended": 0,
#     "max_buckets": 1000,
#     "auid": 0,
#     "subusers": [],
#     "keys": [
#         {
#             "user": "admin",
#             "access_key": "QQ...EF",
#             "secret_key": "hP...MF"
#         }
#     ],
#     "swift_keys": [],
#     "caps": [
#         {
#             "type": "buckets",
#             "perm": "*"
#         },
#         {
#             "type": "metadata",
#             "perm": "read"
#         },
#         {
#             "type": "usage",
#             "perm": "*"
#         },
#         {
#             "type": "users",
#             "perm": "*"
#         }
#     ],
#     "op_mask": "read, write, delete",
#     "default_placement": "",
#     "placement_tags": [],
#     "bucket_quota": {
#         "enabled": false,
#         "max_size_kb": -1,
#         "max_objects": -1
#     },
#     "user_quota": {
#         "enabled": false,
#         "max_size_kb": -1,
#         "max_objects": -1
#     },
#     "temp_url_keys": []
# }

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-H', '--hostname', help='radosgw hostname', required=True)
    parser.add_argument('-a', '--access-key', help='S3 access key', required=True)
    parser.add_argument('-s', '--secret-key', help='S3 secret key', required=True)
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    parser.add_argument('-d', '--debug', help='debug', action='store_true')
    args = parser.parse_args()

    rgwadmin = radosgw.connection.RadosGWAdminConnection(host = args.hostname,
                                                         access_key = args.access_key,
                                                         secret_key = args.secret_key)

    print "{:*^20}".format('Buckets')
    buckets = rgwadmin.get_buckets()
    print "{:>3} buckets".format(len(buckets))
    i = 1
    total_size_kb = 0
    total_num_object = 0
    for bucket in buckets:
        print "{:>3} bucket: {}".format(i, bucket)
        owner = rgwadmin.get_user(uid=bucket.owner)
        print "    owner: {}".format(owner)
        print "    usage: {}".format(bucket.usage)
        if bucket.usage:
            total_size_kb += bucket.usage.size_kb
            total_num_object += bucket.usage.num_objects
        i += 1
    print "Total: {} objects, {} KB".format(total_num_object, total_size_kb)

    print "{:*^20}".format('Users')
    users = rgwadmin.get_users()
    for user in users:
        print "user:", user
        for key in user.keys:
            print " key:", key
        for cap in user.caps:
            print " cap:", cap
