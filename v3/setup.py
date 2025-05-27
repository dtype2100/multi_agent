"""패키지 설정 파일"""

from setuptools import setup, find_packages

setup(
    name="agi_agent_system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "langgraph>=0.0.10",
        "llama-cpp-python>=0.2.0",
        "pydantic>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "python-dotenv>=1.0.0"
    ],
    entry_points={
        "console_scripts": [
            "agi-agent=agi_agent_system.main:main",
            "agi-agent-cli=agi_agent_system.run_cli:main"
        ]
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="AGI 에이전트 시스템",
    long_description=open("agi_agent_system/README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/agi-agent-system",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11"
    ],
    python_requires=">=3.8"
) 