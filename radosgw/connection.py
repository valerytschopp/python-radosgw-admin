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
import json
import boto
import boto.connection
import boto.s3.bucket
import boto.s3.connection

import radosgw.exception
from radosgw.user import UserInfo
from radosgw.bucket import BucketInfo

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


class RadosGWAdminConnection(boto.connection.AWSAuthConnection):
    """Ceph RADOS Gateway (radosgw) admin connection.
    :see: http://docs.ceph.com/docs/master/radosgw/adminops/
    """
    def __init__(self,
                 host,
                 access_key, secret_key,
                 admin_path='/admin',
                 aws_signature='AWS4',
                 timeout=30,
                 is_secure=True, port=None,
                 proxy=None, proxy_port=None, proxy_user=None, proxy_pass=None,
                 debug=False,
                 https_connection_factory=None, security_token=None,
                 validate_certs=True):
        """Constructor."""

        self._admin_path = admin_path
        if debug:
            boto.set_stream_logger('boto')
            debug_boto = 10
        else:
            debug_boto = 0

        # AWS4 and AWS2 signature support
        # see boto.auth.S3HmacAuthV4Handler
        # see boto.auth.HmacAuthV1Handler
        if aws_signature == 'AWS4':
            # AWS4 signature
            self._signature_algo = ['hmac-v4-s3']
        else:
            # old style AWS2 signature algo
            self._signature_algo = ['hmac-v1']

        # init AWS connection
        boto.connection.AWSAuthConnection.__init__(self,
                                                   host=host,
                                                   aws_access_key_id=access_key,
                                                   aws_secret_access_key=secret_key,
                                                   is_secure=is_secure, port=port,
                                                   proxy=proxy, proxy_port=proxy_port,
                                                   proxy_user=proxy_user, proxy_pass=proxy_pass,
                                                   debug=debug_boto,
                                                   https_connection_factory=https_connection_factory,
                                                   path=self._admin_path,
                                                   provider='aws',
                                                   security_token=security_token,
                                                   suppress_consec_slashes=True,
                                                   validate_certs=validate_certs)
        # set http_socket_timeout
        self.http_connection_kwargs['timeout'] = timeout
        if aws_signature == 'AWS4':
            self._set_auth_region_name('s3')


    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.host)

    def get_admin_path(self):
        """Returns the admin query path prefix."""
        return self._admin_path

    def _required_auth_capability(self):
        """Authentication algo required for S3"""
        return self._signature_algo

    def make_request(self, method, path, query_params=None, headers=None, data='', host=None,
                     sender=None, override_num_retries=3, retry_handler=None):
        """Makes a request to the RADOS GW admin server.
        :param str method: GET|PUT|HEAD|POST|DELETE|...
        :param str path: admin sub request path (i.e. /user)
        :param dict query_params: url query parameters
        :returns boto.connection.HttpResponse: the HTTP response
        """
        auth_path = path
        if not query_params:
            query_params = {}
        else:
            query = urlencode(query_params)
            # handle path like /admin/bucket?index&<params>
            path = "{}{}{}".format(path,
                                   '&' if '?' in path else '?',
                                   query)
        http_request = self.build_base_http_request(method, path, auth_path,
                                                    query_params, headers, data, host)
        boto.log.debug('http_request:%s' % http_request)
        return self._mexe(http_request, sender, override_num_retries,
                          retry_handler=retry_handler)

    def _process_response(self, response):
        """Processes the response and returns the body or throws an error."""
        body = response.read()
        boto.log.debug('status: %d body: %s' % (response.status, body))
        if response.status == 200:
            if not body:
                return None
            else:
                if isinstance(body, bytes) and hasattr(body, 'decode'):
                    body = body.decode('utf-8')
                return body
        else:
            boto.log.error('%s %s' % (response.status, response.reason))
            boto.log.error('%s' % body)
            raise radosgw.exception.factory(response.status, response.reason, body)

    # uid= None, start= None, end= None, show_summary= True, show_entries= True, format= 'json'
    def get_usage(self, **kwargs):
        """Gets bandwidth usage information. Doesn't work!
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#get-usage
        """
        params = {}
        _kwargs_get('uid', kwargs, params)
        _kwargs_get('start', kwargs, params)
        _kwargs_get('end', kwargs, params)
        _kwargs_get('show_summary', kwargs, params, True)
        _kwargs_get('show_entries', kwargs, params, True)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/usage', query_params=params)
        body = self._process_response(response)
        usage = json.loads(body)
        return usage

    def delete_usage(self, **kwargs):
        """Trim usage
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#trim-usage
        """
        params = {}
        _kwargs_get('uid', kwargs, params)
        _kwargs_get('start', kwargs, params)
        _kwargs_get('end', kwargs, params)
        _kwargs_get('remove-all', kwargs, params)
        response = self.make_request('DELETE', path='/usage', query_params=params)
        body = self._process_response(response)
        return body
    
    def get_uids(self, **kwargs):
        """Get all the users uid.
        :return list uids: the list of uid
        """
        params = {}
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/metadata/user', query_params=params)
        body = self._process_response(response)
        uids = json.loads(body)
        return uids

    def get_users(self, **kwargs):
        """Get all the users information.
        :returns iterator: iterator of users information
        """
        params = {}
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/metadata/user', query_params=params)
        body = self._process_response(response)
        uids = json.loads(body)
        for uid in uids:
            boto.log.debug('uid: %s' % uid)
            if 'stats' in kwargs and kwargs['stats']:
                try:  # Valid user without stats return 404 error
                    user = self.get_user(uid, stats=True)
                except radosgw.exception.NoSuchKey:
                    user = self.get_user(uid, stats=False)
            else:
                user = self.get_user(uid)
            yield user

    def get_user(self, uid, **kwargs):
        """Get the user information.
        :param str uid: the user id
        :returns radosgw.user.UserInfo: the user info
        :throws radosgw.exception.RadosGWAdminError: if an error occurs
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#get-user-info
        """
        # mandatory query parameters
        if 'tenant' in kwargs:
            uid = kwargs['tenant'] + '$' + uid
        params = {'uid': uid}
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        _kwargs_get('stats', kwargs, params, False)
        response = self.make_request('GET', path='/user', query_params=params)
        body = self._process_response(response)
        user_dict = json.loads(body)
        user = UserInfo(self, user_dict)
        return user

    # uid= UID
    # display_name= DISPLAY_NAME
    # email= None, key_type= 's3|swift',
    # access_key= None, secret_key= None, user_caps= None, generate_key= True,
    # max_buckets= None, suspended= False, format= 'json'
    def create_user(self, uid, display_name, **kwargs):
        """Creates a new user.
        :param str uid: the user id
        :param str tenant: the user tenant
        :param str display_name: the display name
        :param str email: the user email
        :param str key_type: the key_type 's3' or 'swift'. Default: 's3'
        :param str access_key: the access key
        :param str secret_key: the secret key
        :param bool generate_key: True to auto generate a new key pair. Default: True
        :param str user_caps: the user caps. i.e. "user=read; usage=read,write"
        :param int max_buckets: max bucket for the user. Default: 1000
        :param bool suspended: to suspend a user
        :return radosgw.user.UserInfo: the created user
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#create-user
        """
        # mandatory query parameters
        if 'tenant' in kwargs:
            uid = kwargs['tenant'] + "$" + uid
        params = {'uid': uid, 'display-name': display_name}
        # optional query parameters
        _kwargs_get('email', kwargs, params)
        _kwargs_get('key_type', kwargs, params, 's3')
        _kwargs_get('access_key', kwargs, params)
        _kwargs_get('secret_key', kwargs, params)
        _kwargs_get('user_caps', kwargs, params)
        _kwargs_get('generate_key', kwargs, params, True)
        _kwargs_get('max_buckets', kwargs, params)
        _kwargs_get('suspended', kwargs, params)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('PUT', path='/user', query_params=params)
        body = self._process_response(response)
        user_dict = json.loads(body)
        user = UserInfo(self, user_dict)
        return user

    # uid= UID or TENANT$UID
    # display_name= DISPLAY_NAME
    # email= None, key_type= 's3|swift',
    # access_key= None, secret_key= None, user_caps= None, generate_key= False,
    # max_buckets= None, suspended= False, format= 'json'
    def update_user(self, uid, **kwargs):
        """Update an existing user.
        :param str uid: the user id
        :param str display_name: the display name
        :param str email: the user email
        :param str key_type: the key_type 's3' or 'swift'. Default: 's3'
        :param str access_key: the access key
        :param str secret_key: the secret key
        :param bool generate_key: True to auto generate a new key pair. Default: True
        :param str user_caps: the user caps. i.e. "user=read; usage=read,write"
        :param int max_buckets: max bucket for the user. Default: 1000
        :param bool suspended: to suspend a user
        :return radosgw.user.UserInfo: the updated user
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#modify-user
        """
        params = {'uid': uid}
        # optional query parameters
        _kwargs_get('display_name', kwargs, params)
        _kwargs_get('email', kwargs, params)
        _kwargs_get('key_type', kwargs, params)
        _kwargs_get('access_key', kwargs, params)
        _kwargs_get('secret_key', kwargs, params)
        _kwargs_get('user_caps', kwargs, params)
        _kwargs_get('generate_key', kwargs, params, False)
        _kwargs_get('max_buckets', kwargs, params)
        _kwargs_get('suspended', kwargs, params)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('POST', path='/user', query_params=params)
        body = self._process_response(response)
        user_dict = json.loads(body)
        user = UserInfo(self, user_dict)
        return user

    def delete_user(self, uid, purge_data=True, **kwargs):
        """Delete a user identified by uid.
        :param str uid: the user_id
        :param bool purge_data: purge the user data. default: True
        :returns bool:
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#remove-user
        """
        params = {'uid': uid, 'purge-data': purge_data}
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('DELETE', path='/user', query_params=params)
        return self._process_response(response) is None

    def create_key(self, uid, **kwargs):
        """Creates a key for the user specified
        :param str uid: the user id
        :param str key_type: the key_type 's3' or 'swift'. Default: 's3'
        :param str access_key: the access key
        :param str secret_key: the secret key
        :param bool generate_key: True to auto generate a new key pair. Default: True
        :return bool:
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#create-key
        """
        params = {'uid': uid}
        # optional query parameters
        _kwargs_get('key_type', kwargs, params)
        _kwargs_get('access_key', kwargs, params)
        _kwargs_get('secret_key', kwargs, params)
        _kwargs_get('generate_key', kwargs, params, False)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('PUT', path='/user?key', query_params=params)
        body = self._process_response(response)
        return json.loads(body)

    def remove_key(self, access_key, **kwargs):
        """Delete an existing access key
        :param str access_key: the access key
        :param str uid: the user id
        :param str key_type: the key_type 's3' or 'swift'. Default: 's3'
        :returns bool:
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#remove-key
        """
        params = {'access-key': access_key}
        # optional query parameters
        _kwargs_get('uid', kwargs, params)
        _kwargs_get('key_type', kwargs, params)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('DELETE', path='/user?key', query_params=params)
        return self._process_response(response) is None

    def get_bucket(self, bucket_name, **kwargs):
        """Get a bucket information.
        :param str bucket_name: the bucket name
        :returns BucketInfo:
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#get-bucket-info
        """
        params = {'bucket': bucket_name}
        _kwargs_get('stats', kwargs, params, True)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/bucket', query_params=params)
        body = self._process_response(response)
        bucket_dict = json.loads(body)
        # XXX: print(json.dumps(bucket_dict, indent=4, sort_keys=True))
        bucket = BucketInfo(self, bucket_dict)
        return bucket

    def get_buckets(self, uid=None, **kwargs):
        """Get all, or user specific, buckets information.
        :param str uid: the user id
        :returns iterator: iterator of buckets information
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#get-bucket-info
        """
        params = {'stats': True}
        if uid:
            params['uid'] = uid
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/bucket', query_params=params)
        body = self._process_response(response)
        body_json = json.loads(body)
        boto.log.debug('%d buckets' % len(body_json))
        for bucket_dict in body_json:
            bucket = BucketInfo(self, bucket_dict)
            yield bucket


    def check_bucket_index(self, bucket_name, check_objects=True, fix=False, **kwargs):
        """Check the index of an existing bucket.
        :param str bucket_name:
        :param bool check_objects:
        :param bool fix:
        :return: nothing
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#check-bucket-index
        """
        params = {'bucket': bucket_name,
                  'check-objects': check_objects,
                  'fix': fix }
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/bucket?index', query_params=params)
        body = self._process_response(response)
        # print "XXX: body:", body

    def delete_bucket(self, bucket_name, purge_objects=True, **kwargs):
        """Delete an existing bucket.
        :param str bucket_name:
        :param bool purge_objects:
        :return: None
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#remove-bucket
        """
        params = {'bucket': bucket_name,
                  'purge-objects': purge_objects }
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('DELETE', path='/bucket', query_params=params)
        return self._process_response(response) is None

    def unlink_bucket(self, bucket_name, uid, **kwargs):
        """Unlink a bucket from a specified user.
        Primarily useful for changing bucket ownership.
        :param str bucket_name: name of the bucket to unlink
        :param str uid: current user id of the bucket
        :param kwargs:
        :return: None
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#unlink-bucket
        """
        params = {'bucket': bucket_name, 'uid': uid}
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('POST', path='/bucket', query_params=params)
        return self._process_response(response) is None

    def link_bucket(self, bucket_name, bucket_id, uid, **kwargs):
        """Link a bucket to a specified user, unlinking the bucket from any previous user.
        :param str bucket_name: name of the bucket to link
        :param str bucket_id: id of the bucket to link
        :param str uid: user ID to link the bucket to
        :param kwargs:
        :return: None
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#link-bucket
        """
        params = {'bucket': bucket_name, 'bucket-id': bucket_id, 'uid': uid}
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('PUT', path='/bucket', query_params=params)
        body = self._process_response(response)
        return self._process_response(response) is None

    def remove_object(self, bucket_name, object_name, **kwargs):
        """Remove an existing object from a bucket.
        :param str bucket_name:
        :param str object_name:
        :param kwargs:
        :return: None
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#remove-object
        """
        params = {'bucket': bucket_name,
                  'object': object_name }
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('DELETE', path='/bucket?object', query_params=params)
        return self._process_response(response) is None

    def get_policy(self, bucket_name, object_name=None, **kwargs):
        """Read the policy of an object or bucket.
        :param str bucket_name:
        :param str object_name:
        :param kwargs:
        :return: bucket or object policy
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#get-bucket-or-object-policy
        """
        params = {'bucket': bucket_name}
        if object_name:
            params['object'] = object_name
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/bucket?policy', query_params=params)
        return self._process_response(response)

    def get_quota(self, uid, quota_type, **kwargs):
        """Gets the quota of an specific quota_type (user or bucket).
        :param str uid: current user id for the quota operation
        :param str quota_type: type of the quota (user or bucket)
        :param kwargs:
        :return: None
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#quotas
        """
        params = {'uid': uid, 'quota-type': quota_type }
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/user?quota', query_params=params)
        return self._process_response(response)

    def set_quota(self, uid, quota_type, **kwargs):
        """Gets the quota of an specific quota_type (user or bucket).
        :param str uid: current user id for the quota operation
        :param str quota_type: type of the quota (user or bucket)
        :param int max_objects: maximum number of objects
        :param str max_size_kb: quota size in kb
        :param bool enabled: The enabled option specifies whether the quota should be enabled
        :param kwargs:
        :return: None
        :see: http://docs.ceph.com/docs/master/radosgw/adminops/#quotas
        """
        params = {'uid': uid, 'quota-type': quota_type }
        # optional query parameters
        _kwargs_get('max_objects', kwargs, params)
        _kwargs_get('max_size_kb', kwargs, params)
        _kwargs_get('enabled', kwargs, params)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('PUT', path='/user?quota', query_params=params)
        return self._process_response(response)


# utilities
def _kwargs_get(key, kwargs, params, default=None):
    nkey = key.replace('_', '-')
    if key in kwargs and kwargs[key]:
        params[nkey] = kwargs[key]
    elif default is not None:
        params[nkey] = default
