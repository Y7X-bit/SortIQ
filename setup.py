from setuptools import setup

setup(
    name="FileOrganizerPro",
    version="1.0",
    author="Yugank",
    description="A smart file organizer that categorizes your files by type.",
    py_modules=["file_organizer"],
    entry_points={
        "console_scripts": [
            "organize-files = file_organizer:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
