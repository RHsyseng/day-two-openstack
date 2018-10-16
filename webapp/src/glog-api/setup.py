from setuptools import setup

setup(
    name='glog_api',
    packages=['glog_api'],
    version='0.170404',
    include_package_data=True,
    install_requires=[
        'bson',
        'Flask',
        'flask-restplus',
        'pymongo==3.6.0',
        'Werkzeug==0.14.1',
        'python-dateutil==2.6.1',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
