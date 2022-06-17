# Ifc2Graph

The Ifc2Graph module can be used as a tool to extract space topology from IFC-files. 


## Installation:
- XXX


### Dependencies
- XXX


## Usage 


### Ifc2Graph
Ifc2Graph currently has two functionalities. The IfcGeometry class extracts geometry 
The tool first extracts the geometry for each IfcSpace entity in the provided IFC-file using [IfcOpenShell](http://ifcopenshell.org/python), which is used to define [Trimesh](https://trimsh.org/trimesh.html) objects. 
These Trimesh objects

#### Input:
As input a valid IFC-file must be provided. An example file is found in the "test_ifc_files" folder.

#### Ouput:
The output is a dictionary with keys corresponding to the Name attribute of the IfcSpace entities contained in the IFC input file.
The values of this dictionary are lists containing the Name attributes of the adjacent IfcSpace entities.


<img src="https://user-images.githubusercontent.com/74002963/174341376-44a9bcea-aec3-4a21-b186-1f16fc31a294.png" width="50" height="50">
<img src="https://user-images.githubusercontent.com/74002963/174342723-81112bf1-4928-452a-b142-6d8372bd83e8.png" width="50" height="50">

## Example
The test.py file shows the basic use of the module.








