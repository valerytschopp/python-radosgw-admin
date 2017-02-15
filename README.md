# python-radosgw-admin

Python REST API for the Ceph RADOS Gateway (radosgw) admin operations

http://ceph.com/docs/master/radosgw/adminops/

## Requirement

- boto

## Installation

    python setup.py install

## Configuration of the admin user

Create or modify a user in radosgw with the following capabilities (caps):

    "caps": [
        { "type": "buckets",
          "perm": "*"},
        { "type": "usage",
          "perm": "*"},
        { "type": "metadata",
          "perm": "read"},
        { "type": "users",
          "perm": "*"}
    ]

You can use `radosgw-admin caps add --uid <USER_ID> --caps "buckets=read,write"` to add capabilities to an existing user.

## Example

See the example in [examples/radosgw-admin-example.py](https://github.com/valerytschopp/python-radosgw-admin/blob/master/examples/radosgw-admin-example.py)

