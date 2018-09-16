try:
    # Try using ez_setup to install setuptools if not already installed.
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # Ignore import error and assume Python 3 which already has setuptools.
    pass

from setuptools import setup, find_packages

# REFERENCE: https://setuptools.readthedocs.io/en/latest/setuptools.html#declaring-dependencies
# REFERENCE: https://pypi.org/

''' TODO:
    integrate:
        * test_suite
        * tests_require
        * test_loader
        * use_2to3* for integrating python support for 2/3
'''

classifiers = ['Development Status :: 4 - Beta',
               'Operating System :: POSIX :: Linux',
               #'License :: OSI Approved :: MIT License',
               'Intended Audience :: Developers',
               'Programming Language :: Python :: 2.7',
               #'Programming Language :: Python :: 3',
               'Topic :: Software Development',
               'Topic :: System :: Hardware']

setup(
    name              = 'pv_array_solar_tracker',
    version           = '0.1',
    author            = 'Glen Nicholls',
    author_email      = 'gnicholl@uccs.edu',
    description       = 'Python base to control PV array to track the sun throughout the day',
    license           = '',
    classifiers       = classifiers,
    url               = 'https://github.com/GlenNicholls/solar_tracking_project',
    dependency_links  = ['https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.6.5',
                         'https://github.com/adafruit/Adafruit_Python_MCP3008/tarball/master#egg=Adafruit-MCP3008-1.0.2'],
                         # 'https://github.com/adafruit/Adafruit_CircuitPython_DS3231/tarball/master#egg=Adafruit_CircuitPython_DS3231-2.1.0',],
    install_requires  = ['Adafruit-GPIO>=0.6.5',
                         'Adafruit-MCP3008>=1.0.2'],
                         # 'adafruit-circuitpython-ds3231>=2.1.0'],
    packages          = find_packages('src'), # can also leave blank (empty parameters) to declare anything below, don't need src/ top level in setup.py loc
    package_dir       = {'':'src'},
    package_data      = {'':['__init__.py']} # ['' : ['*.data', '*.rst'],] -- include packages with these file delimeters in all sub dirs from package_dir
                                              # 'myPkg' : ['data/*.dat'] ]  -- only include .dat files in myPkg/data
)

