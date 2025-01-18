from setuptools import setup, find_packages

setup(
    name="gpt-pilot",
    version="0.1.0",
    packages=find_packages(exclude=["tests*"]),
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
        ],
    },
    python_requires=">=3.11",
    author="Eric B",
    description="GPT-Pilot project with deepseek integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.11",
    ],
)