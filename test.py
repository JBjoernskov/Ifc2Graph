from pathlib import Path
import ifcopenshell
import os
import ifc2graph.ifcgeometry as ifcgeometry
import ifc2graph.graph as graph

path = str(Path(__file__).parent)
project_name = "test"
ifc_file_name = "test.ifc"
ifc_file_path = os.path.join(path, "test_ifc_files", ifc_file_name)

print(ifc_file_path)
ifc_file = ifcopenshell.open(ifc_file_path)
ifc_geometry = ifcgeometry.IfcGeometry(ifc_file, project_name, force_init=True)
adjacent_space_dict = ifc_geometry.get_adjacent_spaces()
graph = graph.Graph(adjacent_space_dict=adjacent_space_dict,
                    space_type_name_dict=ifc_geometry.space_type_name_dict,
                    name=project_name)
graph.generate_graph()