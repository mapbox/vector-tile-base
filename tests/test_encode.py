import pytest
from vector_tile_base import VectorTile, CurveFeature, PointFeature, PolygonFeature, LineStringFeature, Layer, FeatureAttributes, Float

def test_no_layers():
    vt = VectorTile()
    assert len(vt.serialize()) == 0

def test_create_layer():
    vt = VectorTile()
    layer = vt.add_layer('point')
    assert layer.name == 'point'
    assert layer.version == 2
    assert isinstance(layer, Layer)
    layer = vt.add_layer('point_3', 3)
    assert layer.name == 'point_3'
    assert layer.version == 3
    assert isinstance(layer, Layer)
    layer = vt.add_layer('point_4', 4)
    assert layer.name == 'point_4'
    assert layer.version == 4
    assert isinstance(layer, Layer)

def test_layer_extent():
    vt = VectorTile()
    layer = vt.add_layer('test')
    assert layer.extent == 4096
    layer.extent = 8000
    assert layer.extent == 8000

def test_layer_name():
    vt = VectorTile()
    layer = vt.add_layer('test')
    assert layer.name == 'test'
    layer.name = 'foo'
    assert layer.name == 'foo'

def test_layer_features():
    vt = VectorTile()
    layer = vt.add_layer('test')
    assert len(layer.features) == 0
    assert isinstance(layer.features, list)
    with pytest.raises(AttributeError):
        layer.features = [1,2]
    assert len(layer.features) == 0

