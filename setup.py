from distutils.core import setup

setup(
    name='rgkit',
    version='0.1',
    packages=['rgkit',],
    package_data={'rgkit': ['maps/*.py']},
    license='Unlicense',
    long_description=open('README.md').read(),
    scripts=['bin/run.py', 'bin/mapeditor.py'],
)