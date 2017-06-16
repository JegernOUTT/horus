# -*- coding: utf-8 -*-
# This file is part of the Horus Project
from enum import Enum

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2016 Mundo Reader S.L.\
                 Copyright (C) 2013 David Braam from Cura Project'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import os
from itertools import islice
from scipy.spatial import Delaunay
import numpy as np
from sklearn.neighbors import NearestNeighbors
from horus.util.processes import NormalEstimation, PoissonReconstruction

np.seterr(all='ignore')


class ModelType(Enum):
    PointCloud = 0
    Mesh = 1


class Model(object):
    """
    Each object has a Mesh and a 3x3 transformation matrix to rotate/scale the object.
    """

    def __init__(self, origin_filename, on_type_changed=None):
        self._origin_filename = origin_filename
        self._model_type = ModelType.Mesh
        if on_type_changed is not None:
            self.on_type_changed_callbacks = [on_type_changed]
        else:
            self.on_type_changed_callbacks = []

        if origin_filename is None:
            self._name = 'None'
        else:
            self._name = os.path.basename(origin_filename)
        if '.' in self._name:
            self._name = os.path.splitext(self._name)[0]
        self._mesh = None
        self._position = np.array([0.0, 0.0, 0.0])
        self._matrix = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]], np.float64)
        self._min = None
        self._max = None
        self._size = np.array([0.0, 0.0, 0.0])
        self._boundary_circle_size = 75.0
        self._draw_offset = np.array([0.0, 0.0, 0.0])

    def _add_mesh(self):
        self._mesh = Mesh(self)
        return self._mesh

    def on_type_changed(self, callback):
        if type(callback) is not list:
            self.on_type_changed_callbacks.append(callback)
        elif type(callback) is list:
            self.on_type_changed_callbacks += callback

    def _post_process_after_load(self):
        if len(self._mesh.vertexes) > 0:
            if self._model_type == ModelType.Mesh:
                self._mesh._calculate_normals()

            self._min = np.array([np.inf, np.inf, np.inf], np.float64)
            self._max = np.array([-np.inf, -np.inf, -np.inf], np.float64)
            self._boundary_circle_size = 0

            vertexes = self._mesh.vertexes
            vmin = vertexes.min(0)
            vmax = vertexes.max(0)
            for n in xrange(0, 3):
                self._min[n] = min(vmin[n], self._min[n])
                self._max[n] = max(vmax[n], self._max[n])

            # Calculate the boundary circle
            center = vmin + (vmax - vmin) / 2.0
            boundary_circle_size = round(np.max(np.linalg.norm(vertexes - center, axis=1)), 3)
            self._boundary_circle_size = max(self._boundary_circle_size, boundary_circle_size)

            self._size = self._max - self._min
            if self.model_type() == ModelType.Mesh:
                self._draw_offset = (self._max + self._min) / 2
                self._draw_offset[2] = self._min[2]
            self._max -= self._draw_offset
            self._min -= self._draw_offset

    def get_position(self):
        return self._position

    def get_matrix(self):
        return self._matrix

    def get_size(self):
        return self._size

    def get_draw_offset(self):
        return self._draw_offset

    def get_boundary_circle(self):
        return self._boundary_circle_size

    def model_type(self):
        return self._model_type

    def set_model_type(self, new_type):
        self._model_type = new_type
        for callback in self.on_type_changed_callbacks:
            callback(self._model_type)

    def get_scale(self):
        return np.array([
            np.linalg.norm(self._matrix[::, 0].getA().flatten()),
            np.linalg.norm(self._matrix[::, 1].getA().flatten()),
            np.linalg.norm(self._matrix[::, 2].getA().flatten())], np.float64)


class Mesh(object):
    """
    A mesh is a list of 3D triangles build from vertexes.
    Each triangle has 3 vertexes. It can be also a point cloud.
    A "VBO" can be associated with this object, which is used for rendering this object.
    """

    def __init__(self, obj):
        self.vertexes = None
        self.colors = None
        self.normal = None
        self.vertex_count = 0
        self.vbo = None
        self._obj = obj
        self.has_normals = False
        self.has_colors = False
        self.estimator = None
        self.reconstruction = None

    def _add_vertex(self, x, y, z, r=255, g=255, b=255):
        n = self.vertex_count
        self.vertexes[n], self.colors[n] = (x, y, z), (r, g, b)
        self.vertex_count += 1

    def _add_face(self, x0, y0, z0, x1, y1, z1, x2, y2, z2):
        n = self.vertex_count
        self.vertexes[n], self.vertexes[
            n + 1], self.vertexes[n + 2] = (x0, y0, z0), (x1, y1, z1), (x2, y2, z2)
        self.vertex_count += 3

    def _prepare_vertex_count(self, vertex_number):
        # Set the amount of vertex before loading data in them. This way we can
        # create the np arrays before we fill them.
        self.vertexes = np.zeros((vertex_number, 3), np.float32)
        self.colors = np.zeros((vertex_number, 3), np.int32)
        self.normal = np.zeros((vertex_number, 3), np.float32)
        self.vertex_count = 0

    def _prepare_face_count(self, face_number):
        # Set the amount of faces before loading data in them. This way we can
        # create the np arrays before we fill them.
        self.vertexes = np.zeros((face_number * 3, 3), np.float32)
        self.normal = np.zeros((face_number * 3, 3), np.float32)
        self.vertex_count = 0

    def clear_normals(self):
        self.normal = []


    def start_normals_with_normal_estimation(self, **kwargs):
        self.estimator = NormalEstimation(self, **kwargs)
        self.estimator.run()

    def is_finished_normals_with_normal_estimation(self):
        assert self.estimator is not None
        return_code = self.estimator.check_process()
        return return_code is not None

    def result_normals_with_normal_estimation(self):
        assert self.estimator is not None
        self.normal = self.estimator.get_normals()
        self.has_normals = True
        self.estimator = None
        return self.normal

    def stop_normals_with_normal_estimation(self):
        if self.estimator is not None:
            try:
                self.estimator.terminate()
                self.estimator = None
            except:
                pass


    def start_reconstruct_poisson(self, **kwargs):
        self.reconstruction = PoissonReconstruction(self, **kwargs)
        self.reconstruction.run()

    def is_finished_reconstruct_poisson(self):
        assert self.reconstruction is not None
        return_code = self.reconstruction.check_process()
        return return_code is not None

    def result_normals_reconstruct_poisson(self):
        assert self.reconstruction is not None
        name = self.reconstruction.output_name
        self.reconstruction = None
        return name

    def stop_normals_reconstruct_poisson(self):
        if self.reconstruction is not None:
            try:
                self.reconstruction.terminate()
                self.reconstruction = None
            except:
                pass

    def _calculate_normals(self):
        # Calculate the normals
        tris = self.vertexes.reshape(self.vertex_count / 3, 3, 3)
        normals = np.cross(tris[::, 1] - tris[::, 0], tris[::, 2] - tris[::, 0])
        normals /= np.linalg.norm(normals)
        n = np.concatenate((np.concatenate((normals, normals), axis=1), normals), axis=1)
        self.normal = n.reshape(self.vertex_count, 3)
        self.has_normals = True
