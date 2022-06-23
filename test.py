from pathlib import Path
import os
import ifc2graph.ifcgeometry as ifcgeometry
import ifc2graph.ifcgraph as ifcgraph

path = str(Path(__file__).parent)
project_name = "test"
ifc_file_name = "Office Building.ifc"
# ifc_file_name = "Residential House.ifc"
ifc_file_path = os.path.join(path, "test_ifc_files", ifc_file_name)

# First the IfcGeometry object is instantiated.
ifc_geometry = ifcgeometry.IfcGeometry(ifc_file_path, project_name, force_init=True)

# The extracted geometry can be visualized using the below function (this will open a new window).
# Simply close the opened window to execute the rest of this file.
ifc_geometry.visualize()

# Using the IfcGeometry object, a dictionary can be created. 
# Here, the keys corresponds to the Name attribute of the IfcSpace entities contained in the IFC input file. 
# The values of this dictionary are lists containing the Name attributes of the adjacent IfcSpace entities.
adjacent_spaces_dict = ifc_geometry.get_adjacent_spaces_dict()

# To produce an image of the generated graph, a Graph object must be instantiated.
ifc_graph = ifcgraph.IfcGraph(adjacent_spaces_dict=adjacent_spaces_dict,
                                space_type_name_dict=ifc_geometry.space_type_name_dict,
                                space_storey_dict=ifc_geometry.space_storey_dict,
                                graph_name=project_name)


# This function saves as a default an image of the generated graph in the .../Ifc2Graph directory.
# Optionally, a path can be given as argument. 
# E.g.: 
# ifc_graph.generate_graph(save_dir="path/to/rep")
ifc_graph.generate()
