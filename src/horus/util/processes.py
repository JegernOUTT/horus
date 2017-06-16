import subprocess
import sys
import json

import logging
import numpy as np
import os
import multiprocessing

import struct

logger = logging.getLogger(__name__)


class NormalEstimation:
    def __init__(self, mesh, settings_filename=None):
        assert mesh is not None
        assert mesh.vertexes is not None
        assert len(mesh.vertexes) > 0

        self.input_filename = '_input.xyz'
        self.output_filename = '_output.xyz'
        self.process_filename = './Hough_Exec'

        self.process = None

        try:
            with open(settings_filename, 'r') as f:
                data = json.load(f)

            assert 'neighborhood_size' in data.keys()
            assert 'planes_count' in data.keys()
            assert 'acc_steps' in data.keys()
            assert 'rotation_count' in data.keys()
            assert 'tolerance_angle' in data.keys()
            assert 'neighborhood_size_dens_est' in data.keys()

            self.neighborhood_size = data['neighborhood_size']
            self.planes_count = data['planes_count']
            self.acc_steps = data['acc_steps']
            self.rotation_count = data['rotation_count']
            self.tolerance_angle = data['tolerance_angle']
            self.neighborhood_size_dens_est = data['neighborhood_size_dens_est']

            logger.debug('Loaded settings for normals estimation from {}'.format(settings_filename))
        except:
            self._load_default_settings()

        self.mesh = mesh
        self.executed = False
        self._prepare()

    def _load_default_settings(self):
        logger.debug('Loaded default settings for normals estimation')
        self.neighborhood_size = 100
        self.planes_count = 1000
        self.acc_steps = 15
        self.rotation_count = 5
        self.tolerance_angle = 79
        self.neighborhood_size_dens_est = 5

    def __del__(self):
        if os.path.isfile(self.input_filename):
            os.remove(self.input_filename)
        if os.path.isfile(self.output_filename):
            os.remove(self.output_filename)

    def _prepare(self):
        with open(self.input_filename, 'w') as f:
            for vertex in self.mesh.vertexes:
                f.write('{0} {1} {2}\n'.format(vertex[0], vertex[1], vertex[2]))

        assert os.path.isfile(self.input_filename)
        assert os.stat(self.input_filename).st_size > 0

    def run(self):
        assert os.path.isfile(self.input_filename)

        with open(self.input_filename, 'r') as stdin:
            with open(self.output_filename, 'w') as stdout:
                self.process = subprocess.Popen([self.process_filename,
                                                 '-k {0}'.format(self.neighborhood_size),
                                                 '-t {0}'.format(self.planes_count),
                                                 '-p {0}'.format(self.acc_steps),
                                                 '-r {0}'.format(self.rotation_count),
                                                 '-a {0}'.format(self.tolerance_angle / 100),
                                                 '-e {0}'.format(self.neighborhood_size_dens_est)],
                                                stdin=stdin,
                                                stdout=stdout,
                                                stderr=sys.stderr,
                                                shell=False)

    def check_process(self):
        assert self.process is not None
        return_code = self.process.poll()
        if return_code is None:
            return None

        if return_code == 0:
            self.executed = True
        else:
            raise RuntimeError('Execution of {} was unsuccessful: '
                               'return code {}'.format(self.process_filename, return_code))
        return return_code

    def wait_process(self):
        assert self.process is not None
        return_code = self.process.wait()
        if return_code == 0:
            self.executed = True
        else:
            raise RuntimeError('Execution of {} was unsuccessful: '
                               'return code {}'.format(self.process_filename, return_code))

    def terminate(self):
        assert self.process is not None
        self.process.terminate()
        self.executed = True

    def get_normals(self):
        assert self.executed
        assert os.path.isfile(self.output_filename)
        assert os.stat(self.output_filename).st_size > 0

        with open(self.output_filename, 'r') as f:
            lines = f.readlines()

        index_of_data = 0
        for i, line in enumerate(lines):
            if line.strip() == 'points':
                index_of_data = i + 1
                break

        return np.array([[float(value) for value in line.split()[3:]]
                         for line in lines[index_of_data:]])


