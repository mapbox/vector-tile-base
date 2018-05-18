import itertools
from . import vector_tile_pb2

# Python3 Compatability
try:
    unicode
    other_str = unicode
except NameError:
    other_str = bytes

def zig_zag_encode(val):
    return (int(val) << 1) ^ (int(val) >> 31)

def zig_zag_decode(val):
    return ((val >> 1) ^ (-(val & 1)))

def command_integer(cmd_id, count):
    return (cmd_id & 0x7) | (count << 3);

def command_move_to(count):
    return command_integer(1, count)

def command_line_to(count):
    return command_integer(2, count)

def command_close_path():
    return command_integer(7,0)

def get_command_id(command_integer):
    return command_integer & 0x7;

def get_command_count(command_integer):
    return command_integer >> 3

def next_command_move_to(command_integer):
    return get_command_id(command_integer) == 1

def next_command_line_to(command_integer):
    return get_command_id(command_integer) == 2

def next_command_close_path(command_integer):
    return get_command_id(command_integer) == 7

class Float(float):
    
    def __init__(self, *args, **kwargs):
        float.__init__(self, *args, **kwargs)

class FeatureProperties(object):

    def __init__(self, feature, layer):
        self._feature = feature
        self._layer = layer
        self._prop = {}
        self._prop_current = False

    def _encode_prop(self):
        self._feature.tags[:] = self._layer.add_attributes(self._prop)
        self._prop_current = True
    
    def _decode_prop(self):
        if not self._prop_current:
            if len(self._feature.tags) == 0:
                self._prop = {}
            else:
                self._prop = self._layer.get_attributes(self._feature.tags)
            self._prop_current = True

    def __len__(self):
        self._decode_prop()
        return len(self._prop)
        
    def __getitem__(self, key):
        self._decode_prop()
        if not isinstance(key, str) and not isinstance(key, other_str):
            raise TypeError("Keys must be of type str")
        return self._prop[key]

    def __delitem__(self, key):
        self._decode_prop()
        del self._prop[key]
        self._encode_prop()

    def __setitem__(self, key, value):
        if not isinstance(key, str) and not isinstance(key, other_str):
            raise TypeError("Keys must be of type str or other_str")
        self._decode_prop()
        self._prop[key] = value
        self._encode_prop()

    def __iter__(self):
        self._decode_prop()
        return self._prop.__iter__()

    def __eq__(self, other):
        self._decode_prop()
        if isinstance(other, dict):
            return self._prop == other
        elif isinstance(other, FeatureProperties):
            other._decode_prop()
            return self._prop == other._prop
        return False
    
    def __str__(self):
        self._decode_prop()
        return self._prop.__str__()

    def __contains__(self, key):
        self._decode_prop()
        return self._prop.__contains__(key)
   
    def set(self, prop):
        self._prop = dict(prop)
        self._encode_prop()

class Feature(object):

    def __init__(self, feature, layer, dimensions):
        self._feature = feature
        self._layer = layer
        self.dimensions = dimensions
        self._reset_cursor()
        self._properties = FeatureProperties(feature, layer)

    def _reset_cursor(self):
        self.cursor = []
        self.cursor[:self.dimensions] = itertools.repeat(0, self.dimensions)
        self._cursor_at_end = False
    
    def _encode_point(self, pt):
        for i in range(self.dimensions):
            self._feature.geometry.append(zig_zag_encode(pt[i] - self.cursor[i]))
            self.cursor[i] = pt[i]

    def _decode_point(self, integers):
        for i in range(self.dimensions):
            self.cursor[i] = self.cursor[i] + zig_zag_decode(integers[i])
        return list(self.cursor)

    def _points_equal(self, pt1, pt2):
        for i in range(self.dimensions):
            if pt1[i] is not pt2[i]:
                return False
        return True

    @property
    def properties(self):
        return self._properties

    @properties.setter
    def properties(self, props):
        self._properties.set(props)

    @property
    def id(self):
        if self._feature.HasField('id'):
            return self._feature.id;
        return None
    
    @id.setter
    def id(self, id_val):
        self._feature.id = id_val

    def clear_geometry(self):
        self.has_geometry = False
        self._feature.ClearField('geometry')

