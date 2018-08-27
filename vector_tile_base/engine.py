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

def zig_zag_encode_64(val):
    return (int(val) << 1) ^ (int(val) >> 63)

def zig_zag_decode(val):
    return ((val >> 1) ^ (-(val & 1)))

def command_integer(cmd_id, count):
    return (cmd_id & 0x7) | (count << 3);

def command_move_to(count):
    return command_integer(1, count)

def command_line_to(count):
    return command_integer(2, count)

def command_close_path():
    return command_integer(7,1)

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

def get_inline_value_id(complex_value):
    return complex_value & 0x0F;

def get_inline_value_parameter(complex_value):
    return complex_value >> 4;

def complex_value_integer(cmd_id, param):
    return (cmd_id & 0x0F) | (param << 4);

class Float(float):
    
    def __init__(self, *args, **kwargs):
        float.__init__(self, *args, **kwargs)

class UInt(int):
    
    def __init__(self, *args, **kwargs):
        int.__init__(self, *args, **kwargs)

class FeatureAttributes(object):

    def __init__(self, feature, layer):
        self._feature = feature
        self._layer = layer
        self._attr = {}
        self._attr_current = False

    def _encode_attr(self):
        if self._layer._pool:
            self._feature.attributes[:] = self._layer.add_attributes(self._attr)
        else:
            self._feature.tags[:] = self._layer.add_attributes(self._attr)
        self._attr_current = True
    
    def _decode_attr(self):
        if not self._attr_current:
            if self._layer._pool:
                if len(self._feature.attributes) == 0:
                    self._attr = {}
                else:
                    self._attr = self._layer.get_attributes(self._feature.attributes)
            else:
                if len(self._feature.tags) == 0:
                    self._attr = {}
                else:
                    self._attr = self._layer.get_attributes(self._feature.tags)
            self._attr_current = True

    def __len__(self):
        self._decode_attr()
        return len(self._attr)
        
    def __getitem__(self, key):
        self._decode_attr()
        if not isinstance(key, str) and not isinstance(key, other_str):
            raise TypeError("Keys must be of type str")
        return self._attr[key]

    def __delitem__(self, key):
        self._decode_attr()
        del self._attr[key]
        self._encode_attr()

    def __setitem__(self, key, value):
        if not isinstance(key, str) and not isinstance(key, other_str):
            raise TypeError("Keys must be of type str or other_str")
        self._decode_attr()
        self._attr[key] = value
        self._encode_attr()

    def __iter__(self):
        self._decode_attr()
        return self._attr.__iter__()

    def __eq__(self, other):
        self._decode_attr()
        if isinstance(other, dict):
            return self._attr == other
        elif isinstance(other, FeatureAttributes):
            other._decode_attr()
            return self._attr == other._attr
        return False
    
    def __str__(self):
        self._decode_attr()
        return self._attr.__str__()

    def __contains__(self, key):
        self._decode_attr()
        return self._attr.__contains__(key)
   
    def set(self, attr):
        self._attr = dict(attr)
        self._encode_attr()

class Feature(object):

    def __init__(self, feature, layer, dimensions=None):
        self._feature = feature
        self._layer = layer
        if dimensions is None:
            if len(self._feature.geometry_3d) != 0:
                self._dimensions = 3
            else:
                self._dimensions = 2
        else:
            if dimensions > 2 and self._layer.version < 3:
                raise Exception("Layers of version 1 or 2 can only have two dimensional geometry in features")
            elif dimensions > 3:
                raise Exception("Features can not have more then 3 dimensions of geometry")
            elif dimensions < 2:
                raise Exception("Features must have at least 2 dimensions")
            self._dimensions = dimensions

        self._reset_cursor()
        self._attributes = FeatureAttributes(feature, layer)

    def _reset_cursor(self):
        self.cursor = []
        self.cursor[:self.dimensions] = itertools.repeat(0, self.dimensions)
        self._cursor_at_end = False
    
    def _encode_point(self, pt, cmd_list):
        for i in range(self.dimensions):
            cmd_list.append(zig_zag_encode(pt[i] - self.cursor[i]))
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
    def dimensions(self):
        return self._dimensions

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, attrs):
        self._attributes.set(attrs)

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
        self._reset_cursor()
        self._feature.ClearField('geometry')
        self._feature.ClearField('geometry_3d')

