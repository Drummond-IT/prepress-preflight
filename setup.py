from setuptools import setup, find_packages

setup(
    name="prepress-preflight",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["click>=8.1", "rich>=13.0"],
    entry_points={"console_scripts": ["prepress-preflight=preflight.cli:cli"]},
    python_requires=">=3.9",
    author="darshd9941",
    description="Prepress file preflight — scan PDFs for print-readiness issues",
    url="https://github.com/darshd9941/prepress-preflight",
    license="MIT",
)
