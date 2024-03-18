import pytest
import os
import requests
import tarfile

def pytest_sessionstart(session):

    res = requests.get('https://osf.io/2a4kh/download', stream=True)
    target_path = 'wnutils_tutorial_data.tar.gz'

    if res.status_code == 200:
        with open(target_path, 'wb') as f:
            f.write(res.raw.read())

    tar = tarfile.open(name=target_path, mode='r:gz')
    tar.extractall()
    tar.close()

def pytest_sessionfinish(session, exitstatus):
    os.system('rm -fr *.xml *.h5 *.gz')