class PointFeature(Feature):
    
    def __init__(self, feature, layer, dimensions=None):
        super(PointFeature, self).__init__(feature, layer, dimensions)
        if feature.type is not vector_tile_pb2.Tile.POINT:
            feature.type = vector_tile_pb2.Tile.POINT
        self.type = 'point'
        self._num_points = 0
            
    def add_points(self, points):
        if not isinstance(points, list):
            raise Exception("Invalid point geometry")
        if not self._cursor_at_end:
            # Use geometry retrieval process to move cursor to proper position
            pts = self.get_points()
            self._num_points = len(pts)
        if len(points) < 1:
            return
        multi_point = isinstance(points[0], list)
        if multi_point:
            num_commands = len(points)
        else:
            num_commands = 1

        cmd_list = []
        if self._num_points == 0:
            cmd_list.append(command_move_to(num_commands))
        try:
            if multi_point:
                for i in range(num_commands):
                    self._encode_point(points[i], cmd_list)
            else:
                self._encode_point(points, cmd_list)
        except Exception as e:
            self._reset_cursor()
            raise e
        if self.dimensions == 2:
            if self._num_points != 0:
                self._num_points = self._num_points + num_commands
                self._feature.geometry[0] = command_move_to(self._num_points)
            self._feature.geometry.extend(cmd_list)
        else:
            if self._num_points != 0:
                self._num_points = self._num_points + num_commands
                self._feature.geometry_3d[0] = command_move_to(self._num_points)
            self._feature.geometry_3d.extend(cmd_list)

    def get_points(self):
        points = []
        self._reset_cursor()
        if self.dimensions == 2:
            geom = iter(self._feature.geometry)
        else:
            geom = iter(self._feature.geometry_3d)
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
    
    def __init__(self, feature, layer, dimensions=None):
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
        try:
            cmd_list = []
            cmd_list.append(command_move_to(1))
            self._encode_point(linestring[0], cmd_list)
            cmd_list.append(command_line_to(num_commands - 1))
            for i in range(1, num_commands):
                self._encode_point(linestring[i], cmd_list)
        except Exception as e:
            self._reset_cursor()
            raise e
        if self.dimensions == 2:
            self._feature.geometry.extend(cmd_list)
        else:
            self._feature.geometry_3d.extend(cmd_list)
    
    def get_line_strings(self):
        line_strings = []
        line_string = []
        self._reset_cursor()
        if self.dimensions == 2:
            geom = iter(self._feature.geometry)
        else:
            geom = iter(self._feature.geometry_3d)
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
    
    def __init__(self, feature, layer, dimensions=None):
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
        try:
            cmd_list = []
            cmd_list.append(command_move_to(1))
            self._encode_point(ring[0], cmd_list)
            cmd_list.append(command_line_to(num_commands - 1))
            for i in range(1, num_commands):
                self._encode_point(ring[i], cmd_list)
            cmd_list.append(command_close_path())
        except Exception as e:
            self._reset_cursor()
            raise e
        if self.dimensions == 2:
            self._feature.geometry.extend(cmd_list)
        else:
            self._feature.geometry_3d.extend(cmd_list)
    
    def get_rings(self):
        rings = []
        ring = []
        self._reset_cursor()
        if self.dimensions == 2:
            geom = iter(self._feature.geometry)
        else:
            geom = iter(self._feature.geometry_3d)
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

