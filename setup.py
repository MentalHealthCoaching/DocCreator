from setuptools import setup, find_packages

setup(
    name="doccreator",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyQt5',
        'python-docx',
        'docx2pdf',
        'PyPDF2',
        'cryptography',
        'Pillow',
        'Flask',
        'reportlab',
    ],
    entry_points={
        'console_scripts': [
            'doccreator=desktop_app.main:main',
        ],
    },
)
