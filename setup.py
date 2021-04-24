"""Setup for package Blowboard

This:
- Gets version information (__version__)
- Reads README.md into long_description
- Calls setuptools.setup()
"""

import re
import setuptools

# --- Collect version information --------------------------------------------
version_info = open('blowboard/__init__.py').read()

pattern = r'__version__\s?=\s?[\'\"](.*)[\'"]'
match = re.search(pattern, version_info)
if match:
    __version__ = match.group(1)
else:
    __version__ = None

# --- Collect README ---------------------------------------------------------
with open('README.md', 'r') as readme_file:
    readme = readme_file.read()

# --- Setup ------------------------------------------------------------------
if __name__ == '__main__':
    setuptools.setup(name='blowboard',
                     version=__version__,
                     packages=setuptools.find_packages(),
                     install_requires=[],
                     long_description=readme,
                     )