class PointFeature(Feature):
    
    def __init__(self, feature, layer, dimensions):
        super(PointFeature, self).__init__(feature, layer, dimensions)
        if feature.type is not vector_tile_pb2.Tile.POINT:
            feature.type = vector_tile_pb2.Tile.POINT
        self.type = 'point'
            
    def add_points(self, points):
        if not isinstance(points, list):
            raise Exception("Invalid point geometry")
        if not self._cursor_at_end:
            # Use geometry retrieval process to move cursor to proper position
            self.get_points()
        if len(points) < 1:
            return
        multi_point = isinstance(points[0], list)
        if multi_point:
            num_commands = len(points)
        else:
            num_commands = 1
        self._feature.geometry.append(command_move_to(num_commands))
        if multi_point:
            for i in range(num_commands):
                self._encode_point(points[i])
        else:
            self._encode_point(points)

    def get_points(self):
        points = []
        self._reset_cursor()
        geom = iter(self._feature.geometry)
        try:
            current_command = next(geom)
            while next_command_move_to(current_command):
                for i in range(get_command_count(current_command)):
                    points.append(self._decode_point([next(geom) for n in range(self.dimensions)]))
                current_command = next(geom)
        except StopIteration:
            pass
        self._cursor_at_end = True
        return points
 
    def get_geometry(self):
        return self.get_points()       

class LineStringFeature(Feature):
    
    def __init__(self, feature, layer, dimensions):
        super(LineStringFeature, self).__init__(feature, layer, dimensions)
        if feature.type is not vector_tile_pb2.Tile.LINESTRING:
            feature.type = vector_tile_pb2.Tile.LINESTRING
        self.type = 'line_string'
            
    def add_line_string(self, linestring):
        num_commands = len(linestring)
        if num_commands < 2:
            raise Exception("Error adding linestring, less then 2 points provided")
        if not self._cursor_at_end:
            # Use geometry retrieval process to move cursor to proper position
            self.get_line_strings()
        self._feature.geometry.append(command_move_to(1))
        self._encode_point(linestring[0])
        self._feature.geometry.append(command_line_to(num_commands - 1))
        for i in range(1, num_commands):
            self._encode_point(linestring[i])
    
    def get_line_strings(self):
        line_strings = []
        line_string = []
        self._reset_cursor()
        geom = iter(self._feature.geometry)
        try:
            current_command = next(geom)
            while next_command_move_to(current_command):
                line_string = []
                if get_command_count(current_command) != 1:
                    raise Exception("Command move_to has command count not equal to 1 in a line string")
                line_string.append(self._decode_point([next(geom) for n in range(self.dimensions)]))
                current_command = next(geom)
                if not next_command_line_to(current_command):
                    raise Exception("Command move_to not followed by a line_to command in a line string")
                while next_command_line_to(current_command):
                    for i in range(get_command_count(current_command)):
                        line_string.append(self._decode_point([next(geom) for n in range(self.dimensions)]))
                    current_command = next(geom)
                if len(line_string) > 1:
                    line_strings.append(line_string)
        except StopIteration:
            if len(line_string) > 1:
                line_strings.append(line_string)
            pass
        self._cursor_at_end = True
        return line_strings
    
    def get_geometry(self):
        return self.get_line_strings()       

class PolygonFeature(Feature):
    
    def __init__(self, feature, layer, dimensions):
        super(PolygonFeature, self).__init__(feature, layer, dimensions)
        if feature.type is not vector_tile_pb2.Tile.POLYGON:
            feature.type = vector_tile_pb2.Tile.POLYGON
        self.type = 'polygon'
            
    def add_ring(self, ring):
        if not self._cursor_at_end:
            # Use geometry retrieval process to move cursor to proper position
            self.get_rings()
        num_commands = len(ring)
        if num_commands < 3:
            raise Exception("Error adding ring to polygon, too few points")
        if self._points_equal(ring[0], ring[-1]):
            num_commands = num_commands - 1
        if num_commands < 3:
            raise Exception("Error adding ring to polygon, too few points with last point closing")
        self._feature.geometry.append(command_move_to(1))
        self._encode_point(ring[0])
        self._feature.geometry.append(command_line_to(num_commands - 1))
        for i in range(1, num_commands):
            self._encode_point(ring[i])
        self._feature.geometry.append(command_close_path())
    
    def get_rings(self):
        rings = []
        ring = []
        self._reset_cursor()
        geom = iter(self._feature.geometry)
        try:
            current_command = next(geom)
            while next_command_move_to(current_command):
                ring = []
                if get_command_count(current_command) != 1:
                    raise Exception("Command move_to has command count not equal to 1 in a line string")
                ring.append(self._decode_point([next(geom) for n in range(self.dimensions)]))
                current_command = next(geom)
                while next_command_line_to(current_command):
                    for i in range(get_command_count(current_command)):
                        ring.append(self._decode_point([next(geom) for n in range(self.dimensions)]))
                    current_command = next(geom)
                if not next_command_close_path(current_command):
                    raise Exception("Polygon not closed with close_path command")
                ring.append(ring[0])
                if len(ring) > 3:
                    rings.append(ring)
                current_command = next(geom)
        except StopIteration:
            pass
        self._cursor_at_end = True
        return rings
    
    def _is_ring_clockwise(self, ring):
        if self.dimensions != 2:
            return False
        area = 0.0
        for i in range(len(ring) - 1):
            area += (float(ring[i][0]) * float(ring[i+1][1])) - (float(ring[i][1]) * float(ring[i+1][0]))
        return area < 0.0
    
    def get_polygons(self):
        rings = self.get_rings()
        polygons = []
        polygon = []
        for ring in rings:
            if not self._is_ring_clockwise(ring):
                if len(polygon) != 0:
                    polygons.append(polygon)
                polygon = []
                polygon.append(ring)
            elif len(polygon) != 0:
                polygon.append(ring)
        if len(polygon) != 0:
            polygons.append(polygon)
        return polygons

    def get_geometry(self):
        return self.get_polygons()       

