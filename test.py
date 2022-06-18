from pathlib import Path
import os
import ifc2graph.ifcgeometry as ifcgeometry
import ifc2graph.graph as graph

path = str(Path(__file__).parent)
project_name = "test"
ifc_file_name = "Office Building.ifc"
# ifc_file_name = "Residential House.ifc"
ifc_file_path = os.path.join(path, "test_ifc_files", ifc_file_name)

# First the IfcGeometry object is instantiated.
ifc_geometry = ifcgeometry.IfcGeometry(ifc_file_path, project_name, force_init=True)

# Using the IfcGeometry object, a dictionary is produced. 
# Here, the keys corresponds to the Name attribute of the IfcSpace entities contained in the IFC input file. 
# The values of this dictionary are lists containing the Name attributes of the adjacent IfcSpace entities.
adjacent_space_dict = ifc_geometry.get_adjacent_spaces()



# To produce an image of the generated graph, a Graph object must be instantiated.
graph = graph.Graph(adjacent_space_dict=adjacent_space_dict,
                    space_type_name_dict=ifc_geometry.space_type_name_dict,
                    name=project_name)


# This function saves as a default an image of the generated graph in the .../Ifc2Graph directory.
# Optionally, a path can be given as argument. 
# E.g.: 
# graph.generate_graph(save_dir="path/to/rep")
graph.generate_graph() 