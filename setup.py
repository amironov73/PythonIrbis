import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="irbis",
    version="0.1.100",
    author="Alexey Mironov",
    author_email="amironov73@gmail.com",
    description="Framework for client development for popular Prussian library computer system IRBIS64",
    keywords='IRBIS64',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amironov73/PythonIrbis",
    packages=setuptools.find_packages(),
    classifiers=(
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
