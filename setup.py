# setup module

# imports
from setuptools import setup
from setuptools import find_packages

# running setup
setup(name='pytree',
      version='2.0',
      description="pytree - a simpler 'tree' command running in python",
      author='angelo-angonezi',
      author_email='angeloangonezi2@gmail.com',
      packages=find_packages(where='./src',
                             exclude=['./test_folder']),
      package_dir={'': 'src'},
      python_requires='>=3.9',
      install_requires=['treelib',
                        'psutil'],
      entry_points={'console_scripts': ['pytree = pytree:main']})

# end of current module
