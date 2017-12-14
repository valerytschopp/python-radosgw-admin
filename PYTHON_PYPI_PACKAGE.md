# Python package in PyPi

https://wiki.python.org/moin/TestPyPI

https://testpypi.python.org

https://pypi.python.org


## ~/.pypirc

    [distutils]
    index-servers=
        pypi
        testpypi
  
    [testpypi]
    repository = https://test.pypi.org/legacy/
    username = valery-tschopp
    password = ********
  
    [pypi]
    repository = https://upload.python.org/legacy/
    username = valery-tschopp
    password = **********


## Clean up & build

    rm -fr build dist radosgw_admin.egg-info
    python setup.py sdist bdist_wheel


## Register and upload files

### testpypi

    twine register -r testpypi dist/radosgw_admin-VERSION-py2.py3-none-any.whl
    twine upload -r testpypi dist/*

Check https://test.pypi.org

### pypi

    twine register dist/radosgw_admin-VERSION-py2.py3-none-any.whl
    twine upload dist/*

Check https://pypi.python.org


## Test

    rm -fr test-package
    virtualenv test-package
    cd test-package
    . bin/activate
    pip install -i https://test.pypi.org/legacy/ radosgw-admin
    #pip install radosgw-admin

    cp ../examples/*.py .
    python radosgw-admin-example.py --hostname $S3_HOSTNAME --access-key $S3_ACCESS_KEY --secret-key $S3_SECRET_KEY

    deactivate


