from setuptools import setup, find_packages

setup(
    name="BlueStacksAgent",
    version="0.2.2",
    description="A Python library for real-time interaction with BlueStacks using scrcpy, minicap, and MediaProjection.",
    long_description=open("README.md", encoding="utf8").read(),
    long_description_content_type="text/markdown",
    author="Alessandro Flati",
    author_email="alessandro.flati@gmail.com",
    url="https://github.com/AlessandroFlati/BlueStacksAgent",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*"]),
    install_requires=[
        "scrcpy-client",  # required for the scrcpy interface
        # You can add other requirements here as needed.
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ],
)
