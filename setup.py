from setuptools import setup, find_packages

setup(
    name="gpt-pilot",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#")
    ],
    entry_points={
        "console_scripts": [
            "gpt-pilot=main:main",
        ],
    },
)