class SplineFeature(Feature):
    
    def __init__(self, feature, layer, dimensions):
        super(SplineFeature, self).__init__(feature, layer, dimensions)
        if feature.type is not vector_tile_pb2.Tile.SPLINE:
            feature.type = vector_tile_pb2.Tile.SPLINE
        self.type = 'spline'
            
    def add_control_points(self, control_points):
        num_commands = len(control_points)
        if num_commands < 2:
            raise Exception("Error adding control points, less then 2 points provided")
        self._feature.geometry.append(command_move_to(1))
        self._encode_point(control_points[0])
        self._feature.geometry.append(command_line_to(num_commands - 1))
        for i in range(1, num_commands):
            self._encode_point(control_points[i])
    
    def get_control_points(self):
        control_points = []
        self._reset_cursor()
        geom = iter(self._feature.geometry)
        try:
            current_command = next(geom)
            if next_command_move_to(current_command):
                if get_command_count(current_command) != 1:
                    raise Exception("Command move_to has command count not equal to 1 in a line string")
                control_points.append(self._decode_point([next(geom) for n in range(self.dimensions)]))
                current_command = next(geom)
                while next_command_line_to(current_command):
                    for i in range(get_command_count(current_command)):
                        control_points.append(self._decode_point([next(geom) for n in range(self.dimensions)]))
                    current_command = next(geom)
        except StopIteration:
            pass
        self._cursor_at_end = True
        if len(control_points) < 1:
            return []
        return control_points

    def add_knots(self, knots):
        self._feature.knots[:] = knots

    def get_knots(self):
        return self._feature.knots

    def get_geometry(self):
        return [self.get_control_points(), self.get_knots()]  

