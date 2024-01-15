from setuptools import setup, find_packages

setup(
    name='Score Board',
    version='2.0.0',
    packages=find_packages(),
    install_requires=[
        'attrs',
        'nicegui',
        'pyyaml',
        'tortoise-orm',
    ],
)
