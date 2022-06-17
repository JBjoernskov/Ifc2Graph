

import ifcopenshell
import ifcopenshell.geom


import numpy as np
import extract_geometry_from_ifc

import pprint
import networkx as nx
import os

def get_story(name):
    _1st_color_identifier_list = ["-00","ØØØØØ","-01","-02"]
    _2nd_color_identifier_list = ["ØØØØØ","-0","-1","-2"]

    # _1st_color_identifier_list = [".99",".00",".01"]
    # _2nd_color_identifier_list = ["-0","-1","-2"]
    
    
    bool_vec = np.array([name.find(color_identifier)!=-1 for color_identifier in _1st_color_identifier_list])
    temp = np.where(bool_vec)[0]
    if temp.size!=0:
        story_idx = temp[0]
    else:
        bool_vec = np.array([name.find(color_identifier)!=-1 for color_identifier in _2nd_color_identifier_list])
        temp = np.where(bool_vec)[0]
        if temp.size!=0:
            story_idx = temp[0]
        else:
            story_idx = 3

    return story_idx



def generate_adjacent_rooms_graph(adjecent_space_dict, space_type_name_dict, project_name):
    adjacent_rooms_graph = nx.Graph() ###
    adjacent_rooms_graph_node_attribute_dict = {}

    color_list = ["#808B96", "#e99d4e", "#a6cee3", "#b2df8a", "#91998e"] #Last is default

    danish_english_dictionary = {
        "Gang": "Corridor", #OU44####################
        "Teknikrum": "Technical room",
        "Undervisningsrum": "Teaching room",
        "Printerrum": "Printing room",
        "Kontor": "Office",
        "Foyer": "Foyer",
        "Auditorie": "Auditorium",
        "Forrum": "Anteroom",
        "Læse- og opholdsrum": "Study room",
        "Thekøkken": "Kitchenette",
        "Trappe": "Stairs",
        "Depotrum": "Storage",
        "Toilet": "Toilet",
        "Elevator": "Elevator",
        "Handicap toilet": "Toilet",
        "Rengøringsrum": "Cleaning equipment room",
        "Bad": "Shower",
        "Mødelokale": "Meeting room", #OU44################
        "Fælles adgangsveje": "Common corridor", #Dokk1#################
        "Brandtrappe": "Fire escape",
        "Teknik": "Technical room",
        "P-område under tag": "Parking",
        "MMH": "MMH",
        "P-anlæg": "Parking",
        "Wc": "Toilet",
        "Omkl.": "Changing room",
        "HC wc": "Toilet",
        "MMH logistikområde": "MMH logistic area",
        "Udvendige elevator": "External elevator",
        "Elevator til niveau 1": "Elevator to level 1",
        "Udvendig elevator": "External elevator",
        "Areal under tag": "Area under roof",
        "Selvaflevering": "Selvaflevering" #Dokk1 ##############
    }

    
    
    #Orange, Grey, Blue


    for space,adjacent_space_list in adjecent_space_dict.items():
        space = space.replace("Ø","OE")

        story_space_idx = get_story(space)
        for adjacent_space in adjacent_space_list:
            if adjacent_space is not "Outside":
                story_adjacent_idx = get_story(adjacent_space)
                if story_space_idx!=story_adjacent_idx:
                    story_idx = len(color_list)-1
                else:
                    story_idx = story_space_idx
                


                adjacent_space = adjacent_space.replace("Ø","OE")
                adjacent_rooms_graph.add_edge(adjacent_space, space, color=color_list[story_idx])

                # if space_type_name_dict[adjacent_space.replace("OE","Ø")] in danish_english_dictionary:
                #     adjacent_rooms_graph_node_attribute_dict[adjacent_space] = {"label": danish_english_dictionary[space_type_name_dict[adjacent_space.replace("OE","Ø")]]}
                # else:
                #     adjacent_rooms_graph_node_attribute_dict[adjacent_space] = {"label": space_type_name_dict[adjacent_space.replace("OE","Ø")]}

                # if space_type_name_dict[space.replace("OE","Ø")] in danish_english_dictionary:
                #     adjacent_rooms_graph_node_attribute_dict[space] = {"label": danish_english_dictionary[space_type_name_dict[space.replace("OE","Ø")]]}
                # else:
                #     adjacent_rooms_graph_node_attribute_dict[space] = {"label": space_type_name_dict[space.replace("OE","Ø")]}


    min_fontsize = 25
    max_fontsize = 25

    

    min_width = 1
    max_width = 4

    degree_list = [adjacent_rooms_graph.degree(node) for node in adjacent_rooms_graph.nodes]
    min_deg = min(degree_list)
    max_deg = max(degree_list)

    a_fontsize = (max_fontsize-min_fontsize)/(max_deg-min_deg)
    b_fontsize = max_fontsize-a_fontsize*max_deg

    a_width = (max_width-min_width)/(max_deg-min_deg)
    b_width = max_width-a_width*max_deg
    for node in adjacent_rooms_graph.nodes:
        deg = adjacent_rooms_graph.degree(node)
        fontsize = a_fontsize*deg + b_fontsize
        width = a_width*deg + b_width        


        story_idx = get_story(node)
        

        if node not in adjacent_rooms_graph_node_attribute_dict:
            adjacent_rooms_graph_node_attribute_dict[node] = {"fontsize": fontsize, "width": width, "color": color_list[story_idx]}
        else:
            adjacent_rooms_graph_node_attribute_dict[node]["fontsize"] = fontsize
            adjacent_rooms_graph_node_attribute_dict[node]["width"] = width
            adjacent_rooms_graph_node_attribute_dict[node]["color"] = color_list[story_idx]


    nx.set_node_attributes(adjacent_rooms_graph, values=adjacent_rooms_graph_node_attribute_dict)

    graph = nx.drawing.nx_pydot.to_pydot(adjacent_rooms_graph)
    graph.set_node_defaults(shape="circle", width=0.8, fixedsize="shape", margin=0, style="filled", fontname="Helvetica", color="#23a6db66", fontsize=10, colorscheme="oranges9")
    graph.set_edge_defaults(fontname="Helvetica", penwidth=5, color="#999999", fontcolor="#999999", fontsize=10, weight=3)

    adjacent_rooms_graph = nx.drawing.nx_pydot.from_pydot(graph)

    print("Drawing graph...")
    file_name = "adjacent_rooms_graph_" + project_name + ".png"
    print(file_name)
    nx.drawing.nx_pydot.write_dot(adjacent_rooms_graph, 'adjacent_rooms_graph.dot')
    cmd_string = "\"C:/Program Files/Graphviz/bin/dot.exe\" -Tpng -Ksfdp -Grankdir=LR -Goverlap=scale -Gsplines=true -Gmargin=0 -Gratio=fill -Gsize=7,5! -Gpack=true -Gdpi=1000 -Grepulsiveforce=10 -o " + file_name + " adjacent_rooms_graph.dot"
    os.system(cmd_string)



def extract_adjacent_rooms_from_ifc(ifc_file, project_name):
    force = False
    conv_block_size = 0.5
    space_map_name = project_name

    no_sensor_room_list = []
    exclude_space_list = []
    space_map = extract_geometry_from_ifc.get_space_map(ifc_file,space_map_name,force,exclude_space_list,no_sensor_room_list,conv_block_size)
    adjacent_space_dict = space_map.get_adjacent_spaces()
    space_type_name_dict = space_map.space_type_name_dict

    print(len(adjacent_space_dict))

    generate_adjacent_rooms_graph(adjacent_space_dict, space_type_name_dict, project_name)

    # pprint.pprint(adjecent_space_dict)

    return adjacent_space_dict

    


# project_name = "OU44"
# folder_path = "C:/Users/jabj/OneDrive - Syddansk Universitet/PhD_Project_Jakob/Twin4build/ifc/OU44_Architecture/"
# ifc_file_name = "SDU-OD_F1_H0_BY_44_EX"
# ifc_file_path = folder_path + ifc_file_name + ".ifc"
# ifc_file = ifcopenshell.open(ifc_file_path)

# adjecent_space_dict = extract_adjacent_rooms_from_ifc(ifc_file, project_name)