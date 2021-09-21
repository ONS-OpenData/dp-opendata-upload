import setuptools

setuptools.setup(
    name="lambdautils",
    packages=["lambdautils"],
    version="0.0.1",
    description="Reusable classes, functions and schemas for opendata team lambda functions",
    author="Michael Adams",
    author_email="michael.adams@ons.gov.uk",
    url="https://github.com/mikeAdamss/dp-opendata-lambda-utils",
    download_url="https://github.com/ONS-Opendata/dp-opendata-upload/archive/0.1.tar.gz",
    keywords=["lambda", "opendata"],
    install_requires=["jsonschema", "boto3"],
)
