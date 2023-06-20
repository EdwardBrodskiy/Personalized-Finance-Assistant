from setuptools import setup, find_packages

setup(
    name='theme_tk',
    version='0.1',
    packages=find_packages(),
    author='Edward Brodski',
    author_email='brodskiedward@gmail.com',
    description='A Tkinter library extension',
    long_description=open('README.md').read(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    install_requires=[
        'customtkinter>=5.1.3'
    ]
)