class CurveFeature(Feature):
    
    def __init__(self, feature, layer, dimensions=None):
        super(CurveFeature, self).__init__(feature, layer, dimensions)
        if feature.type is not vector_tile_pb2.Tile.CURVE:
            feature.type = vector_tile_pb2.Tile.CURVE
        self.type = 'curve'
            
    def add_control_points(self, control_points):
        num_commands = len(control_points)
        if num_commands < 2:
            raise Exception("Error adding control points, less then 2 points provided")
        try:
            cmd_list = []
            cmd_list.append(command_move_to(1))
            self._encode_point(control_points[0], cmd_list)
            cmd_list.append(command_line_to(num_commands - 1))
            for i in range(1, num_commands):
                self._encode_point(control_points[i], cmd_list)
        except Exception as e:
            self._reset_cursor()
            raise e
        if self.dimensions == 2:
            self._feature.geometry.extend(cmd_list)
        else:
            self._feature.geometry_3d.extend(cmd_list)
    
    def get_control_points(self):
        control_points = []
        self._reset_cursor()
        if self.dimensions == 2:
            geom = iter(self._feature.geometry)
        else:
            geom = iter(self._feature.geometry_3d)
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

    def __init__(self, layer, name = None, version = None):
        self._layer = layer
        self._features = []
        if name:
            self._layer.name = name
        if version:
            self._layer.version = version
        elif not self._layer.HasField('version'):
            self._layer.version = 2
        
        self._keys = []
        if self._layer.HasField('attribute_pool') or self.version > 2:
            self._pool = True
            self._string_values = []
            self._float_values = []
            self._double_values = []
            self._signed_integer_values = []
            self._unsigned_integer_values = []
            self._decode_inline_keys()
            self._decode_inline_values()
        else:
            self._pool = False
            self._values = []
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
    
    def _decode_inline_values(self):
        if not self._layer.HasField('attribute_pool'):
            return
        for val in self._layer.attribute_pool.string_values:
            self._string_values.append(val)
        for val in self._layer.attribute_pool.float_values:
            self._float_values.append(Float(val))
        for val in self._layer.attribute_pool.double_values:
            self._double_values.append(val)
        for val in self._layer.attribute_pool.signed_integer_values:
            self._signed_integer_values.append(val)
        for val in self._layer.attribute_pool.unsigned_integer_values:
            self._unsigned_integer_values.append(UInt(val))

    def _decode_keys(self):
        for key in self._layer.keys:
            self._keys.append(key)

    def _decode_inline_keys(self):
        if self._layer.HasField('attribute_pool'):
            for key in self._layer.attribute_pool.keys:
                self._keys.append(key)

    def _build_features(self):
        for feature in self._layer.features:
            if feature.type == vector_tile_pb2.Tile.POINT:
                self._features.append(PointFeature(feature, self))
            elif feature.type == vector_tile_pb2.Tile.LINESTRING:
                self._features.append(LineStringFeature(feature, self))
            elif feature.type == vector_tile_pb2.Tile.POLYGON:
                self._features.append(PolygonFeature(feature, self))
            elif feature.type == vector_tile_pb2.Tile.CURVE:
                self._features.append(CurveFeature(feature, self))
    
    def add_point_feature(self, dimensions=2):
        self._features.append(PointFeature(self._layer.features.add(), self, dimensions))
        return self._features[-1]

    def add_line_string_feature(self, dimensions=2):
        self._features.append(LineStringFeature(self._layer.features.add(), self, dimensions))
        return self._features[-1]
    
    def add_polygon_feature(self, dimensions=2):
        self._features.append(PolygonFeature(self._layer.features.add(), self, dimensions))
        return self._features[-1]
    
    def add_curve_feature(self, dimensions=2):
        if self.version < 3:
            raise Exception("Can not add curves to Version 2 or below Vector Tiles.")
        self._features.append(CurveFeature(self._layer.features.add(), self, dimensions))
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
    def version(self):
        if self._layer.HasField('version'):
            return self._layer.version
        return 2

    def get_attributes(self, int_list):
        if not self._pool:
            attributes = {}
            for i in range(0,len(int_list),2):
                attributes[self._keys[int_list[i]]] = self._values[int_list[i+1]]
            return attributes
        else:
            return self._get_inline_map_attributes(iter(int_list))
 
    def _get_inline_value(self, complex_value, value_itr):
        val_id = get_inline_value_id(complex_value)
        param = get_inline_value_parameter(complex_value)
        if val_id == 0:
            return self._string_values[param]
        elif val_id == 1:
            return self._float_values[param]
        elif val_id == 2:
            return self._double_values[param]
        elif val_id == 3:
            return self._signed_integer_values[param]
        elif val_id == 4:
            return self._unsigned_integer_values[param]
        elif val_id == 5:
            return param
        elif val_id == 6:
            return zig_zag_decode(param)
        elif val_id == 7:
            if param == 0:
                return False
            elif param == 1:
                return True
            else:
                return None
        elif val_id == 8:
            return self._get_inline_list_attributes(value_itr, param)
        elif val_id == 9:
            return self._get_inline_map_attributes(value_itr, param)
        else:
            raise Exception("Unknown value type in inline value")
           
    def _get_inline_map_attributes(self, value_itr, limit = None):
        attr_map = {}
        if limit == 0:
            return attr_map
        count = 0
        for key in value_itr:
            try:
                val = next(value_itr)
            except StopIteration:
                break
            attr_map[self._keys[key]] = self._get_inline_value(val, value_itr)
            count = count + 1
            if limit is not None and count >= limit:
                break
        return attr_map
    
    def _get_inline_list_attributes(self, value_itr, limit = None):
        attr_list = []
        if limit == 0:
            return attr_list
        count = 0
        for val in value_itr:
            attr_list.append(self._get_inline_value(val, value_itr))
            count = count + 1
            if limit is not None and count >= limit:
                break
        return attr_list

    def _add_legacy_attributes(self, attrs):
        tags = []
        remove = []
        for k,v in attrs.items():
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
                elif isinstance(v,UInt) and v >= 0:
                    val = self._layer.values.add()
                    val.uint_value = v
                elif isinstance(v,int):
                    val = self._layer.values.add()
                    val.int_value = v
                elif isinstance(v,Float):
                    val = self._layer.values.add()
                    val.float_value = v
                elif isinstance(v,float):
                    val = self._layer.values.add()
                    val.double_value = v
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
            del attrs[k]
        return tags
    
    def _add_inline_value(self, v):
        if v is None:
            return complex_value_integer(7, 2)
        elif isinstance(v, bool):
            if v == True:
                return complex_value_integer(7, 1)
            else:
                return complex_value_integer(7, 0)
        elif isinstance(v,str) or isinstance(v,other_str):
            try:
                return self._string_values.index(v)
            except ValueError:
                self._string_values.append(v)
                self._layer.attribute_pool.string_values.append(v)
                return complex_value_integer(0, len(self._string_values) - 1)
        elif isinstance(v,UInt) and v >= 0:
            if v >= 2**56:
                try:
                    return self._unsigned_integer_values.index(v)
                except ValueError:
                    self._unsigned_integer_values.append(v)
                    self._layer.attribute_pool.unsigned_integer_values.append(v)
                    return complex_value_integer(4, len(self._unsigned_integer_values) - 1)
            else:
                return complex_value_integer(5, v)
        elif isinstance(v,int):
            if v >= 2**55 or v <= -2**55:
                try:
                    return self._signed_integer_values.index(v)
                except ValueError:
                    self._signed_integer_values.append(v)
                    self._layer.attribute_pool.signed_integer_values.append(v)
                    return complex_value_integer(3, len(self._signed_integer_values) - 1)
            else:
                return complex_value_integer(6, zig_zag_encode_64(v))
        elif isinstance(v, Float):
            try:
                return self._float_values.index(v)
            except ValueError:
                self._float_values.append(v)
                self._layer.attribute_pool.float_values.append(v)
                return complex_value_integer(1, len(self._float_values) - 1)
        elif isinstance(v, float):
            try:
                return self._double_values.index(v)
            except ValueError:
                self._double_values.append(v)
                self._layer.attribute_pool.double_values.append(v)
                return complex_value_integer(2, len(self._double_values) - 1)
        elif isinstance(v,list):
            values, length = self._add_inline_list_attributes(v)
            if not values:
                return None
            values.insert(0, complex_value_integer(8, length))
            return values
        elif isinstance(v, dict):
            values, length = self._add_inline_map_attributes(v)
            if not values:
                return None
            values.insert(0, complex_value_integer(9, length))
            return values
        return None
    
    def _add_inline_list_attributes(self, attrs):
        complex_values = []
        length = len(attrs)
        remove = []
        for v in attrs:
            val = self._add_inline_value(v)
            if val is None:
                remove.append(v)
                continue
            if isinstance(val, list):
                complex_values.extend(val)
            else:
                complex_values.append(val)
        if remove:
            length = length - len(remove)
            data[:] = [x for x in data if x not in remove]
        return complex_values, length

    def _add_inline_map_attributes(self, attrs):
        complex_values = []
        length = len(attrs)
        remove = []
        for k,v in attrs.items():
            if not isinstance(k, str) and not isinstance(k, other_str):
                remove.append(k)
                continue
            val = self._add_inline_value(v)
            if val is None:
                remove.append(k)
                continue
            try:
                key_val = self._keys.index(k)
            except ValueError:
                self._layer.attribute_pool.keys.append(k)
                self._keys.append(k)
                key_val = len(self._keys) - 1
            complex_values.append(key_val)
            if isinstance(val, list):
                complex_values.extend(val)
            else:
                complex_values.append(val)
        length = length - len(remove)
        for k in remove:
            del attrs[k]
        return complex_values, length

    def add_attributes(self, attrs):
        if self._pool:
            values, length = self._add_inline_map_attributes(attrs)
            return values
        else:
            return self._add_legacy_attributes(attrs)

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

    def add_layer(self, name, version = None):
        self._layers.append(Layer(self._tile.layers.add(), name, version))
        return self._layers[-1]

    @property
    def layers(self):
        return self._layers
