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



## Cite as
```yaml
@inproceedings{Ifc2Grap},
title = {A Modular Thermal Space Coupling Approach for Indoor Temperature Forecasting Using Artificial Neural Networks",
abstract = {With the increasing digitalization of buildings andthe adoption of comprehensive sensing and meter-ing networks, the concept of building digital twinsis emerging as a key component in future smart andenergy-efficient buildings. Such digital twins enablethe use of flexible and adaptable data-driven modelsto provide services such as automated performancemonitoring and model-based operational planning inbuildings. In this context, accurate indoor temper-ature models are vital to ensure that the proposedoperational strategies are effective, feasible, and donot compromise indoor comfort. In this work, thesignificance of thermal space coupling for data-drivenindoor temperature forecasting is investigated by as-sessing and comparing the performance of an isolatedand coupled Long Short-Term Memory model archi-tecture across 70 spaces in a case study building. Toconstruct the coupled architecture, an open-sourcetool is developed and presented, which allows the au-tomated extraction of space topology from IFC-filesto identify adjacent spaces. The coupled architec-ture is found to outperform the isolated architecturefor ∼84% of the investigated spaces, with significantimprovements under certain operational and climaticconditions. To account for the subset of spaces wherethe isolated architecture performs better, it is pro-posed to select between the two architectures accord-ingly. The demonstrated modularity and embeddedadaptability of the proposed model architectures pro-vide a sound basis for implementation in a highly dy-namic building Digital Twin environment.},
author = {Jakob Bj{\o}rnskov and Muhyiddine Jradi},
year = {2022},
month = {dec},
language = {English},
volume = {6},
booktitle = {Proceedings of BSO Conference 2022: 6th Conference of IBPSA-England},
publisher = {International Building Performance Simulation Association},
note = {Building Simulation and Optimisation 2022 ; Conference date: 13-12-2022 Through 14-12-2022},
}
```




