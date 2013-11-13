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

"""Ceph RADOS Gateway Bucket Information."""

class BucketInfo(object):
    """Ceph RADOS Gateway Bucket Info"""

# {
#    "bucket": "example_bucket",
#    "id": "79826.5",
#    "index_pool": ".rgw.buckets",
#    "marker": "79826.5",
#    "master_ver": 0,
#    "max_marker": "",
#    "mtime": 0,
#    "owner": "example_user",
#    "pool": ".rgw.buckets",
#    "usage": {
#        "rgw.main": {
#            "num_objects": 1,
#            "size_kb": 147,
#            "size_kb_actual": 148
#        }
#    },
#    "ver": 0
#}

    def __init__(self, radosgw_admin, bucket_dict):
        """INTERNAL ONLY."""
        self._rgwadmin = radosgw_admin
        for key in bucket_dict:
            self.__setattr__(key.lower(), bucket_dict[key])

    def __str__(self):
        return "<BucketInfo: %s>" % self.bucket

    def __repr__(self):
        return "<BucketInfo: %s>" % self.bucket
