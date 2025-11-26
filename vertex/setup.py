from setuptools import setup, find_packages

setup(
    name="nebula.vertex",
    version="3.10.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    package_data={
        "": ["*.pem"],  # Include SSL certificate files
    },
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-jose[cryptography]",
        "python-multipart",
        "celery",
        "pydantic",
        "pycryptodome",
    ],
    author="Administrator",
    author_email="administrator@xecutables.com",
    description="REST API layer for Nebula Rivulet - provides FastAPI endpoints for search and ML operations",
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