class PoissonReconstruction:
    def __init__(self, mesh, settings_filename=None):
        assert mesh is not None
        assert mesh.vertexes is not None
        assert len(mesh.vertexes) > 0

        self.process = None

        try:
            with open(settings_filename, 'r') as f:
                data = json.load(f)

            assert 'boundary_type' in data.keys()
            assert 'octree_depth' in data.keys()
            assert 'samples_per_node' in data.keys()
            assert 'point_weight' in data.keys()
            assert 'iterations' in data.keys()
            assert 'full_depth' in data.keys()
            assert 'density' in data.keys()
            assert 'linear_fit' in data.keys()
            assert 'polygon_mesh' in data.keys()

            self.boundary_type = data['boundary_type']
            self.octree_depth = data['octree_depth']
            self.samples_per_node = data['samples_per_node']
            self.point_weight = data['point_weight']
            self.iterations = data['iterations']
            self.full_depth = data['full_depth']
            self.density = data['density']
            self.linear_fit = data['linear_fit']
            self.polygon_mesh = data['polygon_mesh']

            logger.debug('Loaded settings for poisson reconstruction from {}'.format(settings_filename))
        except:
            self._load_default_settings()

        self.mesh = mesh
        self.executed = False

        self.input_name = '__poisson_input.ply'
        self.output_name = '__poisson_output.ply'
        self.process_filename = './PoissonRecon'

        self._prepare()

    def _load_default_settings(self):
        logger.debug('Loaded default settings for poisson reconstruction')
        self.boundary_type = 3
        self.octree_depth = 8
        self.samples_per_node = 5.5
        self.point_weight = 4.0
        self.iterations = 7
        self.full_depth = 5
        self.density = False
        self.linear_fit = False
        self.polygon_mesh = False

    def __del__(self):
        try:
            os.remove(self.input_name)
        except:
            pass

    def _prepare(self):
        with open(self.input_name, 'wb') as f:
            self.__save_scene_stream(f, self.mesh)

    def __save_scene_stream(self, stream, m):
        if m is not None:
            pack_type = '<fff'
            frame = "ply\n"
            frame += "format binary_little_endian 1.0\n"
            frame += "element vertex {0}\n".format(m.vertex_count)
            frame += "property float x\n"
            frame += "property float y\n"
            frame += "property float z\n"
            if m.has_colors:
                frame += "property uchar red\n"
                frame += "property uchar green\n"
                frame += "property uchar blue\n"
                pack_type += 'BBB'
            frame += "property float nx\n"
            frame += "property float ny\n"
            frame += "property float nz\n"
            pack_type += 'fff'
            frame += "element face 0\n"
            frame += "end_header\n"
            stream.write(frame)

            if m.has_colors:
                for i in xrange(m.vertex_count):
                    packed = struct.pack(pack_type,
                                         m.vertexes[i, 0], m.vertexes[i, 1], m.vertexes[i, 2],
                                         m.colors[i, 0], m.colors[i, 1], m.colors[i, 2],
                                         m.normal[i, 0], m.normal[i, 1], m.normal[i, 2])
                    stream.write(packed)
            else:
                for i in xrange(m.vertex_count):
                    packed = struct.pack(pack_type,
                                         m.vertexes[i, 0], m.vertexes[i, 1], m.vertexes[i, 2],
                                         m.normal[i, 0], m.normal[i, 1], m.normal[i, 2])
                    stream.write(packed)

    def run(self):
        params = [self.process_filename,
                  "--in", self.input_name,
                  "--out", self.output_name,
                  "--bType", str(self.boundary_type),
                  "--depth", str(self.octree_depth),
                  "--samplesPerNode", str(self.samples_per_node),
                  "--pointWeight", str(self.point_weight),
                  "--fullDepth", str(self.full_depth),
                  "--threads", str(multiprocessing.cpu_count())]
        if self.density:
            params.append("--density")
        if self.linear_fit:
            params.append("--linearFit")
        if self.polygon_mesh:
            params.append("--polygonMesh")

        self.process = subprocess.Popen(params, stdout=sys.stdout, stderr=sys.stdout)

    def wait_process(self):
        assert self.process is not None
        return_code = self.process.wait()
        if return_code == 0:
            self.executed = True
        else:
            raise RuntimeError('Execution of {} was unsuccessful: '
                               'return code {}'.format(self.process_filename, return_code))

    def check_process(self):
        assert self.process is not None
        return_code = self.process.poll()
        if return_code is None:
            return None

        if return_code == 0:
            self.executed = True
        else:
            raise RuntimeError('Execution of {} was unsuccessful: '
                               'return code {}'.format(self.process_filename, return_code))
        return return_code

    def terminate(self):
        assert self.process is not None
        self.process.terminate()
        self.executed = True

    def __load_binary(self, stream, dtype, count, tri_count, fm):
        data = np.fromfile(stream, dtype=dtype, count=count)

        fields = dtype.fields

        if 'v' in fields:
            vertexes = data['v']

        if 'n' in fields:
            normal = data['n']

        if 'c' in fields:
            colors = data['c']

        if tri_count > 0:
            tri_data = np.fromfile(stream,
                                   dtype=[('tr', '{0}u1, {0}i4, {0}i4, {0}i4'.format(fm), (1,))],
                                   count=tri_count)
            return tri_data['tr'][['f1', 'f2', 'f3']].view((fm + 'i4', 3)).reshape(tri_count, 3)

    def __load_scene(self, filename):
        with open(filename, "rb") as f:
            dtype = []
            count = 0
            tri_count = 0
            format = None
            line = None
            header = ''

            while line != 'end_header\n' and line != '':
                line = f.readline()
                header += line
            header = header.split('\n')

            if header[0] == 'ply':
                for line in header:
                    if 'format ' in line:
                        format = line.split(' ')[1]
                        break

                if format is not None:
                    if format == 'binary_big_endian':
                        fm = '>'
                    elif format == 'binary_little_endian':
                        fm = '<'

                df = {'float': fm + 'f', 'uchar': fm + 'B'}
                dt = {'x': 'v', 'nx': 'n', 'red': 'c', 'alpha': 'a'}
                ds = {'x': 3, 'nx': 3, 'red': 3, 'alpha': 1}

                for line in header:
                    if 'element vertex ' in line:
                        count = int(line.split('element vertex ')[1])
                    elif 'property ' in line:
                        props = line.split(' ')
                        if props[2] in dt.keys():
                            dtype = dtype + [(dt[props[2]], df[props[1]], (ds[props[2]],))]
                    elif 'element face ' in line:
                        tri_count = int(line.split('element face ')[1])

                dtype = np.dtype(dtype)

                if format is not None:
                    return self.__load_binary(f, dtype, count, tri_count, fm)

    def get_triangles(self):
        assert self.executed
        try:
            triangles = self.__load_scene(self.output_name)
            return triangles
        except:
            return None
