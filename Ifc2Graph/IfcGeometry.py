#misc non-standard libraries
import ifcopenshell
import ifcopenshell.geom
import numpy as np
import matplotlib.pyplot as plt
import itertools

#custom
import utils.progressbar as progressbar

#standard
import math
import os
import pickle

#geometry
import trimesh

# plotting
from mayavi import mlab



class IfcGeometry:
    def __init__(self, 
                ifc_file=None, #An open ifc-file
                name = None, #Name of the SpaceGeometryContainer
                force_init=False, #Force the creation of a new SpaceGeometryContainer object
                exclude_space_list=[], #List with names of rooms that should not be included 
                voxel_distance=0.5, #Distance between coordiantes along each axis X, Y, Z
                tol=1e-4): #Tolerance used in the geometrical analysis. This should likely just be left at the default value

        self.ifc_file = ifc_file
        self.name = name
        self.force_init = force_init
        self.exclude_space_list = exclude_space_list
        self.voxel_distance = voxel_distance
        self.tol = tol
        self.x_size = None
        self.y_size = None
        self.z_size = None
        self.voxel_x_location_vec = None
        self.voxel_y_location_vec = None
        self.voxel_z_location_vec = None
        self.grid_shape = None
        self.space_idx_dict = {}
        self.neutral_idx = -50
        self.ambient_idx = -100

        self.init_geometry()
        self.init_3D_space_idx_list()

    def init_geometry(self):
        current_dir = os.path.dirname(os.path.realpath(__file__))
        space_map_filename = current_dir + "/" + "space_map_" + self.name + ".pickle"
        if self.force_init or os.path.isfile(space_map_filename) == False:
            settings = ifcopenshell.geom.settings()
            settings.set(settings.USE_WORLD_COORDS, True)
            id_iter = itertools.count()

            print("Extracting geometry from ifc...")
            neutral_space_name = "Area" #spaces that doesnt classify as a room but is a part of the building
            ifc_space_list = self.ifc_file.by_type("IfcSpace")
            if len(ifc_space_list)==0:
                print("Ifc-file does not contain any space objects -> quitting...")
            else:
                self.space_name_list = []
                self.space_mesh_list = []
                self.space_type_name_dict = {}
                self.space_name_neutral_list = []
                self.space_mesh_neutral_list = []
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
                    
                    if (space.Name in self.exclude_space_list)==False:
                        if space.LongName == neutral_space_name:
                            self.space_name_neutral_list.append(space.Name)
                            self.space_mesh_neutral_list.append(mesh)
                        else:
                            self.space_name_list.append(space.Name)
                            self.space_mesh_list.append(mesh)
                            self.space_type_name_dict[space.Name] = space.LongName

                    progressbar.progressbar(i,0,len(ifc_space_list)-1)

                #Check for duplicate room names
                if len(set(self.space_name_list)) != len(self.space_name_list):
                    print("Warning: duplicate space names found in IFC.")


    def init_3D_space_idx_list(self):
        min_x_list = []
        min_y_list = []
        min_z_list = []
        
        max_x_list = []
        max_y_list = []
        max_z_list = []

        for space_mesh in self.space_mesh_list:
            min_x_list.append(np.min(space_mesh.vertices[:,0]))
            min_y_list.append(np.min(space_mesh.vertices[:,1]))
            min_z_list.append(np.min(space_mesh.vertices[:,2]))

            max_x_list.append(np.max(space_mesh.vertices[:,0]))
            max_y_list.append(np.max(space_mesh.vertices[:,1]))
            max_z_list.append(np.max(space_mesh.vertices[:,2]))

        for space_mesh in self.space_mesh_neutral_list:
            min_x_list.append(np.min(space_mesh.vertices[:,0]))
            min_y_list.append(np.min(space_mesh.vertices[:,1]))
            min_z_list.append(np.min(space_mesh.vertices[:,2]))

            max_x_list.append(np.max(space_mesh.vertices[:,0]))
            max_y_list.append(np.max(space_mesh.vertices[:,1]))
            max_z_list.append(np.max(space_mesh.vertices[:,2]))

        min_x = np.min(np.array(min_x_list))
        min_y = np.min(np.array(min_y_list))
        min_z = np.min(np.array(min_z_list))

        max_x = np.max(np.array(max_x_list))
        max_y = np.max(np.array(max_y_list))
        max_z = np.max(np.array(max_z_list))

        self.x_size = math.floor((max_x-min_x)/self.voxel_distance)+2
        self.y_size = math.floor((max_y-min_y)/self.voxel_distance)+2
        self.z_size = math.floor((max_z-min_z)/self.voxel_distance)+2

        x_rem = (max_x-min_x)-self.x_size*self.voxel_distance
        z_rem = (max_y-min_y)-self.y_size*self.voxel_distance
        y_rem = (max_z-min_z)-self.z_size*self.voxel_distance

        min_x = min_x+x_rem*0.5 - self.voxel_distance #add additional outdoor block
        min_y = min_y+y_rem*0.5 - self.voxel_distance #add additional outdoor block
        min_z = min_z+z_rem*0.5 - self.voxel_distance #add additional outdoor block

        max_x = max_x-x_rem*0.5 + self.voxel_distance #add additional outdoor block
        max_y = max_y-y_rem*0.5 + self.voxel_distance #add additional outdoor block
        max_z = max_z-z_rem*0.5 + self.voxel_distance #add additional outdoor block

        voxel_x_idx_vec = np.arange(self.x_size) #(x_size)
        voxel_y_idx_vec = np.arange(self.y_size) #(y_size)
        voxel_z_idx_vec = np.arange(self.z_size) #(z_size)

        self.voxel_x_location_vec = np.linspace(min_x,max_x,self.x_size) #(x_size)
        self.voxel_y_location_vec = np.linspace(min_y,max_y,self.y_size) #(y_size)
        self.voxel_z_location_vec = np.linspace(min_z,max_z,self.z_size) #(conv_z_size)

        voxel_x_idx_mesh,voxel_y_idx_mesh,voxel_z_idx_mesh = np.meshgrid(voxel_x_idx_vec,voxel_y_idx_vec,voxel_z_idx_vec)
        voxel_x_location_mesh,voxel_y_location_mesh,voxel_z_location_mesh = np.meshgrid(self.voxel_x_location_vec,self.voxel_y_location_vec,self.voxel_z_location_vec)

        idx_mesh = np.swapaxes(np.array([voxel_x_idx_mesh,voxel_y_idx_mesh,voxel_z_idx_mesh]),0,3) #(conv_x_size,conv_y_size,conv_z_size,3)
        location_mesh = np.swapaxes(np.array([voxel_x_location_mesh,voxel_y_location_mesh,voxel_z_location_mesh]),0,3) #(conv_x_size,conv_y_size,conv_z_size)

        idx_mesh_vec = np.reshape(idx_mesh,(idx_mesh.shape[0]*idx_mesh.shape[1]*idx_mesh.shape[2],idx_mesh.shape[3]))
        location_mesh_vec = np.reshape(location_mesh,(location_mesh.shape[0]*location_mesh.shape[1]*location_mesh.shape[2],location_mesh.shape[3]))

        print("Generating space to position index map...")
        self.grid_shape = (self.x_size,self.y_size,self.z_size)
        self._3D_space_idx_list = np.ones(self.grid_shape,dtype=np.int)*self.ambient_idx

        #Set indices for neutral space
        for space_counter,space_mesh in enumerate(self.space_mesh_neutral_list):
            bool_vec = space_mesh.contains(location_mesh_vec)
            x_idx = idx_mesh_vec[bool_vec,0]
            y_idx = idx_mesh_vec[bool_vec,1]
            z_idx = idx_mesh_vec[bool_vec,2]
            self._3D_space_idx_list[x_idx,y_idx,z_idx] = self.neutral_idx

            progressbar.progressbar(space_counter,0,len(self.space_mesh_neutral_list)-1)

        #Set indices for normal space
        for space_counter,space_mesh in enumerate(self.space_mesh_list):
            bool_vec = space_mesh.contains(location_mesh_vec)
            x_idx = idx_mesh_vec[bool_vec,0]
            y_idx = idx_mesh_vec[bool_vec,1]
            z_idx = idx_mesh_vec[bool_vec,2]
            self._3D_space_idx_list[x_idx,y_idx,z_idx] = space_counter
            self.space_idx_dict[self.space_name_list[space_counter]] = space_counter

            progressbar.progressbar(space_counter,0,len(self.space_mesh_list)-1)
            

    def get_point_space_idx(self,x_idx,y_idx,z_idx):
        return self._3D_space_idx_list[x_idx,y_idx,z_idx]

    def get_NN_3D_input(self,value_space_list,value_neutral,value_ground,value_ambient_air):
        NN_3D_temp_input = np.zeros(self.grid_shape,dtype=np.float)
        neutral_mask = self._3D_space_idx_list==self.neutral_idx
        outside_mask = self._3D_space_idx_list==self.ambient_idx
        below_zero_mask = np.zeros(self.grid_shape,dtype=np.bool)
        below_zero_mask[:,:,self.voxel_z_location_vec<0] = True
        ground_mask = np.logical_and(outside_mask,below_zero_mask)
        NN_3D_temp_input[neutral_mask] = value_neutral
        NN_3D_temp_input[outside_mask] = value_ambient_air
        NN_3D_temp_input[ground_mask] = value_ground
        for space_counter,value in enumerate(value_space_list):
            NN_3D_temp_input[self._3D_space_idx_list==space_counter] = value

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
            dx_temp[dx_temp>=self.grid_shape[0]] = dx_idx_space_2_x[dx_temp>=self.grid_shape[0]]
            temp = self._3D_space_idx_list[dx_temp, dx_idx_space_2_y, dx_idx_space_2_z] ###     If +1 point is not a room then check +2 point
            bool_dx = np.logical_or(dx_idx_pair_2 == self.neutral_idx, dx_idx_pair_2 == self.ambient_idx) ###
            dx_idx_pair_2[bool_dx] = temp[bool_dx] ###

            dy_temp = dy_idx_space_2_y+i+1
            dy_temp[dy_temp>=self.grid_shape[1]] = dy_idx_space_2_y[dy_temp>=self.grid_shape[1]]
            temp = self._3D_space_idx_list[dy_idx_space_2_x, dy_temp, dy_idx_space_2_z] ###
            bool_dy = np.logical_or(dy_idx_pair_2 == self.neutral_idx, dy_idx_pair_2 == self.ambient_idx) ###
            dy_idx_pair_2[bool_dy] = temp[bool_dy] ###

            dz_temp = dz_idx_space_2_z+i+1
            dz_temp[dz_temp>=self.grid_shape[2]] = dz_idx_space_2_z[dz_temp>=self.grid_shape[2]]
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