class Layer(object):

    def __init__(self, layer, name = None, dimensions = None, version = None):
        self._layer = layer
        self._values = []
        self._keys = []
        self._features = []
        if name:
            self._layer.name = name
        if version:
            self._layer.version = version
        if dimensions:
            self._layer.dimensions = dimensions
        elif not self._layer.HasField('dimensions'):
            self._layer.dimensions = 2
        self._decode_keys()
        self._decode_values()
        self._build_features()

    def _decode_list(self, tags):
        out = []
        for t in tags:
            out.append(self._values[t])
        return out
    
    def _decode_values(self):
        for val in self._layer.values:
            if val.HasField('bool_value'):
                self._values.append(val.bool_value)
            elif val.HasField('string_value'):
                self._values.append(val.string_value)
            elif val.HasField('float_value'):
                self._values.append(val.float_value)
            elif val.HasField('double_value'):
                self._values.append(val.double_value)
            elif val.HasField('int_value'):
                self._values.append(val.int_value)
            elif val.HasField('uint_value'):
                self._values.append(val.uint_value)
            elif val.HasField('sint_value'):
                self._values.append(val.sint_value)
            elif len(val.hash_value) > 0:
                self._values.append(self.get_attributes(val.hash_value))
            elif len(val.list_value) > 0:
                self._values.append(self._decode_list(val.list_value))

    def _decode_keys(self):
        for key in self._layer.keys:
            self._keys.append(key)

    def _build_features(self):
        dim = self._layer.dimensions
        for feature in self._layer.features:
            if feature.type == vector_tile_pb2.Tile.POINT:
                self._features.append(PointFeature(feature, self, dim))
            elif feature.type == vector_tile_pb2.Tile.LINESTRING:
                self._features.append(LineStringFeature(feature, self, dim))
            elif feature.type == vector_tile_pb2.Tile.POLYGON:
                self._features.append(PolygonFeature(feature, self, dim))
            elif feature.type == vector_tile_pb2.Tile.SPLINE:
                self._features.append(SplineFeature(feature, self, dim))
    
    def add_point_feature(self):
        dim = self._layer.dimensions
        self._features.append(PointFeature(self._layer.features.add(), self, dim))
        return self._features[-1]

    def add_line_string_feature(self):
        dim = self._layer.dimensions
        self._features.append(LineStringFeature(self._layer.features.add(), self, dim))
        return self._features[-1]
    
    def add_polygon_feature(self):
        dim = self._layer.dimensions
        self._features.append(PolygonFeature(self._layer.features.add(), self, dim))
        return self._features[-1]
    
    def add_spline_feature(self):
        dim = self._layer.dimensions
        self._features.append(SplineFeature(self._layer.features.add(), self, dim))
        return self._features[-1]

    @property
    def features(self):
        return self._features

    @property
    def name(self):
        return self._layer.name

    @name.setter
    def name(self, name):
        self._layer.name = name
        
    @property
    def extent(self):
        if self._layer.HasField('extent'):
            return self._layer.extent
        return 4096

    @extent.setter
    def extent(self, extent):
        self._layer.extent = extent
    
    @property
    def dimensions(self):
        return self._layer.dimensions

    @property
    def version(self):
        return self._layer.version

    @version.setter
    def version(self, version):
        self._layer.version = version
 
    def get_attributes(self, tags):
        properties = {}
        for i in range(0,len(tags),2):
            properties[self._keys[tags[i]]] = self._values[tags[i+1]]
        return properties

    def add_attribute_list(self, data):
        tags = []
        remove = []
        for v in data:
            if not (v in self._values and type(self._values[self._values.index(v)]) == type(v)):
                if isinstance(v,bool):
                    val = self._layer.values.add()
                    val.bool_value = v
                elif (isinstance(v,str)) or (isinstance(v,other_str)):
                    val = self._layer.values.add()
                    val.string_value = v
                elif isinstance(v,int):
                    val = self._layer.values.add()
                    val.int_value = v
                elif isinstance(v,Float):
                    val = self._layer.values.add()
                    val.float_value = v
                elif isinstance(v,float):
                    val = self._layer.values.add()
                    val.double_value = v
                elif isinstance(v,list):
                    list_tags = self.add_attribute_list(v)
                    if len(list_tags) > 0:
                        val = self._layer.values.add()
                        val.list_value[:] = list_tags
                    else:
                        remove.append(v)
                        continue
                elif isinstance(v, dict):
                    dict_tags = self.add_attributes(v)
                    if len(dict_tags) > 0:
                        val = self._layer.values.add()
                        val.hash_value[:] = dict_tags
                    else:
                        remove.append(v)
                        continue
                else:
                    remove.append(v)
                    continue
                self._values.append(v)
                value_index = len(self._values) - 1
            else:
                value_index = self._values.index(v)
            tags.append(value_index)
        if remove:
            data[:] = [x for x in data if x not in remove]
        return tags

    def add_attributes(self, props):
        tags = []
        remove = []
        for k,v in props.items():
            if not isinstance(k, str) and not isinstance(k, other_str):
                remove.append(k)
                continue
            if not (v in self._values and type(self._values[self._values.index(v)]) == type(v)):
                if isinstance(v,bool):
                    val = self._layer.values.add()
                    val.bool_value = v
                elif (isinstance(v,str)) or (isinstance(v,other_str)):
                    val = self._layer.values.add()
                    val.string_value = v
                elif isinstance(v,int):
                    val = self._layer.values.add()
                    val.int_value = v
                elif isinstance(v,Float):
                    val = self._layer.values.add()
                    val.float_value = v
                elif isinstance(v,float):
                    val = self._layer.values.add()
                    val.double_value = v
                elif isinstance(v,list):
                    list_tags = self.add_attribute_list(v)
                    if len(list_tags) > 0:
                        val = self._layer.values.add()
                        val.list_value[:] = list_tags
                    else:
                        remove.append(k)
                        continue
                elif isinstance(v, dict):
                    dict_tags = self.add_attributes(v)
                    if len(dict_tags) > 0:
                        val = self._layer.values.add()
                        val.hash_value[:] = dict_tags
                    else:
                        remove.append(k)
                        continue
                else:
                    remove.append(k)
                    continue
                self._values.append(v)
                value_index = len(self._values) - 1
            else:
                value_index = self._values.index(v)

            if k not in self._keys:
                self._layer.keys.append(k)
                self._keys.append(k)
            tags.append(self._keys.index(k))
            tags.append(value_index)
        for k in remove:
            del props[k]
        return tags


class VectorTile(object):

    def __init__(self, tile = None):
        self._layers = []
        if tile:
            if (isinstance(tile,str)) or (isinstance(tile,other_str)):
                self._tile = vector_tile_pb2.Tile()
                self._tile.ParseFromString(tile)
            else:
                self._tile = tile
            self._build_layers()
        else:
            self._tile = vector_tile_pb2.Tile()
    
    def __str__(self):
        return self._tile.__str__()

    def _build_layers(self):
        for layer in self._tile.layers:
            self._layers.append(Layer(layer))

    def serialize(self):
        return self._tile.SerializeToString()

    def add_layer(self, name, dimensions = 2, version = 2):
        self._layers.append(Layer(self._tile.layers.add(), name, dimensions, version))
        return self._layers[-1]

    @property
    def layers(self):
        return self._layers
