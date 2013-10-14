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

"""CEPH RADOS Gateway User Information."""

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
#      "access_key":"76A1O263ZTMJ6ECG0TLS",
#      "secret_key":"cYWPiYJPS4feM2vdQY5iJJ1beZpuPEjN6+xGcY7t"
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

    def __init__(self,radosgw_connection,user_dict):
        self._connection= radosgw_connection
        for key in user_dict:
            self.__setattr__(key.lower(), user_dict[key])
        
    def __str__(self):
        return "<UserInfo: %s '%s'>" % (self.user_id,self.display_name)