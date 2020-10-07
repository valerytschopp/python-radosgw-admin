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
# author: Valery Tschopp <valery.tschopp@switch.ch>

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
    parser.add_argument('-p', '--port', help='radosgw port', default=443)
    parser.add_argument('-a', '--access-key', help='S3 access key', required=True)
    parser.add_argument('-s', '--secret-key', help='S3 secret key', required=True)
    parser.add_argument('--insecure', help='disable ssl validation', action='store_true')
    parser.add_argument('-v', '--verbose', help='verbose', action='store_true')
    parser.add_argument('-d', '--debug', help='debug', action='store_true')
    parser.add_argument('--signature', help='AWS signature version to use: AWS4 or AWS2', default='AWS4')
    args = parser.parse_args()

    rgwadmin = radosgw.connection.RadosGWAdminConnection(host=args.hostname,
                                                         port=args.port,
                                                         access_key=args.access_key,
                                                         secret_key=args.secret_key,
                                                         is_secure=not args.insecure,
                                                         debug=args.debug,
                                                         aws_signature=args.signature)

    print("{:*^20}".format('Buckets'))
    buckets = rgwadmin.get_buckets()
    i = 1
    total_size_kb = 0
    total_num_object = 0
    for bucket in buckets:
        print("{:>3} bucket: {}".format(i, bucket))
        if bucket.usage:
            print("     usage: {}".format(bucket.usage))
            total_size_kb += bucket.usage.size_kb
            total_num_object += bucket.usage.num_objects
        i += 1
    print("Total: {} objects, {} KB".format(total_num_object, total_size_kb))

    print("{:*^20}".format('Users'))
    # WARNING: get_users is very slow !!!
    #          one callout per user
    users = rgwadmin.get_users()
    for user in users:
        print("user: {}".format(user))
        for key in user.keys:
            print(" key: {}".format(key))
        for cap in user.caps:
            print(" cap: {}".format(cap))

    print("{:*^20}".format('User IDs'))
    uids = rgwadmin.get_uids()
    for uid in uids:
        print("uid: {}".format(uid))
