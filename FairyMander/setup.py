from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="fairymander",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    author="Jeysen Angous, Dylan Franco, Sophia Ingram, Ceanna Jarrett, Izaac Molina",
    author_email="jaa678@nau.edu, dfk55@nau.edu, sni7@nau.edu, cjj@262@nau.edu, iam97@nau.edu",
    description="Package for generating fair voting district plans, developed as part of the FairyMander capstone project at Northern Arizona University",
    url="https://github.com/Jeysen34/FairyMander",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
