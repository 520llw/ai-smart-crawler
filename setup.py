from setuptools import setup, find_packages

with open("README_GITHUB.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-smart-crawler",
    version="1.0.0",
    author="GongJianwei",
    author_email="",
    description="AI-enhanced smart web crawler with knowledge base",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GongJianwei/ai-smart-crawler",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0",
        "beautifulsoup4>=4.12.0",
        "aiohttp>=3.9.0",
    ],
    extras_require={
        "full": [
            "crawl4ai>=0.4.0",
            "playwright>=1.40.0",
            "openai>=1.0.0",
            "chromadb>=0.4.0",
            "langgraph>=0.0.50",
        ],
    },
)
