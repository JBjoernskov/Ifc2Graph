import networkx as nx
import os
import shutil
import subprocess


class IfcGraph(nx.Graph):

    def __init__(self,
                adjacent_spaces_dict=None,
                space_type_name_dict=None,
                name_to_type_dict=None,
                space_storey_dict = None,
                graph_name=None):
        self.adjacent_spaces_dict = adjacent_spaces_dict
        self.space_type_name_dict = space_type_name_dict
        self.name_to_type_dict = name_to_type_dict
        self.space_storey_dict = space_storey_dict
        self.graph_name = graph_name

        # This is a color list for the building stories
        self.color_list = ["#808B96", "#e99d4e", "#a6cee3", "#b2df8a", "#fddbd0", "#91998e"] #Last is default
        super().__init__()

    def generate(self, save_dir=None):
        graph_node_attribute_dict = {}

        for space_name,adjacent_spaces_list in self.adjacent_spaces_dict.items():
            story_space_idx = self.space_storey_dict[space_name]
            for adjacent_space in adjacent_spaces_list:
                if adjacent_space is not "Outside":
                    story_adjacent_idx = self.space_storey_dict[adjacent_space]
                    if story_space_idx!=story_adjacent_idx:
                        story_idx = len(self.color_list)-1
                    else:
                        story_idx = story_space_idx
                    
                    self.add_edge(adjacent_space, space_name, color=self.color_list[story_idx])
                    if self.space_type_name_dict is not None and self.name_to_type_dict is not None:
                        if self.space_type_name_dict[adjacent_space] in self.name_to_type_dict:
                            graph_node_attribute_dict[adjacent_space] = {"label": self.name_to_type_dict[self.space_type_name_dict[adjacent_space]]}
                        else:
                            graph_node_attribute_dict[adjacent_space] = {"label": self.space_type_name_dict[adjacent_space]}

                        if self.space_type_name_dict[space_name] in self.name_to_type_dict:
                            graph_node_attribute_dict[space_name] = {"label": self.name_to_type_dict[self.space_type_name_dict[space_name]]}
                        else:
                            graph_node_attribute_dict[space_name] = {"label": self.space_type_name_dict[space_name]}
        min_fontsize = 35
        max_fontsize = 35

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

            story_idx = self.space_storey_dict[node]
            

            if node not in graph_node_attribute_dict:
                graph_node_attribute_dict[node] = {"fontsize":fontsize, "width":width, "height":width, "color":self.color_list[story_idx]}
            else:
                graph_node_attribute_dict[node]["fontsize"] = fontsize
                graph_node_attribute_dict[node]["width"] = width
                graph_node_attribute_dict[node]["height"] = width
                graph_node_attribute_dict[node]["color"] = self.color_list[story_idx]


        nx.set_node_attributes(self, graph_node_attribute_dict)
        nx.set_node_attributes(self, values="Helvetica", name="fontname")
        nx.set_edge_attributes(self, values=5, name="penwidth")
        # nx.set_node_attributes(self, values=10, name="fontsize")


        print("Drawing graph...")
        if save_dir is None:
            file_name = "adjacent_rooms_graph_" + self.graph_name
        else:
            file_name = os.path.join(save_dir, "adjacent_rooms_graph_" + self.graph_name)


        nx.drawing.nx_pydot.write_dot(self, file_name+".dot")

        # If Python can't find the dot executeable, change "app_path" variable to the full path
        app_path = shutil.which("dot")
        args = [app_path,
                "-Tpng",
                "-Ksfdp",
                "-Nstyle=filled",
                "-Nfixedsize=true",
                "-Grankdir=LR",
                "-Goverlap=scale",
                "-Gsplines=true",
                "-Gmargin=0",
                "-Gratio=fill",
                "-Gsize=7,5!",
                "-Gpack=true",
                "-Gdpi=1000",
                "-Grepulsiveforce=10",
                "-o" + file_name + ".png",
                file_name + ".dot"]

        subprocess.run(args=args)

        cwd = os.getcwd()
        print("Generated graph can be found in directory: \"" + cwd + "\"")
