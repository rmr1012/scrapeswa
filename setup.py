import setuptools
import os
thelibFolder = os.path.dirname(os.path.realpath(__file__))
requirementPath = thelibFolder + '/requirements.txt'
install_requires = [] # Examples: ["gunicorn", "docutils>=0.3", "lxml==0.5a7"]
if os.path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

import scrapeswa


setuptools.setup(
    name="scrapeswa",
    version=scrapeswa.__version__,
    author="Dennis Ren",
    install_requires=install_requires,
    author_email="code@dennisren.com",
    description="A Simple Scraper for Southwest Airlines",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rmr1012/scrapeswa",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only"
    ],
)
