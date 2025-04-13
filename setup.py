from setuptools import setup, find_packages

setup(
    name="WenDataStudio",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pandas>=1.5.0",
        "matplotlib>=3.5.0",
        "seaborn>=0.11.0",
        "streamlit>=1.10.0",
        "openpyxl>=3.0.0",
        "numpy>=1.20.0",
    ],
    author="sonw7",
    author_email="example@example.com",
    description="表格数据处理与可视化工具",
    keywords="data,visualization,excel,csv",
    python_requires=">=3.8",
)