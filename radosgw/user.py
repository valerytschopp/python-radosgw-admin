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
#  "email":"",
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
#        "perm":"*"
#      }
#   ]
# }

    def __init__(self, radosgw_admin, user_dict):
        """INTERNAL ONLY.
        :see: radosgw.connection.RadosGWAdminConnection:create_user()"""
        self._rgwadmin = radosgw_admin
        for key in user_dict:
            self.__setattr__(key.lower(), user_dict[key])

    def __str__(self):
        return "<UserInfo: %s '%s'>" % (self.user_id, self.display_name)

    def __repr__(self):
        return "<UserInfo: %s '%s'>" % (self.user_id, self.display_name)

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
        :return radosgw.user.UserInfo: the updated user
        :see: radosgw.connection.RadosGWAdminConnection#create_user
        """
        return self._rgwadmin.update_user(uid=self.user_id, **kwargs)

    def delete(self, **kwargs):
        """Delete the user.
        :param bool purge_data: purge the user data. default: True
        :returns bool:
        """
        return self._rgwadmin.delete_user(uid=self.user_id, **kwargs)

    def get_buckets(self):
        """Gets the user buckets information.
        :return list: the list of buckets information
        """
        buckets = self._rgwadmin.get_buckets(uid=self.user_id)
        return buckets
