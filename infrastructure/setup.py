import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="pipeline",
    version="0.0.1",

    description="AWS Data Analytics Playground",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Panagiotis Katsaroumpas",

    package_dir={"": "pipeline"},
    packages=setuptools.find_packages(where="pipeline"),

    install_requires=[
        "aws-cdk.core==1.130.0",
        "aws-cdk.aws-kinesisfirehose-destinations==1.130.0",
        "aws-cdk.aws-lambda-python==1.130.0",
        "aws-cdk.aws-redshift==1.130.0",
        "aws-cdk.pipelines==1.130.0",
        "flake8==4.0.1",
        "mypy==0.910",
        "python-benedict==0.24.3"
    ],

    python_requires=">=3.6",

    classifiers=[
        "Development Status :: 4 - Beta",

        "Intended Audience :: Developers",

        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",

        "Topic :: Software Development :: Code Generators",
        "Topic :: Utilities",

        "Typing :: Typed",
    ],
)
