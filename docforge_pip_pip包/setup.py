"""
DocForge - 办公与数据处理自动化框架
"""

from setuptools import setup, find_packages

# 版本信息
__version__ = "0.1.0"
__author__ = "Xiaomi-MiMo-V2-pro and NocXen"
__description__ = "办公与数据处理自动化框架"

# 读取依赖
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# 读取README
try:
    with open('docforge/README.md', 'r', encoding='utf-8') as f:
        long_description = f.read()
except:
    long_description = "DocForge - 办公与数据处理自动化框架"

setup(
    name='docforge',
    version=__version__,
    author=__author__,
    description=__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nocxen/docforge',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'docforge=docforge.cli:main',
        ],
    },
    include_package_data=True,
    package_data={
        'docforge': ['*.md', '*.txt', '*.json'],
    },
)
