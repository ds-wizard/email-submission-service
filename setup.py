from setuptools import setup, find_packages
import os

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = ''.join(f.readlines())

setup(
    name='email_submitter',
    version='0.1.0',
    keywords='dsw submission document email notification',
    description='DSW submission service sending email notifications',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Marek Suchánek',
    author_email='suchama4@fit.cvut.cz',
    license='Apache2',
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'PyYAML',
        'requests',
        'uvicorn[standard]',
    ],
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
    ],
)
