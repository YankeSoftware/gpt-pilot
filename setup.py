from setuptools import setup, find_packages

setup(
    name="gpt-pilot",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "core": ["prompts/**/*", "templates/**/*"]
    },
    install_requires=[
        line.strip()
        for line in open("requirements.txt")
        if line.strip() and not line.startswith("#") and not line.startswith("-r")
    ],
    extras_require={
        "dev": [
            line.strip()
            for line in open("requirements-dev.txt")
            if line.strip() and not line.startswith("#") and not line.startswith("-r")
        ]
    },
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "gpt-pilot=main:main",
        ],
    }
)