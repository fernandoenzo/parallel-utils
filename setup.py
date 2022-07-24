# encoding:utf-8

# More on how to configure this file here: https://setuptools.readthedocs.io/en/latest/setuptools.html#metadata
import setuptools
from setuptools import find_packages

name = 'parallel-utils'

# https://www.python.org/dev/peps/pep-0440/#version-scheme
version = '1.2'

description = 'This library implements a class Monitor, as defined by Per Brinch Hansen and C.A.R. Hoare, ' \
              'for synchronization and concurrent management of threads and processes in Python. It also provides other ' \
              'functions to ease the creation and collection of results for both threads and processes.'

with open("README.md", "r") as fh:
    long_description = fh.read()

author = 'Fernando Enzo Guarini'
author_email = 'fernandoenzo@gmail.com'

url = 'https://github.com/fernandoenzo/parallel-utils/'

# https://packaging.python.org/guides/distributing-packages-using-setuptools/#project-urls
project_urls = {
    'Source': 'https://github.com/fernandoenzo/parallel-utils/',
}

packages = find_packages(exclude=("*tests*",))
test_suite = 'parallel_utils.tests'

license = 'GPLv3+'

zip_safe = True

keywords = 'concurrency concurrent concurrent-programming distributed library lock locker locker-manager module monitor ' \
           'multiprocess multiprocessing multithreading parallel parallelism process semaphore sync synchronize ' \
           'synchronization thread threading'

python_requires = '>=3.9'

install_requires = [
    "private-attrs",
]

# https://pypi.org/classifiers/
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 3 :: Only',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10',
    'Topic :: Software Development :: Libraries :: Python Modules',
]
setuptools.setup(
    author_email=author_email,
    author=author,
    classifiers=classifiers,
    description=description,
    download_url=url,
    install_requires=install_requires,
    keywords=keywords,
    license=license,
    long_description_content_type="text/markdown",
    long_description=long_description,
    name=name,
    packages=packages,
    project_urls=project_urls,
    python_requires=python_requires,
    test_suite=test_suite,
    url=url,
    version=version,
    zip_safe=zip_safe,
)
