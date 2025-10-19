# unsure
from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "readme.md").read_text(encoding='utf-8')

setup(
    name="talekeeper",
    version="3.0.0",
    author="TaleKeeper Development Team",
    description="A single-player D&D 2024 tactical RPG for Windows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kostchei/talekeeper",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Role-Playing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
    ],
    python_requires=">=3.9",
    install_requires=[
        "PyQt6>=6.5.0",
        "PyQt6-WebEngine>=6.5.0",
        "piper-tts>=1.2.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-qt>=4.0.0",
            "pylint>=2.0.0",
            "mypy>=1.0.0",
        ],
        "lora": [
            "torch>=2.0.0",
            "torchaudio>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "talekeeper=talekeeper.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "talekeeper": ["py.typed"],
    },
)
