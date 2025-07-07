#!/usr/bin/env python3
"""
HELIX v2.0 项目设置脚本
按照系统级CLAUDE.md文件管理规范创建
"""

from setuptools import setup, find_packages

setup(
    name="helix",
    version="2.0.0",
    description="AI-driven creative production system",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        line.strip()
        for line in open("requirements.txt").readlines()
        if line.strip() and not line.startswith("#")
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0", 
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "helix-api=api.main:main",
            "helix-orchestrator=orchestrator.main:main",
        ]
    },
)