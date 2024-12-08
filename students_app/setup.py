from setuptools import setup, find_packages

setup(
    name="students_app",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.9',
        'SQLAlchemy>=2.0.23',
        'pandas>=2.1.3',
        'openpyxl>=3.1.2',
    ],
)
