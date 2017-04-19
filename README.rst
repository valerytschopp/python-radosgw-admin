python-radosgw-admin
====================

Python REST API for the Ceph RADOS Gateway (radosgw) admin operations

http://docs.ceph.com/docs/master/radosgw/adminops/

Requirement
-----------

- boto

Installation
------------

.. image:: https://img.shields.io/pypi/v/radosgw-admin.svg
   :target: https://pypi.python.org/pypi/radosgw-admin

The package is available on https://pypi.python.org/pypi/radosgw-admin. To install it use ``pip``::

  pip install radosgw-admin

Or clone this `repository <https://github.com/valerytschopp/python-radosgw-admin>`_ and install it locally::

  python setup.py install


Configuration of the admin user
-------------------------------

To create or modify a bucket/user in radosgw, the admin user require the following ``read,write`` capabilities (caps)::

  "caps": [
     { "type": "buckets",
       "perm": "*" },
     { "type": "usage",
       "perm": "read" },
     { "type": "metadata",
       "perm": "read" },
     { "type": "users",
       "perm": "*" }
  ]

You can use the ``radosgw-admin`` command to add capabilities to an existing user::

  radosgw-admin caps add --uid <USER_ID> --caps "buckets=read,write"
  radosgw-admin caps add --uid <USER_ID> --caps "users=read,write"


Examples
--------

See the example in `examples/radosgw-admin-example.py <https://github.com/valerytschopp/python-radosgw-admin/blob/master/examples/radosgw-admin-example.py>`_


Here is a simple example:

.. code-block:: python

  import radosgw

  rgwadmin = radosgw.connection.RadosGWAdminConnection(host='hostname.example.org',
                                                       access_key='<ADMIN_ACCESS_KEY>',
                                                       secret_key='<ADMIN_SECRET_KEY>')
  # user operations
  testuser2 = rgwadmin.create_user('testuser2',
                                   display_name='A test user',
                                   email='testuser2@example.org')

  testuser2.update(display_name='Second test user', suspended=True)

  testuser1 = rgwadmin.get_user('testuser1')

  # bucket operations
  buckets = rgwadmin.get_buckets()
  for bucket in buckets:
      print bucket

  testuser1_buckets = testuser1.get_buckets()
  for bucket in testuser1_buckets:
      # transfer buckets to testuser2
      rgwadmin.link_bucket(bucket.name, bucket.id, testuser2.id)

