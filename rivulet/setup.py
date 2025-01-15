from setuptools import setup, find_packages

setup(
    name="nebula-rivulet",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "elasticsearch>=7.0.0",
        "pandas>=1.0.0",
        "scikit-learn>=0.24.0",
    ],
    author="Administrator",
    author_email="your.email@example.com",
    description="A framework for running AI pipelines with Elasticsearch data",
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
