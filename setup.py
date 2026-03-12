"""
Setup configuration for pipescraper.
"""

from setuptools import setup, find_packages
import pathlib

# Read the README file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text(encoding="utf-8")

# Read requirements
REQUIREMENTS = (HERE / "requirements.txt").read_text(encoding="utf-8").splitlines()

setup(
    name="pipescraper",
    version="0.3.0",
    author="pipescraper Contributors",
    author_email="contact@pipescraper.dev",
    description="A pipe-based news article scraping and metadata extraction library",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/Yasser03/pipescraper",
    project_urls={
        "Bug Tracker": "https://github.com/Yasser03/pipescraper/issues",
        "Documentation": "https://github.com/Yasser03/pipescraper#readme",
        "Source Code": "https://github.com/Yasser03/pipescraper",
    },
    packages=find_packages(exclude=["tests", "tests.*", "examples", "examples.*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Text Processing :: Markup :: HTML",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=REQUIREMENTS,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "pipeframe": [
            "pipeframe>=0.1.0",
        ],
        "pipeplotly": [
            "pipeplotly>=0.1.0",
        ],
        "all": [
            "pipeframe>=0.1.0",
            "pipeplotly>=0.1.0",
        ],
    },
    keywords=[
        "web scraping",
        "news extraction",
        "article metadata",
        "trafilatura",
        "newspaper3k",
        "pipe operator",
        "data pipeline",
        "nlp",
        "text extraction",
    ],
    include_package_data=True,
    zip_safe=False,
)
