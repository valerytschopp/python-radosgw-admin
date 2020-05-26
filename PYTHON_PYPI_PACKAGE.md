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
    username = valery-tschopp
    password = **********

## Clean up & build

    rm -fr build dist radosgw_admin.egg-info
    python setup.py sdist bdist_wheel

## Test local build

    rm -fr test-local-venv
    virtualenv test-local-venv
    . test-local-venv/bin/activate
    python setup.py install
    python examples/radosgw-admin-example.py --hostname $S3_HOSTNAME --access-key $S3_ACCESS_KEY --secret-key $S3_SECRET_KEY
    deactivate

## Register and upload files

### testpypi

    twine upload -r testpypi dist/*

Check https://test.pypi.org

### pypi

    twine upload dist/*

Check https://pypi.python.org

## Test Package

    rm -fr test-package-venv
    virtualenv test-package-venv
    . test-package-venv/bin/activate
    pip install -i https://test.pypi.org/simple/ radosgw-admin
    #pip install radosgw-admin

    python examples/radosgw-admin-example.py --hostname $S3_HOSTNAME --access-key $S3_ACCESS_KEY --secret-key $S3_SECRET_KEY
    cp ../examples/*.py .

    deactivate
