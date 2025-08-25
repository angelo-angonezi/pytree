# setup module

from setuptools import setup
from setuptools import find_packages

setup(name="pytree",
      version="2.0",
      description="pytree - a simpler 'tree' command running in python",
      author='angelo-angonezi',
      author_email='angeloangonezi2@gmail.com',
      packages=find_packages(where="src"),
      package_dir={"": "src"},
      entry_points={"console_scripts": ["pytree = pytree:main",]},
      python_requires=">=3.9")

# end of current module
