

#misc non-standard libraries
import ifcopenshell
import ifcopenshell.geom
import numpy as np
import matplotlib.pyplot as plt
import itertools

#custom
import progressbar

#standard
import math
import os
import time
import pickle

#geometry
import trimesh

# plotting
from mayavi import mlab

class TimeCheckpoint:
    def __init__(self,checkpoint_name):
        self.start_time = time.time()
        self.checkpoint_name = checkpoint_name

    def print_elapsed_time(self):
        total_elapsed_secs = time.time()-self.start_time
        h = math.floor(total_elapsed_secs/3600)
        m = math.floor((total_elapsed_secs-h*3600)/60)
        s = math.floor((total_elapsed_secs-h*3600-m*60))
        str1 = "\"%s\" elapsed time: %dh %dm %ds" % (self.checkpoint_name,h,m,s)
        print(str1)

class SpaceMap:
    def __init__(self,space_mesh_list,space_name_list, space_type_name_dict, space_mesh_neutral_list, space_name_neutral_list, conv_block_size, tol):
        self.space_mesh_list = space_mesh_list
        self.space_name_list = space_name_list
        self.space_type_name_dict = space_type_name_dict

        self.space_mesh_neutral_list = space_mesh_neutral_list
        self.space_name_neutral_list = space_name_neutral_list
        
        self.conv_block_size = conv_block_size
        self.tol = tol

        self.conv_input_x_size = None
        self.conv_input_y_size = None
        self.conv_input_z_size = None
        

        self.voxel_x_location_vec = None
        self.voxel_y_location_vec = None
        self.voxel_z_location_vec = None

        self.conv_input_shape = None

        self.space_idx_dict = {}

        self.neutral_idx = -50
        self.ambient_idx = -100

        self.init_3D_space_idx_list()


    def init_3D_space_idx_list(self):
        

        conv_min_x_list = []
        conv_min_y_list = []
        conv_min_z_list = []
        
        conv_max_x_list = []
        conv_max_y_list = []
        conv_max_z_list = []


        for space_mesh in self.space_mesh_list:
            conv_min_x_list.append(np.min(space_mesh.vertices[:,0]))
            conv_min_y_list.append(np.min(space_mesh.vertices[:,1]))
            conv_min_z_list.append(np.min(space_mesh.vertices[:,2]))

            conv_max_x_list.append(np.max(space_mesh.vertices[:,0]))
            conv_max_y_list.append(np.max(space_mesh.vertices[:,1]))
            conv_max_z_list.append(np.max(space_mesh.vertices[:,2]))

        for space_mesh in self.space_mesh_neutral_list:
            conv_min_x_list.append(np.min(space_mesh.vertices[:,0]))
            conv_min_y_list.append(np.min(space_mesh.vertices[:,1]))
            conv_min_z_list.append(np.min(space_mesh.vertices[:,2]))

            conv_max_x_list.append(np.max(space_mesh.vertices[:,0]))
            conv_max_y_list.append(np.max(space_mesh.vertices[:,1]))
            conv_max_z_list.append(np.max(space_mesh.vertices[:,2]))

            
        conv_min_x = np.min(np.array(conv_min_x_list))
        conv_min_y = np.min(np.array(conv_min_y_list))
        conv_min_z = np.min(np.array(conv_min_z_list))

        conv_max_x = np.max(np.array(conv_max_x_list))
        conv_max_y = np.max(np.array(conv_max_y_list))
        conv_max_z = np.max(np.array(conv_max_z_list))

        self.conv_input_x_size = math.floor((conv_max_x-conv_min_x)/self.conv_block_size)+2
        self.conv_input_y_size = math.floor((conv_max_y-conv_min_y)/self.conv_block_size)+2
        self.conv_input_z_size = math.floor((conv_max_z-conv_min_z)/self.conv_block_size)+2

        conv_input_x_rem = (conv_max_x-conv_min_x)-self.conv_input_x_size*self.conv_block_size
        conv_input_z_rem = (conv_max_y-conv_min_y)-self.conv_input_y_size*self.conv_block_size
        conv_input_y_rem = (conv_max_z-conv_min_z)-self.conv_input_z_size*self.conv_block_size

        conv_input_min_x = conv_min_x+conv_input_x_rem*0.5 - self.conv_block_size #add additional outdoor block
        conv_input_min_y = conv_min_y+conv_input_y_rem*0.5 - self.conv_block_size #add additional outdoor block
        conv_input_min_z = conv_min_z+conv_input_z_rem*0.5 - self.conv_block_size #add additional outdoor block

        conv_input_max_x = conv_max_x-conv_input_x_rem*0.5 + self.conv_block_size #add additional outdoor block
        conv_input_max_y = conv_max_y-conv_input_y_rem*0.5 + self.conv_block_size #add additional outdoor block
        conv_input_max_z = conv_max_z-conv_input_z_rem*0.5 + self.conv_block_size #add additional outdoor block


        voxel_x_idx_vec = np.arange(self.conv_input_x_size) #(conv_input_x_size)
        voxel_y_idx_vec = np.arange(self.conv_input_y_size) #(conv_input_y_size)
        voxel_z_idx_vec = np.arange(self.conv_input_z_size) #(conv_input_z_size)

        self.voxel_x_location_vec = np.linspace(conv_input_min_x,conv_input_max_x,self.conv_input_x_size) #(conv_input_x_size)
        self.voxel_y_location_vec = np.linspace(conv_input_min_y,conv_input_max_y,self.conv_input_y_size) #(conv_input_y_size)
        self.voxel_z_location_vec = np.linspace(conv_input_min_z,conv_input_max_z,self.conv_input_z_size) #(conv_input_z_size)


        voxel_x_idx_mesh,voxel_y_idx_mesh,voxel_z_idx_mesh = np.meshgrid(voxel_x_idx_vec,voxel_y_idx_vec,voxel_z_idx_vec)
        voxel_x_location_mesh,voxel_y_location_mesh,voxel_z_location_mesh = np.meshgrid(self.voxel_x_location_vec,self.voxel_y_location_vec,self.voxel_z_location_vec)


        idx_mesh = np.swapaxes(np.array([voxel_x_idx_mesh,voxel_y_idx_mesh,voxel_z_idx_mesh]),0,3) #(conv_input_x_size,conv_input_y_size,conv_input_z_size,3)
        location_mesh = np.swapaxes(np.array([voxel_x_location_mesh,voxel_y_location_mesh,voxel_z_location_mesh]),0,3) #(conv_input_x_size,conv_input_y_size,conv_input_z_size)

        idx_mesh_vec = np.reshape(idx_mesh,(idx_mesh.shape[0]*idx_mesh.shape[1]*idx_mesh.shape[2],idx_mesh.shape[3]))
        location_mesh_vec = np.reshape(location_mesh,(location_mesh.shape[0]*location_mesh.shape[1]*location_mesh.shape[2],location_mesh.shape[3]))

        print("Generating space to position index map...")
        self.conv_input_shape = (self.conv_input_x_size,self.conv_input_y_size,self.conv_input_z_size)
        self._3D_space_idx_list = np.ones(self.conv_input_shape,dtype=np.int)*self.ambient_idx

        #Set indices for neutral space
        for space_counter,space_mesh in enumerate(self.space_mesh_neutral_list):
            bool_vec = space_mesh.contains(location_mesh_vec)

            x_idx = idx_mesh_vec[bool_vec,0]
            y_idx = idx_mesh_vec[bool_vec,1]
            z_idx = idx_mesh_vec[bool_vec,2]

            self._3D_space_idx_list[x_idx,y_idx,z_idx] = self.neutral_idx

            progressbar.progressbar(space_counter,0,len(self.space_mesh_neutral_list))
        print("")

        #Set indices for normal space
        for space_counter,space_mesh in enumerate(self.space_mesh_list):
            bool_vec = space_mesh.contains(location_mesh_vec)

            x_idx = idx_mesh_vec[bool_vec,0]
            y_idx = idx_mesh_vec[bool_vec,1]
            z_idx = idx_mesh_vec[bool_vec,2]

            self._3D_space_idx_list[x_idx,y_idx,z_idx] = space_counter
            self.space_idx_dict[self.space_name_list[space_counter]] = space_counter

            progressbar.progressbar(space_counter,0,len(self.space_mesh_list))
        print("")
            

    def get_point_space_idx(self,x_idx,y_idx,z_idx):
        return self._3D_space_idx_list[x_idx,y_idx,z_idx]

    def get_NN_3D_input(self,value_space_list,value_neutral,value_ground,value_ambient_air):
        NN_3D_temp_input = np.zeros(self.conv_input_shape,dtype=np.float)

        neutral_mask = self._3D_space_idx_list==self.neutral_idx
        outside_mask = self._3D_space_idx_list==self.ambient_idx
        below_zero_mask = np.zeros(self.conv_input_shape,dtype=np.bool)
        below_zero_mask[:,:,self.voxel_z_location_vec<0] = True
        ground_mask = np.logical_and(outside_mask,below_zero_mask)


        NN_3D_temp_input[neutral_mask] = value_neutral
        NN_3D_temp_input[outside_mask] = value_ambient_air
        NN_3D_temp_input[ground_mask] = value_ground
        

        for space_counter,value in enumerate(value_space_list):
            NN_3D_temp_input[self._3D_space_idx_list==space_counter] = value

        # NN_3D_temp_input[below_zero_mask==False] = value_ground

        return NN_3D_temp_input

    def get_adjacent_spaces(self):
        x_bool = np.equal(self._3D_space_idx_list[:-1,:,:], self._3D_space_idx_list[1:,:,:]) == False
        y_bool = (self._3D_space_idx_list[:,:-1,:] == self._3D_space_idx_list[:,1:,:]) == False
        z_bool = (self._3D_space_idx_list[:,:,:-1] == self._3D_space_idx_list[:,:,1:]) == False


        dx_idx_space_1_x, dx_idx_space_1_y, dx_idx_space_1_z = np.where(x_bool)
        dy_idx_space_1_x, dy_idx_space_1_y, dy_idx_space_1_z = np.where(y_bool)
        dz_idx_space_1_x, dz_idx_space_1_y, dz_idx_space_1_z = np.where(z_bool)

        dx_idx_space_2_x = dx_idx_space_1_x+1 
        dy_idx_space_2_x = dy_idx_space_1_x
        dz_idx_space_2_x = dz_idx_space_1_x

        dx_idx_space_2_y = dx_idx_space_1_y
        dy_idx_space_2_y = dy_idx_space_1_y+1
        dz_idx_space_2_y = dz_idx_space_1_y

        dx_idx_space_2_z = dx_idx_space_1_z
        dy_idx_space_2_z = dy_idx_space_1_z
        dz_idx_space_2_z = dz_idx_space_1_z+1

        dx_idx_pair_1 = self._3D_space_idx_list[dx_idx_space_1_x, dx_idx_space_1_y, dx_idx_space_1_z]
        dx_idx_pair_2 = self._3D_space_idx_list[dx_idx_space_2_x, dx_idx_space_2_y, dx_idx_space_2_z]
        dy_idx_pair_1 = self._3D_space_idx_list[dy_idx_space_1_x, dy_idx_space_1_y, dy_idx_space_1_z]
        dy_idx_pair_2 = self._3D_space_idx_list[dy_idx_space_2_x, dy_idx_space_2_y, dy_idx_space_2_z]
        dz_idx_pair_1 = self._3D_space_idx_list[dz_idx_space_1_x, dz_idx_space_1_y, dz_idx_space_1_z]
        dz_idx_pair_2 = self._3D_space_idx_list[dz_idx_space_2_x, dz_idx_space_2_y, dz_idx_space_2_z]
        
        # For each point in the generated mesh, it is checked which space the adjacent point is encapsulated by. 
        # If the adjacent point does not belong to a space, the subsequent point is checked. 
        # This is done up until "n_search_blocks" away from the original point. 
        n_search_blocks = 4
        for i in range(n_search_blocks):
            dx_temp = dx_idx_space_2_x+i+1
            dx_temp[dx_temp>=self.conv_input_shape[0]] = dx_idx_space_2_x[dx_temp>=self.conv_input_shape[0]]
            temp = self._3D_space_idx_list[dx_temp, dx_idx_space_2_y, dx_idx_space_2_z] ###     If +1 point is not a room then check +2 point
            bool_dx = np.logical_or(dx_idx_pair_2 == self.neutral_idx, dx_idx_pair_2 == self.ambient_idx) ###
            dx_idx_pair_2[bool_dx] = temp[bool_dx] ###


            dy_temp = dy_idx_space_2_y+i+1
            dy_temp[dy_temp>=self.conv_input_shape[1]] = dy_idx_space_2_y[dy_temp>=self.conv_input_shape[1]]
            temp = self._3D_space_idx_list[dy_idx_space_2_x, dy_temp, dy_idx_space_2_z] ###
            bool_dy = np.logical_or(dy_idx_pair_2 == self.neutral_idx, dy_idx_pair_2 == self.ambient_idx) ###
            dy_idx_pair_2[bool_dy] = temp[bool_dy] ###


            dz_temp = dz_idx_space_2_z+i+1
            dz_temp[dz_temp>=self.conv_input_shape[2]] = dz_idx_space_2_z[dz_temp>=self.conv_input_shape[2]]
            temp = self._3D_space_idx_list[dz_idx_space_2_x, dz_idx_space_2_y, dz_temp] ###
            bool_dz = np.logical_or(dz_idx_pair_2 == self.neutral_idx, dz_idx_pair_2 == self.ambient_idx) ###
            dz_idx_pair_2[bool_dz] = temp[bool_dz] ###



        dx_idx_pair = np.array([dx_idx_pair_1,dx_idx_pair_2])
        dy_idx_pair = np.array([dy_idx_pair_1,dy_idx_pair_2])
        dz_idx_pair = np.array([dz_idx_pair_1,dz_idx_pair_2])


        

        dx_pair_list = []
        while True:
            dx_pair_list.append(dx_idx_pair[:,0])
            is_equal_bool = np.equal(dx_idx_pair[:,0].reshape((2,1)), dx_idx_pair)
            is_equal_bool = np.logical_and(is_equal_bool[0],is_equal_bool[1])

            if np.all(is_equal_bool):
                break
            else:
                dx_idx_pair = dx_idx_pair[:,is_equal_bool==False]

        dy_pair_list = []
        while True:
            dy_pair_list.append(dy_idx_pair[:,0])
            is_equal_bool = np.equal(dy_idx_pair[:,0].reshape((2,1)), dy_idx_pair)
            is_equal_bool = np.logical_and(is_equal_bool[0],is_equal_bool[1])

            if np.all(is_equal_bool):
                break
            else:
                dy_idx_pair = dy_idx_pair[:,is_equal_bool==False]

        dz_pair_list = []
        while True:
            dz_pair_list.append(dz_idx_pair[:,0])
            is_equal_bool = np.equal(dz_idx_pair[:,0].reshape((2,1)), dz_idx_pair)
            is_equal_bool = np.logical_and(is_equal_bool[0],is_equal_bool[1])

            if np.all(is_equal_bool):
                break
            else:
                dz_idx_pair = dz_idx_pair[:,is_equal_bool==False]

        pair_list = []
        pair_list.extend(dx_pair_list)
        pair_list.extend(dy_pair_list)
        pair_list.extend(dz_pair_list)

        pair_vec = np.array(pair_list).transpose()

        bool_no_self_reference = pair_vec[0,:] != pair_vec[1,:]
        pair_vec = pair_vec[:,bool_no_self_reference]
        pair_list_no_duplicates = []
        while True:
            pair_1 = pair_vec[:,0]
            pair_2 = np.array([pair_vec[1,0],pair_vec[0,0]])
            pair_list_no_duplicates.append(pair_1)

            is_equal_bool_1 = np.equal(pair_1.reshape((2,1)), pair_vec)
            is_equal_bool_1 = np.logical_and(is_equal_bool_1[0],is_equal_bool_1[1])

            is_equal_bool_2 = np.equal(pair_2.reshape((2,1)), pair_vec)
            is_equal_bool_2 = np.logical_and(is_equal_bool_2[0],is_equal_bool_2[1])

            is_equal_bool = np.logical_or(is_equal_bool_1, is_equal_bool_2)

            if np.all(is_equal_bool):
                break
            else:
                pair_vec = pair_vec[:,is_equal_bool==False]


        adjacent_space_dict = {}
        pair_vec_no_duplicates = np.array(pair_list_no_duplicates).transpose()
        for space_counter,space_name in enumerate(self.space_name_list):
            bool_1 = space_counter == pair_vec_no_duplicates[0,:]
            bool_2 = space_counter == pair_vec_no_duplicates[1,:]

            idx_vec_1 = pair_vec_no_duplicates[1,bool_1]
            idx_vec_2 = pair_vec_no_duplicates[0,bool_2]

            adjacent_space_list = []
            for el in idx_vec_1:
                if el != -50 and el != -100:
                    adjacent_space_list.append(self.space_name_list[el])
                elif el == -100:
                    adjacent_space_list.append("Outside")
            for el in idx_vec_2:
                if el != -50 and el != -100:
                    adjacent_space_list.append(self.space_name_list[el])
                elif el == -100:
                    adjacent_space_list.append("Outside")
            adjacent_space_dict[space_name] = adjacent_space_list

        ####### IF duplicate space names occur in the IFC and these spaces are adjacent then the resulting adjacent_space_dict will have elements that reference themselves #########

        return adjacent_space_dict



