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

"""Ceph RADOS Gateway User Information."""

class UserInfo(object):
    """RADOS Gateway User Info"""

# {
#  "user_id":"test",
#  "display_name":"Test User",
#  "email":"test@example.org",
#  "suspended":0,
#  "max_buckets":1000,
#  "subusers":[],
#  "keys":[
#     {
#      "user":"test",
#      "access_key":"7***S",
#      "secret_key":"c***t"
#      }
#   ],
#   "swift_keys":[],
#   "caps":[
#      {
#        "type":"usage",
#        "perm":"read"
#      },
#      {
#        "type":"users",
#        "perm":"read"
#      }
#   ]
# }

    def __init__(self, radosgw_admin, user_dict):
        """INTERNAL ONLY.
        :see: radosgw.connection.RadosGWAdminConnection#get_user
        :see: radosgw.connection.RadosGWAdminConnection#create_user
        """
        self._rgwadmin = radosgw_admin
        self._object = user_dict
        self._update_from_user(user_dict)

    def _update_from_user(self, user):
        if type(user) is dict:
            user_dict = user
        else:
            user_dict = user.__dict__
        self.user_id = user_dict['user_id']
        self.display_name = user_dict['display_name']
        self.email = user_dict['email']
        self.suspended = user_dict['suspended']
        self.max_buckets = user_dict['max_buckets']
        # subusers
        self.subusers = []
        subusers = user_dict['subusers']
        for subuser in subusers:
            # TODO
            pass
        # keys (s3)
        self.keys = []
        keys = user_dict['keys']
        for key in keys:
            if type(key) is dict:
                key_dict = key
            else:
                key_dict = key.__dict__
            s3key = Key(key_dict['user'],
                        key_dict['access_key'], key_dict['secret_key'],
                        's3')
            self.keys.append(s3key)
        # swift_keys
        self.swift_keys = []
        keys = user_dict['swift_keys']
        for key in keys:
            if type(key) is dict:
                key_dict = key
            else:
                key_dict = key.__dict__
            swiftkey = Key(key_dict['user'],
                           key_dict['access_key'], key_dict['secret_key'],
                           'swift')
            self.swift_keys.append(swiftkey)
        # caps
        self.caps = []
        caps = user_dict['caps']
        for cap in caps:
            if type(cap) is dict:
                cap_dict = cap
            else:
                cap_dict = cap.__dict__
            ucap = Cap(cap_dict['type'], cap_dict['perm'])
            self.caps.append(ucap)

    @property
    def id(self):
        return self.user_id


    def __repr__(self):
        return "<User: %s '%s'>" % (self.user_id, self.display_name)

    # display_name= None
    # email= None
    # key_type= 's3|swift',
    # access_key= None
    # secret_key= None
    # user_caps= None
    # generate_key= False
    # max_buckets= None
    # suspended= False
    def update(self, **kwargs):
        """Update the user.
        :param str display_name: the display name
        :param str email: the user email
        :param str key_type: the key_type 's3' or 'swift'. Default: 's3'
        :param str access_key: the access key
        :param str secret_key: the secret key
        :param bool generate_key: True to auto generate a new key pair. Default: False
        :param str user_caps: the user caps. i.e. 'user=read'
        :param int max_bucket: max bucket for the user
        :param bool suspended: to suspend a user
        :returns radosgw.user.UserInfo: the updated user
        :see: radosgw.connection.RadosGWAdminConnection#create_user
        """
        user = self._rgwadmin.update_user(uid=self.user_id, **kwargs)
        self._update_from_user(user)
        return self

    def delete(self, **kwargs):
        """Delete the user.
        :param bool purge_data: purge the user data. default: True
        :returns bool:
        """
        return self._rgwadmin.delete_user(uid=self.user_id, **kwargs)

    def get_buckets(self):
        """Gets the user buckets information.
        :returns list: the list of user's buckets information
        """
        buckets = self._rgwadmin.get_buckets(uid=self.user_id)
        return buckets


class Key(object):
    """RADOS Gateway User key"""
    def __init__(self, user_id, access_key, secret_key, key_type='s3'):
        self.user = user_id
        self.access_key = access_key
        self.secret_key = secret_key
        self.key_type = key_type

    def __repr__(self):
        return '<Key %s: %s: %s %s>' % (self.key_type, self.user, self.access_key, self.secret_key)


class Cap(object):
    """RADOS Gateway User capability"""
    def __init__(self, cap_type, cap_perm):
        self.type = cap_type
        self.perm = cap_perm

    def __repr__(self):
        return '<Capability: %s=%s>' % (self.type, self.perm)
