import networkx as nx
import os


class IfcGraph(nx.Graph):

    def __init__(self,
                adjacent_space_dict=None,
                space_type_name_dict=None,
                name_to_type_dict=None,
                graph_name=None):
        self.adjacent_space_dict = adjacent_space_dict
        self.space_type_name_dict = space_type_name_dict
        self.name_to_type_dict = name_to_type_dict
        self.graph_name = graph_name
        super().__init__()

    # Currently there is no general method to find the story level.
    # This is based on the Name property of the IfcSpace entities and is only valid for the example office building.
    def get_story(self, space):
        name = str(space)
        story_idx = int(space[0])
        return story_idx 

    def generate_graph(self, save_dir=None):
        adjacent_rooms_graph = nx.Graph() ###
        graph_node_attribute_dict = {}

        # This is a color list for the building stories
        color_list = ["#808B96", "#e99d4e", "#a6cee3", "#b2df8a", "#fddbd0", "#91998e"] #Last is default

        for space,adjacent_space_list in self.adjacent_space_dict.items():
            story_space_idx = self.get_story(space)
            for adjacent_space in adjacent_space_list:
                if adjacent_space is not "Outside":
                    story_adjacent_idx = self.get_story(adjacent_space)
                    if story_space_idx!=story_adjacent_idx:
                        story_idx = len(color_list)-1
                    else:
                        story_idx = story_space_idx
                    
                    self.add_edge(adjacent_space, space, color=color_list[story_idx])
                    if self.space_type_name_dict is not None and self.name_to_type_dict is not None:
                        if self.space_type_name_dict[adjacent_space] in self.name_to_type_dict:
                            graph_node_attribute_dict[adjacent_space] = {"label": self.name_to_type_dict[self.space_type_name_dict[adjacent_space]]}
                        else:
                            graph_node_attribute_dict[adjacent_space] = {"label": self.space_type_name_dict[adjacent_space]}

                        if self.space_type_name_dict[space] in self.name_to_type_dict:
                            graph_node_attribute_dict[space] = {"label": self.name_to_type_dict[self.space_type_name_dict[space]]}
                        else:
                            graph_node_attribute_dict[space] = {"label": self.space_type_name_dict[space]}
        min_fontsize = 25
        max_fontsize = 25

        min_width = 1
        max_width = 4

        degree_list = [self.degree(node) for node in self.nodes]
        min_deg = min(degree_list)
        max_deg = max(degree_list)

        a_fontsize = (max_fontsize-min_fontsize)/(max_deg-min_deg)
        b_fontsize = max_fontsize-a_fontsize*max_deg

        a_width = (max_width-min_width)/(max_deg-min_deg)
        b_width = max_width-a_width*max_deg
        for node in self.nodes:
            deg = self.degree(node)
            fontsize = a_fontsize*deg + b_fontsize
            width = a_width*deg + b_width        


            story_idx = self.get_story(node)
            

            if node not in graph_node_attribute_dict:
                graph_node_attribute_dict[node] = {"fontsize": fontsize, "width": width, "color": color_list[story_idx]}
            else:
                graph_node_attribute_dict[node]["fontsize"] = fontsize
                graph_node_attribute_dict[node]["width"] = width
                graph_node_attribute_dict[node]["color"] = color_list[story_idx]


        nx.set_node_attributes(self, values=graph_node_attribute_dict)
        nx.set_node_attributes(self, values="Helvetica", name="fontname")
        nx.set_node_attributes(self, values=5, name="penwidth")
        nx.set_node_attributes(self, values=10, name="fontsize")

        print("Drawing graph...")
        if save_dir is None:
            file_name = "adjacent_rooms_graph_" + self.name
        else:
            file_name = os.path.join(save_dir, "adjacent_rooms_graph_" + self.name)

        nx.drawing.nx_pydot.write_dot(adjacent_rooms_graph, file_name+".dot")
        cmd_string = "\"C:/Program Files/Graphviz/bin/dot.exe\" -Tpng -Ksfdp -Grankdir=LR -Goverlap=scale -Gsplines=true -Gmargin=0 -Gratio=fill -Gsize=7,5! -Gpack=true -Gdpi=1000 -Grepulsiveforce=1 -o " + file_name+".png " + file_name+".dot"
        os.system(cmd_string)