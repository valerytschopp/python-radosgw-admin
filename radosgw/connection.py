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
"""Connections to a Ceph RADOS Gateway (radosgw) service."""
import json
import urllib
import boto.connection
import boto.s3.bucket
import boto.s3.connection

import radosgw.exception
from radosgw.user import UserInfo
from radosgw.bucket import BucketInfo


class RadosGWAdminConnection(boto.connection.AWSAuthConnection):
    """Ceph RADOS Gateway (radosgw) admin operations connection.
    :see: http://ceph.com/docs/next/radosgw/adminops/
    """
    def __init__(self,
                 host,
                 access_key, secret_key,
                 admin_path='/admin',
                 is_secure=True, port=None,
                 proxy=None, proxy_port=None, proxy_user=None, proxy_pass=None,
                 debug=0,
                 https_connection_factory=None, security_token=None,
                 validate_certs=True):
        """Constructor."""

        self.admin_path = admin_path
        boto.connection.AWSAuthConnection.__init__(self,
                                                   host=host,
                                                   aws_access_key_id=access_key,
                                                   aws_secret_access_key=secret_key,
                                                   is_secure=is_secure, port=port,
                                                   proxy=proxy, proxy_port=proxy_port,
                                                   proxy_user=proxy_user, proxy_pass=proxy_pass,
                                                   debug=debug,
                                                   https_connection_factory=https_connection_factory,
                                                   path=self.admin_path,
                                                   provider='aws',
                                                   security_token=security_token,
                                                   suppress_consec_slashes=True,
                                                   validate_certs=validate_certs)

    def __repr__(self):
        return '<%s:%s>' % (self.__class__.__name__, self.host)


    def get_admin_path(self):
        """Returns the admin query path prefix."""
        return self.admin_path

    def _required_auth_capability(self):
        """Authentication required is the same as S3 (boto.auth.HmacAuthV1Handler)"""
        return ['hmac-v1']

    def make_request(self, method, path, query_params=None, headers=None, data='', host=None,
                     sender=None, override_num_retries=None, retry_handler=None):
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
            query = urllib.urlencode(query_params)
            path = path + '?' + query
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
                return body
        else:
            boto.log.error('%s %s' % (response.status, response.reason))
            boto.log.error('%s' % body)
            raise radosgw.exception.factory(response.status, response.reason, body)

    # uid= None, start= None, end= None, show_summary= True, show_entries= True, format= 'json'
    def get_usage(self, **kwargs):
        """Gets bandwidth usage information. Doesn't work!
        :see: http://ceph.com/docs/next/radosgw/adminops/#get-usage
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

    def get_users(self, **kwargs):
        """Get all the users information."""
        params = {}
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/metadata/user', query_params=params)
        body = self._process_response(response)
        uids = json.loads(body)
        users = []
        for uid in uids:
            boto.log.debug('uid: %s' % uid)
            user = self.get_user(uid)
            users.append(user)
        return users

    def get_user(self, uid, **kwargs):
        """Get the user information.
        :param str uid: the user id
        :returns radosgw.user.UserInfo: the user info
        :throws radosgw.exception.RadosGWAdminError: if an error occurs
        :see: http://ceph.com/docs/next/radosgw/adminops/#get-user-info
        """
        # mandatory query parameters
        params = {'uid': uid}
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
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
        :param str display_name: the display name
        :param str email: the user email
        :param str key_type: the key_type 's3' or 'swift'. Default: 's3'
        :param str access_key: the access key
        :param str secret_key: the secret key
        :param bool generate_key: True to auto generate a new key pair. Default: True
        :param str user_caps: the user caps. i.e. "user=read; usage=read,write"
        :param int max_bucket: max bucket for the user. Default: 1000
        :param bool suspended: to suspend a user
        :return radosgw.user.UserInfo: the created user
        :see: http://ceph.com/docs/next/radosgw/adminops/#create-user
        """
        # mandatory query parameters
        params = {'uid': uid, 'display-name': display_name}
        # optional query parameters
        _kwargs_get('email', kwargs, params)
        _kwargs_get('key_type', kwargs, params, 's3')
        _kwargs_get('access_key', kwargs, params)
        _kwargs_get('secret_key', kwargs, params)
        _kwargs_get('user_caps', kwargs, params)
        _kwargs_get('generate_key', kwargs, params, True)
        _kwargs_get('max_bucket', kwargs, params)
        _kwargs_get('suspended', kwargs, params)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('PUT', path='/user', query_params=params)
        body = self._process_response(response)
        user_dict = json.loads(body)
        user = UserInfo(self, user_dict)
        return user

    # uid= UID
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
        :param int max_bucket: max bucket for the user. Default: 1000
        :param bool suspended: to suspend a user
        :return radosgw.user.UserInfo: the updated user
        :see: http://ceph.com/docs/next/radosgw/adminops/#modify-user
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
        _kwargs_get('max_bucket', kwargs, params)
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
        :see: http://ceph.com/docs/next/radosgw/adminops/#remove-user
        """
        params = {'uid': uid, 'purge-data': purge_data}
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('DELETE', path='/user', query_params=params)
        return self._process_response(response) is None

    def get_bucket(self, bucket, **kwargs):
        """Get a bucket information.
        :param str bucket: the bucket name
        :returns BucketInfo:
        :see: http://ceph.com/docs/next/radosgw/adminops/#get-bucket-info
        """
        params = {'bucket': bucket}
        _kwargs_get('bucket', kwargs, params)
        _kwargs_get('stats', kwargs, params, True)
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/bucket', query_params=params)
        body = self._process_response(response)
        bucket_dict = json.loads(body)
        #print json.dumps(bucket_dict, indent=4, sort_keys=True)
        bucket = BucketInfo(self, bucket_dict)
        return bucket

    def get_buckets(self, uid=None, **kwargs):
        """Get all, or user specific, buckets information.
        :param str uid: the user id
        :returns list: the list of buckets information
        :see: http://ceph.com/docs/next/radosgw/adminops/#get-bucket-info
        """
        params = {}
        if uid:
            params = {'uid': uid}
        # optional query parameters
        _kwargs_get('format', kwargs, params, 'json')
        response = self.make_request('GET', path='/bucket', query_params=params)
        body = self._process_response(response)
        bucket_names = json.loads(body)
        buckets = []
        for bucket_name in bucket_names:
            boto.log.debug('bucket_name: %s' % bucket_name)
            bucket = self.get_bucket(bucket=bucket_name)
            buckets.append(bucket)
        return buckets

# utilities
def _kwargs_get(key, kwargs, params, default=None):
    nkey = key.replace('_', '-')
    if kwargs.has_key(key):
        params[nkey] = kwargs[key]
    elif default != None:
        params[nkey] = default
