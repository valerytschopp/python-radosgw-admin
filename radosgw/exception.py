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

"""Ceph RADOS Gateway exceptions."""

import json
import boto.exception
import boto.utils

class RadosGWAdminError(boto.exception.BotoServerError):
    """Ceph RADOS Gateway admin operation generic error."""
    def __init__(self, status, reason, body=None, *args):
        boto.exception.BotoServerError.__init__(self,
                                                status,
                                                reason,
                                                body,
                                                *args)
        if body:
            error = json.loads(body)
            self.code = error['Code']
        else:
            self.code = self.__class__.__name__

    def get_code(self):
        """Returns the error code."""
        return self.code

    def __repr__(self):
        return '%s (%s %s)' % (self.code, self.status, self.reason)

    def __str__(self):
        return '%s (%s %s)' % (self.code, self.status, self.reason)

def factory(status, reason, body=None, *args):
    """Returns the correct error, based on the error code in the body."""
    if body:
        error = json.loads(body)
        code = error['Code']
        exception_class = boto.utils.find_class(__name__, code)
        if exception_class:
            exception = exception_class(status, reason, body, args)
        else:
            exception = RadosGWAdminError(status, reason, body, args)
    else:
        exception = RadosGWAdminError(status, reason, body, args)

    return exception

class AccessDenied(RadosGWAdminError):
    """Access was denied for the request."""


class UserExists(RadosGWAdminError):
    """Attempt to create existing user."""


class InvalidAccessKey(RadosGWAdminError):
    """Invalid access key specified."""


class InvalidKeyType(RadosGWAdminError):
    """Invalid key type specified."""


class InvalidSecretKey(RadosGWAdminError):
    """Invalid secret key specified."""


class KeyExists(RadosGWAdminError):
    """Provided access key exists and belongs to another user."""


class EmailExists(RadosGWAdminError):
    """Provided email address exists."""


class SubuserExists(RadosGWAdminError):
    """Specified subuser exists."""


class InvalidAccess(RadosGWAdminError):
    """Invalid subuser access specified."""


class IndexRepairFailed(RadosGWAdminError):
    """Bucket index repair failed."""


class BucketNotEmpty(RadosGWAdminError):
    """Attempted to delete non-empty bucket."""


class ObjectRemovalFailed(RadosGWAdminError):
    """Unable to remove objects."""


class BucketUnlinkFailed(RadosGWAdminError):
    """Unable to unlink bucket from specified user."""


class BucketLinkFailed(RadosGWAdminError):
    """Unable to link bucket to specified user."""


class NoSuchObject(RadosGWAdminError):
    """Specified object does not exist."""


class IncompleteBody(RadosGWAdminError):
    """Either bucket was not specified for a bucket policy request or bucket
    and object were not specified for an object policy request."""


class InvalidCap(RadosGWAdminError):
    """Attempt to grant invalid admin capability."""


class NoSuchCap(RadosGWAdminError):
    """User does not possess specified capability."""


class InternalError(RadosGWAdminError):
    """Internal server error."""


class NoSuchUser(RadosGWAdminError):
    """User does not exist."""


class NoSuchBucket(RadosGWAdminError):
    """Bucket does not exist."""


class NoSuchKey(RadosGWAdminError):
    """No such access key."""