def test_feature_attributes_version_2():
    vt = VectorTile()
    layer = vt.add_layer('test', version=2)
    feature = layer.add_point_feature()
    assert isinstance(feature, PointFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    prop = feature.attributes
    assert isinstance(prop, FeatureAttributes)
    assert feature.attributes == {}
    assert prop == {}
    prop['fun'] = 'stuff'
    assert 'fun' in prop
    assert prop['fun'] == 'stuff'
    assert feature.attributes['fun'] == 'stuff'
    assert feature.attributes == {'fun':'stuff'}
    # Can set by external dictionary
    prop_dict = { 'number': 1, 'bool': True, 'string': 'foo', 'float': 4.1 }
    feature.attributes = prop_dict
    assert feature.attributes == prop_dict
    # Key error on not existant property
    with pytest.raises(KeyError):
        foo = feature.attributes['doesnotexist']
    # Type errors on invalid key types
    with pytest.raises(TypeError):
        feature.attributes[1.234] = True
    with pytest.raises(TypeError):
        feature.attributes[1] = True
    with pytest.raises(TypeError):
        foo = feature.attributes[1.234]
    with pytest.raises(TypeError):
        foo = feature.attributes[1]
    # During setting invalid attributes with bad keys or value types will just be dropped
    prop_dict = {'foo': [1,2,3], 'fee': [{'a':'b'}, {'a':['c','d']}], 1.2341: 'stuff', 1: 'fish', 'go': False, 'double': 2.32432, 'float': Float(23432.3222) }
    prop_dict2 = {'go': False, 'double': 2.32432, 'float': 23432.3222 }
    feature.attributes = prop_dict
    assert feature.attributes != prop_dict
    assert feature.attributes == prop_dict2
    
    # Now serialize the tile
    data = vt.serialize()
    # Reload as new tile to check that cursor moves to proper position for another add point
    vt = VectorTile(data)
    feature = vt.layers[0].features[0]
    assert feature.attributes['go'] == prop_dict2['go']
    assert feature.attributes['double'] == prop_dict2['double']
    # note change is expected due to float encoding!
    assert feature.attributes['float'] == 23432.322265625 

def test_feature_attributes_version_3():
    vt = VectorTile()
    layer = vt.add_layer('test', version=3)
    feature = layer.add_point_feature()
    assert isinstance(feature, PointFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    prop = feature.attributes
    assert isinstance(prop, FeatureAttributes)
    assert feature.attributes == {}
    assert prop == {}
    prop['fun'] = 'stuff'
    assert 'fun' in prop
    assert prop['fun'] == 'stuff'
    assert feature.attributes['fun'] == 'stuff'
    assert feature.attributes == {'fun':'stuff'}
    # Can set by external dictionary
    prop_dict = { 'number': 1, 'bool': True, 'string': 'foo', 'float': 4.1 }
    feature.attributes = prop_dict
    assert feature.attributes == prop_dict
    # Key error on not existant property
    with pytest.raises(KeyError):
        foo = feature.attributes['doesnotexist']
    # Type errors on invalid key types
    with pytest.raises(TypeError):
        feature.attributes[1.234] = True
    with pytest.raises(TypeError):
        feature.attributes[1] = True
    with pytest.raises(TypeError):
        foo = feature.attributes[1.234]
    with pytest.raises(TypeError):
        foo = feature.attributes[1]
    # During setting invalid attributes with bad keys or value types will just be dropped
    prop_dict = {'foo': [1,2,3], 'fee': [{'a':'b'}, {'a':['c','d']}], 1.2341: 'stuff', 1: 'fish', 'go': False, 'double': 2.32432, 'float': Float(23432.3222) }
    prop_dict2 = {'foo': [1,2,3], 'fee': [{'a':'b'}, {'a':['c','d']}], 'go': False, 'double': 2.32432, 'float': 23432.3222 }
    feature.attributes = prop_dict
    assert feature.attributes != prop_dict
    assert feature.attributes == prop_dict2
    
    # Now serialize the tile
    data = vt.serialize()
    # Reload as new tile to check that cursor moves to proper position for another add point
    vt = VectorTile(data)
    feature = vt.layers[0].features[0]
    assert feature.attributes['foo'] == prop_dict2['foo']
    assert feature.attributes['fee'] == prop_dict2['fee']
    assert feature.attributes['go'] == prop_dict2['go']
    assert feature.attributes['double'] == prop_dict2['double']
    # note change is expected due to float encoding!
    assert feature.attributes['float'] == 23432.322265625 

def test_create_point_feature():
    vt = VectorTile()
    layer = vt.add_layer('test')
    feature = layer.add_point_feature()
    assert isinstance(feature, PointFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    assert feature.dimensions == 2
    feature.add_points([10,11])
    geometry = feature.get_points()
    assert geometry[0] == [10,11]
    # add points simply adds to end
    feature.add_points([10,12])
    feature.add_points([10,13])
    geometry = feature.get_points()
    assert geometry[1] == [10,12]
    assert geometry[2] == [10,13]
    # clear current geometry
    feature.clear_geometry()
    assert feature.get_points() == []
    # This is proper way to add multiple points!
    feature.add_points([[10,11],[10,12],[10,13]])
    assert feature.get_points() == [[10,11],[10,12],[10,13]]

    # Now serialize the tile
    data = vt.serialize()
    # Reload as new tile to check that cursor moves to proper position for another add point
    vt = VectorTile(data)
    feature = vt.layers[0].features[0]
    feature.add_points([10,14])
    assert feature.get_points() == [[10,11],[10,12],[10,13],[10,14]]

def test_create_point_feature_3d():
    vt = VectorTile()
    layer = vt.add_layer('test')
    ## Should fail first because layer is a version 2 layer
    with pytest.raises(Exception):
        feature = layer.add_point_feature(dimensions=3)
    vt = VectorTile()
    layer = vt.add_layer('test', version=3)
    with pytest.raises(Exception):
        feature = layer.add_point_feature(dimensions=99)
    feature = layer.add_point_feature(dimensions=3)
    assert isinstance(feature, PointFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    assert feature.dimensions == 3
    ## Should fail to add 2 point list
    with pytest.raises(IndexError):
        feature.add_points([10,11])
    feature.add_points([10,11,12])
    geometry = feature.get_points()
    assert geometry[0] == [10,11,12]
    # add points simply adds to end
    feature.add_points([10,12,13])
    feature.add_points([10,13,14])
    geometry = feature.get_points()
    assert geometry[1] == [10,12,13]
    assert geometry[2] == [10,13,14]
    # clear current geometry
    feature.clear_geometry()
    assert feature.get_points() == []
    # This is proper way to add multiple points!
    feature.add_points([[10,11,12],[10,12,13],[10,13,14]])
    assert feature.get_points() == [[10,11,12],[10,12,13],[10,13,14]]

    # Now serialize the tile
    data = vt.serialize()
    # Reload as new tile to check that cursor moves to proper position for another add point
    vt = VectorTile(data)
    feature = vt.layers[0].features[0]
    feature.add_points([10,14,15])
    assert feature.get_points() == [[10,11,12],[10,12,13],[10,13,14],[10,14,15]]

def test_create_line_feature():
    vt = VectorTile()
    layer = vt.add_layer('test')
    feature = layer.add_line_string_feature()
    assert isinstance(feature, LineStringFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    assert feature.dimensions == 2
    line_string = [[10,11],[10,12],[10,13],[10,14]]
    feature.add_line_string(line_string)
    # note that we pull back possible multi line string here
    assert feature.get_line_strings() == [line_string]
    
    bad_line_string = [[1,1]]
    with pytest.raises(Exception):
        feature.add_line_string(bad_line_string)
    assert feature.get_line_strings() == [line_string]
    bad_line_string2 = [[1,1], [0]]
    with pytest.raises(IndexError):
        feature.add_line_string(bad_line_string2)
    assert feature.get_line_strings() == [line_string]

    line_string2 = [[9,9],[30,5]]
    feature.add_line_string(line_string2)
    assert feature.get_line_strings() == [line_string, line_string2]

    # clear current geometry
    feature.clear_geometry()
    assert feature.get_line_strings() == []
    feature.add_line_string(line_string)
    assert feature.get_line_strings() == [line_string]

    # Now serialize the tile
    data = vt.serialize()
    # Reload as new tile to check that cursor moves to proper position for another add point
    vt = VectorTile(data)
    feature = vt.layers[0].features[0]
    feature.add_line_string(line_string2)
    assert feature.get_line_strings() == [line_string, line_string2]

def test_create_line_feature_3d():
    vt = VectorTile()
    layer = vt.add_layer('test')
    # Should raise because is version 2 tile
    with pytest.raises(Exception):
        feature = layer.add_line_string_feature(dimensions=3)
    vt = VectorTile()
    layer = vt.add_layer('test', version=3)
    feature = layer.add_line_string_feature(dimensions=3)
    assert isinstance(feature, LineStringFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    assert feature.dimensions == 3
    line_string = [[10,11,12],[10,12,13],[10,13,14],[10,14,15]]
    feature.add_line_string(line_string)
    # note that we pull back possible multi line string here
    assert feature.get_line_strings() == [line_string]
    
    bad_line_string = [[1,1,1]]
    with pytest.raises(Exception):
        feature.add_line_string(bad_line_string)
    assert feature.get_line_strings() == [line_string]
    bad_line_string2 = [[1,1],[2,2]]
    with pytest.raises(IndexError):
        feature.add_line_string(bad_line_string2)
    assert feature.get_line_strings() == [line_string]

    line_string2 = [[9,9,9],[30,5,9]]
    feature.add_line_string(line_string2)
    assert feature.get_line_strings() == [line_string, line_string2]

    # clear current geometry
    feature.clear_geometry()
    assert feature.get_line_strings() == []
    feature.add_line_string(line_string)
    assert feature.get_line_strings() == [line_string]

    # Now serialize the tile
    data = vt.serialize()
    # Reload as new tile to check that cursor moves to proper position for another add point
    vt = VectorTile(data)
    feature = vt.layers[0].features[0]
    feature.add_line_string(line_string2)
    assert feature.get_line_strings() == [line_string, line_string2]

def test_create_polygon_feature():
    vt = VectorTile()
    layer = vt.add_layer('test')
    feature = layer.add_polygon_feature()
    assert isinstance(feature, PolygonFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    assert feature.dimensions == 2
    polygon = [[[0,0],[10,0],[10,10],[0,10],[0,0]],[[3,3],[3,5],[5,5],[3,3]]]
    feature.add_ring(polygon[0])
    feature.add_ring(polygon[1])
    assert feature.get_rings() == polygon
    assert feature.get_polygons() == [polygon]
    
    bad_ring1 = [[0,0],[1,0]]
    with pytest.raises(Exception):
        feature.add_ring(bad_ring)
    assert feature.get_polygons() == [polygon]
    
    bad_ring2 = [[0,0],[1,0],[0,0]]
    with pytest.raises(Exception):
        feature.add_ring(bad_ring2)
    assert feature.get_polygons() == [polygon]
    
    bad_ring3 = [[0,0],[1,0],[1,1],[1],[0,0]]
    with pytest.raises(IndexError):
        feature.add_ring(bad_ring3)
    assert feature.get_polygons() == [polygon]

    feature.add_ring(polygon[0])
    feature.add_ring(polygon[1])
    assert feature.get_polygons() == [polygon, polygon]

    # clear current geometry
    feature.clear_geometry()
    assert feature.get_rings() == []
    assert feature.get_polygons() == []

    # Add in opposite order
    feature.add_ring(polygon[1])
    feature.add_ring(polygon[0])
    assert feature.get_rings() == [polygon[1], polygon[0]]
    # First ring in wrong winding order so dropped from polygon output
    assert feature.get_polygons() == [[polygon[0]]]
    
    # clear current geometry
    feature.clear_geometry()
    assert feature.get_rings() == []
    assert feature.get_polygons() == []

    feature.add_ring(polygon[0])
    feature.add_ring(polygon[1])
    assert feature.get_rings() == polygon
    assert feature.get_polygons() == [polygon]
    
    # Now serialize the tile
    data = vt.serialize()
    # Reload as new tile to check that cursor moves to proper position for another add point
    vt = VectorTile(data)
    feature = vt.layers[0].features[0]
    assert feature.get_rings() == polygon
    assert feature.get_polygons() == [polygon]
    feature.add_ring(polygon[0])
    feature.add_ring(polygon[1])
    assert feature.get_polygons() == [polygon, polygon]

def test_create_polygon_feature_3d():
    vt = VectorTile()
    layer = vt.add_layer('test')
    # Should not be allowed with version 2 layer
    with pytest.raises(Exception):
        feature = layer.add_polygon_feature(dimensions=3)
    vt = VectorTile()
    layer = vt.add_layer('test', version=3)
    feature = layer.add_polygon_feature(dimensions=3)
    assert isinstance(feature, PolygonFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    assert feature.dimensions == 3
    polygon = [[[[0,0,1],[10,0,1],[10,10,1],[0,10,1],[0,0,1]]],[[[3,3,1],[3,5,1],[5,5,1],[3,3,1]]]]
    feature.add_ring(polygon[0][0])
    feature.add_ring(polygon[1][0])
    assert feature.get_rings() == [polygon[0][0], polygon[1][0]]
    assert feature.get_polygons() == polygon
    
    bad_ring1 = [[0,0,1],[1,0,1]]
    with pytest.raises(Exception):
        feature.add_ring(bad_ring)
    assert feature.get_polygons() == polygon
    
    bad_ring2 = [[0,0,1],[1,0,1],[0,0,1]]
    with pytest.raises(Exception):
        feature.add_ring(bad_ring2)
    assert feature.get_polygons() == polygon
    
    bad_ring3 = [[0,0,1],[1,0,1],[1,1,1],[1,1],[0,0,1]]
    with pytest.raises(IndexError):
        feature.add_ring(bad_ring3)
    assert feature.get_polygons() == polygon

    feature.add_ring(polygon[0][0])
    feature.add_ring(polygon[1][0])
    assert feature.get_polygons() == [polygon[0], polygon[1], polygon[0], polygon[1]]

    # clear current geometry
    feature.clear_geometry()
    assert feature.get_rings() == []
    assert feature.get_polygons() == []

    feature.add_ring(polygon[0][0])
    feature.add_ring(polygon[1][0])
    assert feature.get_rings() == [polygon[0][0], polygon[1][0]]
    assert feature.get_polygons() == polygon
    
    # Now serialize the tile
    data = vt.serialize()
    # Reload as new tile to check that cursor moves to proper position for another add point
    vt = VectorTile(data)
    feature = vt.layers[0].features[0]
    assert feature.get_rings() == [polygon[0][0], polygon[1][0]]
    assert feature.get_polygons() == polygon
    feature.add_ring(polygon[0][0])
    feature.add_ring(polygon[1][0])
    assert feature.get_polygons() == [polygon[0], polygon[1], polygon[0], polygon[1]]

def test_create_curve_feature_fail_v2():
    vt = VectorTile()
    layer = vt.add_layer('test')
    with pytest.raises(Exception):
        feature = layer.add_curve_feature()

def test_create_curve_feature():
    vt = VectorTile()
    layer = vt.add_layer('test', version=3)
    feature = layer.add_curve_feature()
    assert isinstance(feature, CurveFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    assert feature.dimensions == 2
    
    bad_control_points1 = [[8,10]]
    with pytest.raises(Exception):
        feature.add_control_points(bad_control_points1)
    bad_control_points2 = [[8,10],[9,11],[9],[12,10]]
    with pytest.raises(IndexError):
        feature.add_control_points(bad_control_points2)
    
    control_points = [[8,10],[9,11],[11,9],[12,10]]
    knots = [0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0]
    feature.add_control_points(control_points)
    feature.add_knots(knots)

    assert feature.get_control_points() == control_points
    assert feature.get_knots() == knots

def test_create_curve_feature_3d():
    vt = VectorTile()
    layer = vt.add_layer('test', version=3)
    feature = layer.add_curve_feature(dimensions=3)
    assert isinstance(feature, CurveFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    assert feature.dimensions == 3
    
    bad_control_points1 = [[8,10,1]]
    with pytest.raises(Exception):
        feature.add_control_points(bad_control_points1)
    bad_control_points2 = [[8,10,1],[9,11,1],[9,1],[12,10,1]]
    with pytest.raises(IndexError):
        feature.add_control_points(bad_control_points2)
    
    control_points = [[8,10,1],[9,11,1],[11,9,1],[12,10,1]]
    knots = [0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0]
    feature.add_control_points(control_points)
    feature.add_knots(knots)

    assert feature.get_control_points() == control_points
    assert feature.get_knots() == knots
