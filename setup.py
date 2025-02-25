from setuptools import setup, find_packages

setup(
    name="fortipy",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests",  # Example dependency
    ],
    entry_points={
        "console_scripts": [
            "fortipy = fortipy.main:main"
        ]
    },
)
