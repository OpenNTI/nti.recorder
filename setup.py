import codecs
from setuptools import setup, find_packages

entry_points = {
    'console_scripts': [
    ],
}

TESTS_REQUIRE = [
    'nti.testing',
    'zope.dottedname',
    'zope.testrunner',
]


def _read(fname):
    with codecs.open(fname, encoding='utf-8') as f:
        return f.read()


setup(
    name='nti.recorder',
    version=_read('version.txt').strip(),
    author='Jason Madden',
    author_email='jason@nextthought.com',
    description="NTI recorder",
    long_description=(_read('README.rst') + '\n\n' + _read('CHANGES.rst')),
    license='Apache',
    keywords='recorder',
    classifiers=[
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    url="https://github.com/NextThought/nti.recorder",
    zip_safe=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['nti'],
    tests_require=TESTS_REQUIRE,
    install_requires=[
        'setuptools',
        'nti.base',
        'nti.dublincore',
        'nti.externalization',
        'nti.property',
        'nti.traversal',
        'nti.schema',
        'nti.zope_catalog',
        'persistent',
        'transaction',
        'ZODB',
        'zope.annotation',
        'zope.cachedescriptors',
        'zope.component',
        'zope.container',
        'zope.deprecation',
        'zope.event',
        'zope.interface',
        'zope.intid',
        'zope.lifecycleevent',
        'zope.location',
        'zope.mimetype',
        'zope.security',
    ],
    extras_require={
        'test': TESTS_REQUIRE,
    },
    entry_points=entry_points,
    test_suite="nti.recorder.tests",
)
