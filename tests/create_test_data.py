from vector_tile_base import *
import os
import sys

# To create a new test fixture create a method
# that starts with "create_" and returns a string
# of a vector tile buffer. This will be saved to a
# file in the test/data/ folder using the name of
# the method provided. The next name after "create_"
# can be be "valid" or "invalid" changing the
# destination folder in which the data is saved. If
# it is not set no folder is assigned.

# Example 1: 
# def create_valid_point_a() will create a file
# named test/data/valid/point_a.mvt
# Example 2: 
# def create_invalid_stuff() will create a file
# named test/data/invalid/stuff.mvt
# Example 3: 
# def create_wild() will create a file
# named test/data/wild.mvt

def create_valid_single_layer_v2_points():
    vt = VectorTile()
    # layer 0
    layer = vt.add_layer('points', version=2)
    feature = layer.add_point_feature(has_elevation=False)
    feature.id = 2
    feature.add_points([20,20])
    feature.attributes = { 'some': 'attr' }
    feature = layer.add_point_feature(has_elevation=False)
    feature.id = 3
    feature.add_points([20,20])
    feature.attributes = { 'some': 'attr' }
    feature = layer.add_point_feature(has_elevation=False)
    feature.id = 4
    feature.add_points([20,20])
    feature.attributes = { 'some': 'otherattr' }
    feature = layer.add_point_feature(has_elevation=False)
    feature.id = 5
    feature.add_points([20,20])
    feature.attributes = { 'otherkey': 'attr' }
    return vt.serialize()

def create_valid_single_layer_v2_linestring():
    vt = VectorTile()
    layer = vt.add_layer('lines', version=2)
    feature = layer.add_line_string_feature(has_elevation=False)
    feature.id = 6
    feature.add_line_string([[10,10],[10,20],[20,20]])
    feature.add_line_string([[11,11],[12,13]])
    feature.attributes = { 'highway': 'primary', 'maxspeed': 50 }
    return vt.serialize()

def create_valid_single_layer_v2_polygon():
    vt = VectorTile()
    layer = vt.add_layer('polygons', version=2)
    feature = layer.add_polygon_feature(has_elevation=False)
    feature.id = 7
    feature.add_ring([[0,0],[10,0],[10,10],[0,10],[0,0]])
    feature.add_ring([[3,3],[3,5],[5,5],[3,3]])
    feature.attributes = { 'natural': 'wood' }
    return vt.serialize()

def create_valid_single_layer_v3_spline():
    vt = VectorTile()
    layer = vt.add_layer('splines', version=3)
    feature = layer.add_spline_feature(has_elevation=False, degree=3)
    feature.id = 8
    scaling = layer.add_attribute_scaling(precision=10.0**-8, min_value=0.0, max_value=25.0)
    knots = FloatList(scaling, [0.0, 2.0, 3.0, 4.0, 5.875, 6.0, 7.0, 8.0])
    feature.add_spline([[8,10],[9,11],[11,9],[12,10]], knots)
    feature.attributes = { 'natural': 'spline' }
    return vt.serialize()

def create_valid_single_layer_v3_points_3d():
    vt = VectorTile()
    layer = vt.add_layer('points_3d', version=3)
    layer.set_tile_location(zoom=4, x=3, y=2)
    feature = layer.add_point_feature(has_elevation=True)
    feature.id = 10
    feature.add_points([20,20,10])
    feature.attributes = { 'some': 'attr' }
    feature = layer.add_point_feature(has_elevation=True)
    feature.id = 11
    feature.add_points([20,20,20])
    feature.attributes = { 'some': 'attr' }
    feature = layer.add_point_feature(has_elevation=True)
    feature.id = 12
    feature.add_points([20,20,30])
    feature.attributes = { 'some': 'otherattr' }
    feature = layer.add_point_feature(has_elevation=True)
    feature.id = 13
    feature.add_points([20,20,40])
    feature.attributes = { 'otherkey': 'attr' }
    return vt.serialize()

def create_valid_single_layer_v3_linestring_3d():
    vt = VectorTile()
    layer = vt.add_layer('lines_3d', version=3)
    feature = layer.add_line_string_feature(has_elevation=True)
    feature.id = 14
    feature.add_line_string([[10,10,10],[10,20,20],[20,20,30]])
    feature.add_line_string([[11,11,10],[12,13,20]])
    feature.attributes = { 'highway': 'primary', 'maxspeed': 50 }
    return vt.serialize()

def create_invalid_single_layer_v3_polygon_3d():
    vt = VectorTile()
    layer = vt.add_layer('polygons_3d', version=3)
    feature = layer.add_polygon_feature(has_elevation=True)
    feature.id = 15
    feature.add_ring([[0,0,10],[10,0,20],[10,10,30],[0,10,20],[0,0,10]])
    feature.add_ring([[3,3,20],[3,5,40],[5,5,30],[3,3,20]])
    feature.attributes = { 'natural': 'wood' }
    return vt.serialize()

def create_valid_single_layer_v3_spline_3d():
    vt = VectorTile()
    layer = vt.add_layer('splines_3d', version=3)
    feature = layer.add_spline_feature(has_elevation=True, degree=3)
    feature.id = 16
    scaling = layer.add_attribute_scaling(precision=10.0**-8, min_value=0.0, max_value=25.0)
    knots = FloatList(scaling, [0.0, 2.0, 3.0, 4.0, 5.875, 6.0, 7.0, 8.0])
    feature.add_spline([[8,10,10],[9,11,11],[11,9,12],[12,10,13]], knots)
    feature.attributes = { 'natural': 'spline' }
    return vt.serialize()

def create_valid_all_attribute_types_v3():
    vt = VectorTile()
    layer = vt.add_layer('example', version=3)
    scaling = layer.add_attribute_scaling(precision=10.0**-8, min_value=0.0, max_value=25.0)
    feature = layer.add_point_feature()
    feature.id = 1
    feature.add_points([20,20])
    feature.attributes = {
        'bool_true': True,
        'bool_false': False,
        'null': None,
        'string': 'a_string',
        'float': Float(1.0),
        'double': 2.0,
        'inline_uint': UInt(1),
        'inline_sint': -1,
        'uint': UInt(2**60),
        'int': -2**60,
        'dlist': FloatList(scaling, [1.0, 2.0, 3.0, 3.5, 4.5, 6.9]),
        'map': {'key1': 1, 'nested_map': { 'key': 1 }, 'nested_list': [1, 2, 3]},
        'list': [True, False, None, 'a_string', Float(1.0), 2.0, UInt(1), -1, UInt(2**60), -2**60, {'key1': 1}, [1,2,3],FloatList(scaling, [1.0, 2.0, 3.0, 3.5, 4.5, 6.9])]  
    }
    return vt.serialize()

def write_test_file(data, name, folder):
    if folder is None:
        filename = os.path.join('tests', 'data', name + '.mvt')
    else:
        filename = os.path.join('tests', 'data', folder, name + '.mvt')
    f = open(filename, 'wb')
    f.write(data)
    f.close()

def run_all_creates():
    a = sys.modules[__name__]
    for i in dir(a):
        item = getattr(a,i)
        if callable(item) and i.startswith('create'):
            data = item()
            divided = i.split('_')
            if divided[1] == 'invalid':
                folder = 'invalid'
                name = '_'.join(divided[2:])
            elif divided[1] == 'valid':
                folder = 'valid'
                name = '_'.join(divided[2:])
            else:
                folder = None
                name = '_'.join(divided[1:])
            write_test_file(data, name, folder)

if __name__ == '__main__':
    run_all_creates()
