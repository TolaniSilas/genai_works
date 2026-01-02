# setup.py
from setuptools import setup, find_packages

setup(
    name="currency_analyst_agent",
    version="0.1",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "crewai[tools]>=1.7.2",   
        "fastapi>=0.128.0",       
        "streamlit>=1.52.2",     
    ],
    python_requires=">=3.10",
)
