from pathlib import Path
import ifcopenshell
import ifcopenshell.geom
import os
import Ifc2Graph.IfcGeometry as IfcGeometry
import Ifc2Graph.Graph as Graph

path = str(Path(__file__).parent)
project_name = "test"
ifc_file_name = "test.ifc"
ifc_file_path = os.path.join(path, "test", ifc_file_name)

ifc_file = ifcopenshell.open(ifc_file_path)

ifc_geometry = IfcGeometry.IfcGeometry(ifc_file, project_name, force_init=True)
adjacent_space_dict = ifc_geometry.get_adjacent_spaces()

graph = Graph.Graph(adjacent_space_dict=adjacent_space_dict,
                    space_type_name_dict=ifc_geometry.space_type_name_dict,
                    name=project_name)

graph.generate_graph()