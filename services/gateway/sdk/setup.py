from setuptools import setup, find_packages

setup(
    name="argus-sdk",
    version="0.1.0",
    description="Official Python SDK for the Argus observability platform",
    author="Santino Coronel",
    author_email="santinopillados@gmail.com",
    url="https://github.com/santinopillados-alt/argus-platform",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "httpx>=0.27.0",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Libraries",
    ],
    keywords="observability monitoring logging metrics tracing argus",
)