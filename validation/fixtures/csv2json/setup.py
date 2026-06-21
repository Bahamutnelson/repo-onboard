from setuptools import setup

setup(
    name="csv2json",
    version="0.2.0",
    description="Convert CSV files to JSON from the command line",
    py_modules=["cli"],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "csv2json=cli:main",
        ],
    },
)
