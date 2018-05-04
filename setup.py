import hpe3par_sdk

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


setup(
  name='hpe3par_sdk',
  version=hpe3par_sdk.version,
  description="HPE 3PAR HTTP REST Client",
  #author="Walter A. Boring IV",
  #author_email="walter.boring@hpe.com",
  #maintainer="Walter A. Boring IV",
  keywords=["hpe", "3par", "rest"],
  install_requires=['python-3parclient'],
  tests_require=["paramiko", "eventlet", "requests", "nose", "werkzeug", "nose-testconfig"],
  license="Apache License, Version 2.0",
  packages=find_packages(),
  provides=['hpe3par_sdk'],
  url="http://packages.python.org/hpe3par_sdk",
  classifiers=[
     'Development Status :: 5 - Production/Stable',
     'Intended Audience :: Developers',
     'License :: OSI Approved :: Apache Software License',
     'Environment :: Web Environment',
     'Programming Language :: Python',
     'Programming Language :: Python :: 2.6',
     'Programming Language :: Python :: 2.7',
     'Programming Language :: Python :: 3.4',
     'Topic :: Internet :: WWW/HTTP',

     ]
  )
