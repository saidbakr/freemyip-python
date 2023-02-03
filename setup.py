import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="freemyip-saidbakr", # Replace with your own username
    version="0.10.4",
    author="Said Bakr",
    author_email="said_fox@yahoo.com",
    description="Freemyip dynamic dns updater",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/saidbakr/freemyip-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
) 
