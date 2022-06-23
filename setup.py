from setuptools import setup

setup(
    name="ifc2graph",
    version="0.0.0",
    description="A tool designed to extract room topology from files following the Industry Foundation Classes (IFC) standard.",
    url="https://github.com/JBjoernskov/Ifc2Graph",
    keywords="ifc graph optimization model identification estimation",
    author="Jakob Bjørnskov, Center for Energy Informatics SDU",
    author_email="jakob.bjornskov@me.com, jabj@mmmi.sdu.dk",
    license="BSD",
    platforms=["Windows", "Linux"],
    packages=[
        "ifc2graph",
        "ifc2graph.utils",
    ],
    include_package_data=True,
    install_requires=[
        "IfcOpenShell",
        "Trimesh",
        "NumPy",
        "NetworkX",
    ],
    classifiers=["Programming Language :: Python :: 3"],
)