def get_space_map(ifc_file,space_map_name,force,exclude_space_list,no_sensor_room_list,conv_block_size):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    space_map_filename = current_dir + "/" + "space_map_" + space_map_name + ".pickle"
    if force or os.path.isfile(space_map_filename) == False:


        # ifc_file_path = folder_path + ifc_file_name + ".ifc"
        # ifc_file = ifcopenshell.open(ifc_file_path)
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)


        id_iter = itertools.count()


        print("Extracting geometry from ifc...")
        neutral_space_name = "Area" #spaces that doesnt classify as a room but is a part of the building
        ifc_space_list = ifc_file.by_type("IfcSpace")
        if len(ifc_space_list)==0:
            print("Ifc-file does not contain any space objects -> quitting...")
            quit = True
        else:
            space_name_list = []
            space_mesh_list = []
            space_type_name_dict = {}
            space_name_neutral_list = []
            space_mesh_neutral_list = []
            for i,space in enumerate(ifc_space_list):
                shape = ifcopenshell.geom.create_shape(settings, space)
                vertices = shape.geometry.verts
                edges = shape.geometry.edges
                faces = shape.geometry.faces

                if space.Name is None: #If the space has no name, give it a generic name 
                    space.Name = "Space_" + str(next(id_iter))

                grouped_vertices = np.array([[vertices[i], vertices[i + 1], vertices[i + 2]] for i in range(0, len(vertices), 3)])
                grouped_edges = np.array([[edges[i], edges[i + 1]] for i in range(0, len(edges), 2)])
                grouped_faces = np.array([[faces[i], faces[i + 1], faces[i + 2]] for i in range(0, len(faces), 3)])

                mesh = trimesh.Trimesh(vertices=grouped_vertices,
                            faces=grouped_faces)

                red_rgb = np.array([220,20,60],dtype=np.uint8)
                blue_rgb = np.array([70,130,180],dtype=np.uint8)
                
                if (space.Name in exclude_space_list)==False: ##########################
                    
                    if space.LongName == neutral_space_name or space.Name in no_sensor_room_list:
                        random_color = False

                        if False:#space.Name.find("Ø28-509b-3")!=-1:
                            for facet in mesh.facets:
                                mesh.visual.face_colors[facet] = trimesh.visual.to_rgba(red_rgb)
                        else:
                            if random_color:
                                color = trimesh.visual.random_color()
                                for facet in mesh.facets:
                                    mesh.visual.face_colors[facet] = color
                            else:
                                for facet in mesh.facets:
                                    mesh.visual.face_colors[facet] = trimesh.visual.to_rgba(red_rgb)

                        
                        space_name_neutral_list.append(space.Name)
                        space_mesh_neutral_list.append(mesh)

                    else:
                        # random_color = False
                        # if space.Name.find("06.01.031")!=-1:
                        #     for facet in mesh.facets:
                        #         mesh.visual.face_colors[facet] = trimesh.visual.to_rgba(red_rgb)
                        # else:
                        #     if random_color:
                        #         color = trimesh.visual.random_color()
                        #         for facet in mesh.facets:
                        #             mesh.visual.face_colors[facet] = color
                        #     else:
                        #         for facet in mesh.facets:
                        #             mesh.visual.face_colors[facet] = trimesh.visual.to_rgba(blue_rgb)

                        space_name_list.append(space.Name)
                        space_mesh_list.append(mesh)
                        space_type_name_dict[space.Name] = space.LongName

                progressbar.progressbar(i,0,len(ifc_space_list))
            print("")
            

                
            # trimesh.Scene(space_mesh_list).show()

            #Check for duplicate room names
            if len(set(space_name_list)) != len(space_name_list):
                print("Warning: duplicate space names found in IFC.")


            tol = 1e-4
            space_map = SpaceMap(space_mesh_list,
                                space_name_list, 
                                space_type_name_dict,
                                space_mesh_neutral_list,
                                space_name_neutral_list,
                                conv_block_size,
                                tol)


            filehandler = open(space_map_filename, 'wb') 
            pickle.dump(space_map, filehandler)
        
    else:
        filehandler = open(space_map_filename, 'rb') 
        space_map = pickle.load(filehandler)


        ########################################
        # value_space_list = []
        # for space_name in space_map.space_name_list:
        #     # print(space_name)
        #     if False:#space_name == "06.99.031":
        #         value_space_list.append(1)
        #     else:
        #         value_space_list.append(0)

        # NN_3D_temp_input = space_map.get_NN_3D_input(value_space_list,0,np.nan,np.nan)


        # print("Plotting...")
        # mesh = np.meshgrid(space_map.voxel_x_location_vec, space_map.voxel_y_location_vec, space_map.voxel_z_location_vec,indexing='ij')
        # t1 = TimeCheckpoint("fig")
        # fig  = mlab.figure()
        # g1 = mlab.points3d(mesh[0], mesh[1], mesh[2], NN_3D_temp_input, scale_factor=0.03, mode='point', transparent=False,figure=fig, vmin=0, vmax=1)
        # g1.actor.property.render_points_as_spheres = True
        # g1.actor.property.point_size = 20
        # mlab.show()
        ##################################################

    return space_map






















