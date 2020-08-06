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
# }


class BucketInfo(object):
    """Ceph RADOS Gateway Bucket Info"""

    def __init__(self, radosgw_admin, bucket_dict):
        """INTERNAL ONLY."""
        self._rgwadmin = radosgw_admin
        self._object = bucket_dict
        for key in bucket_dict:
            setattr(self, key.lower(), bucket_dict[key])

    @property
    def name(self):
        return self.bucket

    @property
    def usage(self):
        return self._usage

    @usage.setter
    def usage(self, value):
        if 'rgw.main' in value:
            self._usage = Usage(value['rgw.main'])
        else:
            self._usage = None

    @property
    def object(self):
        return self._object

    def check_index(self, check_objects=True, fix=False, **kwargs):
        """Check the index of the bucket.
        :param bool check_objects:
        :param bool fix:
        :return: nothing
        """
        self._rgwadmin.check_bucket_index(self.name, check_objects, fix, **kwargs)

    def link(self, uid, **kwargs):
        """Link the bucket to the specified user, unlinking the bucket from any previous user.
        :param str uid: user ID to link the bucket to
        :param kwargs: optional params
        :return: None
        """
        self._rgwadmin.link_bucket(self.name, self.id, uid, **kwargs)

    def unlink(self, **kwargs):
        """Unlink the bucket from the current owner.
        Primarily useful for changing bucket ownership.
        :param kwargs: optional params
        :return: None
        """
        self._rgwadmin.unlink_bucket(self.name, self.owner, **kwargs)

    def delete(self, purge_objects=True, **kwargs):
        """Delete the bucket.
        :param bool purge_objects:
        :param kwargs: optional params
        :return: None
        """
        self._rgwadmin.delete_bucket(self.name, purge_objects, **kwargs)

    def remove_object(self, object_name, **kwargs):
        """Remove an existing object from the bucket.
        :param str object_name: the object name
        :param kwargs: optional params
        :return: None
        """
        self._rgwadmin.remove_object(self.name, object_name, **kwargs)

    def policy(self, object_name=None, **kwargs):
        """get Bucket or Object Policy.
        :param str object_name: the object name:
        :param kwargs: optional params
        :return: bucket or object policy
        """
        self._rgwadmin.get_policy(self.name, object_name, **kwargs)

    def __str__(self):
        return "<Bucket: %s>" % self.name

    def __repr__(self):
        return "<Bucket: %s>" % self.name


class Usage(object):
    """RADOS Gateway bucket usage"""

    def __init__(self, usage_dict):
        self._object = usage_dict
        for key in usage_dict:
            setattr(self, key.lower(), usage_dict[key])

    def __repr__(self):
        return "<Usage: num_objects={} size_kb={} size_kb_actual={}>".format(self.num_objects,
                                                                             self.size_kb,
                                                                             self.size_kb_actual)

    @property
    def object(self):
        return self._object
