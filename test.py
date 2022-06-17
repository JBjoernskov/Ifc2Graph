from pathlib import Path
import ifcopenshell
import ifcopenshell.geom
import Ifc2Graph.extract_adjacent_rooms_from_ifc as extract_adjacent_rooms_from_ifc
import os


path = str(Path(__file__).parent)
project_name = "test"
ifc_file_name = "test.ifc"
ifc_file_path = os.path.join(path, "test", ifc_file_name)

print(ifc_file_path)
ifc_file = ifcopenshell.open(ifc_file_path)
extract_adjacent_rooms_from_ifc.extract_adjacent_rooms_from_ifc(ifc_file, project_name)




