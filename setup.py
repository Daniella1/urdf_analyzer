import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="urdf_analyzer",
    version="0.0.1",
    author="Daniella Tola",
    author_email="dt@ece.au.dk",
    description="A tool for analyzing URDF files",
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    url="https://github.com/Daniella1/urdf_analyzer",
    packages=["urdf_analyzer"],
    install_requires=[
        "numpy>=1",
        "pandas>=1",
    ],
    extras_require={
        "urdf_tools": ["yourdfpy","urdfpy","roboticstoolbox-python"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={"console_scripts": ["urdf_analyzer=urdf_analyzer.cli:main"]},
)