# Ifc2Graph

The Ifc2Graph package can be used as a tool to extract space topology from IFC-files. 
Ifc2Graph currently has two functionalities, divided into the classes IfcGeometry and IfcGraph.

## Installation

The package has been tested for Python 3.7.12, but should also work for other 3.7.X versions. 

The package can be install with pip and git as follows:
```bat
python -m pip install git+https://github.com/JBjoernskov/Ifc2Graph
```

To utilize the ifcgraph module, Graphviz must be installed separately:
- [Graphviz](https://graphviz.org/download) (Remember to add the directory to system path)


## Usage 


### IfcGeometry
The IfcGeometry class extracts the geometry for each IfcSpace entity in the provided IFC-file using [IfcOpenShell](http://ifcopenshell.org/python). This geometry is used to instantiate [Trimesh](https://trimsh.org) objects, which are then used in combination with [NumPy](https://numpy.org) to process the geometry and determine the adjacency of rooms. 

#### Input:
As input a path to a valid IFC-file must be provided. Example files are found in the "test_ifc_files" folder.

<p float="left">
    <img src="https://user-images.githubusercontent.com/74002963/174432556-3e2abdf3-794f-4a54-a24c-0efa45717420.png" width="400">
    <img src="https://user-images.githubusercontent.com/74002963/174432617-f8bc0f66-387d-45f2-9285-7edd3a0620fc.png" width="400">
</p>

[Source](https://www.ifcwiki.org/index.php?title=KIT_IFC_Examples): 
*Institute for Automation and Applied Informatics (IAI) / Karlsruhe Institute of Technology (KIT)*

#### Ouput:
The output is a dictionary with keys corresponding to the Name attribute of the IfcSpace entities contained in the IFC input file.
The values of this dictionary are lists containing the Name attributes of the adjacent IfcSpace entities.


### IfcGraph
The IfcGraph class visualizes the obtained adjacency graph using [NetworkX](https://networkx.org) to construct the graph and [Graphviz](https://graphviz.org) to visualize the the graph.

#### Input:
As input, the previously obtained dictionary must be provided. 

#### Ouput:
The output is an image of the generated graph.
Below, examples of generated graph images is seen for an actual building. 

<p float="left">
    <img src="https://user-images.githubusercontent.com/74002963/174341376-44a9bcea-aec3-4a21-b186-1f16fc31a294.png" width="400">
    <img src="https://user-images.githubusercontent.com/74002963/174342723-81112bf1-4928-452a-b142-6d8372bd83e8.png" width="400">
</p>



## Example
The test.py file shows the basic use of the package.








