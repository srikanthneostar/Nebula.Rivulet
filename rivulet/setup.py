from setuptools import setup, find_packages

setup(
    name="nebula.rivulet",
    version="3.10.0",
    packages=find_packages(where="build/lib"),
    package_dir={"": "build/lib"},
    install_requires=[
        "pymongo",
        "sentence-transformers"
    ],
    author="Administrator",
    author_email="administrator@xecutables.com",
    description="Pipeline framework for Nebula - provides data sources, stages, and pipeline orchestration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://192.168.1.165/root/nebula-rivulet",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
