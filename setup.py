import sys

from setuptools import setup
from areplay import __version__

install_requires = ['apache-log-parser', 'gevent', 'requests', ]

if sys.version_info < (2, 7):
    install_requires += ['argparse']

classifiers = [
    "Programming Language :: Python",
    "License :: OSI Approved :: MIT License",
    "Development Status :: 1 - Planning"
]

description = ''

for file_ in ('README', 'CHANGES', 'CONTRIBUTORS'):
    with open('%s.rst' % file_) as f:
        description += f.read() + '\n\n'

setup(
    name='areplay',
    packages=['areplay'],
    version=__version__,
    description='Apache Log live replicator',
    author='Hugo Dias',
    author_email='hdias@synchlabs.com',
    url='https://github.com/peterldowns/areplay',
    download_url='https://github.com/peterldowns/areplay/tarball/0.1',
    keywords=['testing', 'logging'],
    include_package_data=True,
    classifiers=classifiers,
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'areplay=areplay.main:main',
        ],
    }
)
