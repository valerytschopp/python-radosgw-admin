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

import json
from boto.exception import BotoServerError

class RadosGatewayAdminError(BotoServerError):
    """Rados Gateway Admin Operation Error"""
    def __init__(self, status, reason, body=None, *args):
        BotoServerError.__init__(self, status, reason, body, *args)
        if body:
            error= json.loads(body)
            self.code= error['Code']
        else:
            self.code= 'UnknownError'

    def get_code(self):
        return self.code

    def __repr__(self):
        return '%s (%s %s)' % (self.code, self.status, self.reason)
    
    def __str__(self):
        return '%s (%s %s)' % (self.code, self.status, self.reason)

