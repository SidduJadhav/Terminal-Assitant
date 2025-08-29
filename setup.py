"""Setup script for AI Terminal Assistant."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-terminal",
    version="2.0.0",
    author="Siddu Jadhav",
    description="Natural language shell command interface",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SidduJadhav/ai-terminal",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: System :: Shells",
        "Topic :: Utilities",
    ],
    python_requires=">=3.11",
    install_requires=[
        "google-generativeai>=0.8.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-terminal=ai_terminal.main:main",
            "ait=ai_terminal.main:main",  # Short alias
        ],
    },
)