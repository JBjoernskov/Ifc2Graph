import numpy as np
import networkx as nx
import os


class Graph():

    def __init__(self,
                adjacent_space_dict=None,
                space_type_name_dict=None,
                name_to_type_dict=None,
                name=None):
        self.adjacent_space_dict = adjacent_space_dict
        self.space_type_name_dict = space_type_name_dict
        self.name_to_type_dict = name_to_type_dict
        self.name = name

    def get_story(self, space):
        return 0 #Currently there is no general implemented method to find the story level

    def generate_graph(self, save_dir=None):
        adjacent_rooms_graph = nx.Graph() ###
        adjacent_rooms_graph_node_attribute_dict = {}

        color_list = ["#808B96", "#e99d4e", "#a6cee3", "#b2df8a", "#91998e"] #Last is default

        for space,adjacent_space_list in self.adjacent_space_dict.items():
            space = space.replace("Ø","OE")

            story_space_idx = self.get_story(space)
            for adjacent_space in adjacent_space_list:
                if adjacent_space is not "Outside":
                    story_adjacent_idx = self.get_story(adjacent_space)
                    if story_space_idx!=story_adjacent_idx:
                        story_idx = len(color_list)-1
                    else:
                        story_idx = story_space_idx
                    
                    adjacent_space = adjacent_space.replace("Ø","OE")
                    adjacent_rooms_graph.add_edge(adjacent_space, space, color=color_list[story_idx])
                    if self.space_type_name_dict is not None and self.name_to_type_dict is not None:
                        if self.space_type_name_dict[adjacent_space] in self.name_to_type_dict:
                            adjacent_rooms_graph_node_attribute_dict[adjacent_space] = {"label": self.name_to_type_dict[self.space_type_name_dict[adjacent_space]]}
                        else:
                            adjacent_rooms_graph_node_attribute_dict[adjacent_space] = {"label": self.space_type_name_dict[adjacent_space]}

                        if self.space_type_name_dict[space] in self.name_to_type_dict:
                            adjacent_rooms_graph_node_attribute_dict[space] = {"label": self.name_to_type_dict[self.space_type_name_dict[space]]}
                        else:
                            adjacent_rooms_graph_node_attribute_dict[space] = {"label": self.space_type_name_dict[space]}
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


            story_idx = self.get_story(node)
            

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
        if save_dir is None:
            file_name = "adjacent_rooms_graph_" + self.name
        else:
            file_name = os.path.join(save_dir, "adjacent_rooms_graph_" + self.name)
            
        nx.drawing.nx_pydot.write_dot(adjacent_rooms_graph, file_name+".dot")
        cmd_string = "\"C:/Program Files/Graphviz/bin/dot.exe\" -Tpng -Ksfdp -Grankdir=LR -Goverlap=scale -Gsplines=true -Gmargin=0 -Gratio=fill -Gsize=7,5! -Gpack=true -Gdpi=1000 -Grepulsiveforce=10 -o " + file_name+".png " + file_name+".dot"
        os.system(cmd_string)