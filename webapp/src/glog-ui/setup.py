from setuptools import setup

setup(
    name='glog_ui',
    packages=['glog_ui'],
    version='0.170404',
    include_package_data=True,
    install_requires=[
        'Flask==0.12.2',
        'matplotlib==2.1.2',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)