# settings.set(settings.SITE_LOCAL_PLACEMENT, True)
# settings.set(settings.BUILDING_LOCAL_PLACEMENT, True)

# project = ifc_file.by_type('IfcProject')[0]
# site = ifc_file.by_type('IfcSite')[0]
# print("Modifying ObjectPlacement...")
# placement = site.ObjectPlacement.RelativePlacement

# for RC in project.RepresentationContexts:

#     print(RC.TrueNorth.DirectionRatios)
#     print(RC.WorldCoordinateSystem.Location.Coordinates)
    

#     RC.TrueNorth.DirectionRatios = (1., 0.) # Z
#     RC.WorldCoordinateSystem.Location.Coordinates = (0., 0., 0.)






# placement.Axis.DirectionRatios = (0., 0., 1.) # Z
# placement.RefDirection.DirectionRatios = (1., 0., 0.) # X
# placement.Location.Coordinates = (0., 0., 0.) # origo






# p = Patcher(None, ifc_file, logging.getLogger('IFCPatch'), args = [0,0,0,0])
# p.patch()



# print("Writing to new ifc file...")
# ifc_file_name_new = ifc_file_name + "_corrected"
# ifc_file_path_new = folder_path + ifc_file_name_new + ".ifc"
# ifc_file.write(ifc_file_path_new)




# fig = plt.figure()
# ax = fig.add_subplot(projection='3d')