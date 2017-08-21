import pytest
from vector_tile_base import VectorTile, SplineFeature, PointFeature, PolygonFeature, LineStringFeature, Layer, FeatureProperties

def test_no_layers():
    vt = VectorTile()
    assert len(vt.serialize()) == 0

def test_create_layer():
    vt = VectorTile()
    layer = vt.add_layer('point')
    assert layer.name == 'point'
    assert layer.dimensions == 2
    assert layer.version == 2
    assert isinstance(layer, Layer)
    layer = vt.add_layer('point_3d', 3)
    assert layer.name == 'point_3d'
    assert layer.dimensions == 3
    assert layer.version == 2
    assert isinstance(layer, Layer)
    layer = vt.add_layer('point_4d', 4, 4)
    assert layer.name == 'point_4d'
    assert layer.dimensions == 4
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

def test_layer_dimensions():
    vt = VectorTile()
    layer = vt.add_layer('test')
    assert layer.dimensions == 2
    with pytest.raises(AttributeError):
        layer.dimensions = 3
    assert layer.dimensions == 2

def test_layer_features():
    vt = VectorTile()
    layer = vt.add_layer('test')
    assert len(layer.features) == 0
    assert isinstance(layer.features, list)
    with pytest.raises(AttributeError):
        layer.features = [1,2]
    assert len(layer.features) == 0

def test_feature_properties():
    vt = VectorTile()
    layer = vt.add_layer('test')
    feature = layer.add_point_feature()
    assert isinstance(feature, PointFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    prop = feature.properties
    assert isinstance(prop, FeatureProperties)
    assert feature.properties == {}
    assert prop == {}
    prop['fun'] = 'stuff'
    assert 'fun' in prop
    assert prop['fun'] == 'stuff'
    assert feature.properties['fun'] == 'stuff'
    assert feature.properties == {'fun':'stuff'}
    # Can set by external dictionary
    prop_dict = { 'number': 1, 'bool': True, 'string': 'foo', 'float': 4.1 }
    feature.properties = prop_dict
    assert feature.properties == prop_dict
    # Key error on not existant property
    with pytest.raises(KeyError):
        foo = feature.properties['doesnotexist']
    # Type errors on invalid key types
    with pytest.raises(TypeError):
        feature.properties[1.234] = True
    with pytest.raises(TypeError):
        feature.properties[1] = True
    with pytest.raises(TypeError):
        foo = feature.properties[1.234]
    with pytest.raises(TypeError):
        foo = feature.properties[1]
    # During setting invalid properties with bad keys or value types will just be dropped
    prop_dict = {'foo': [1,2,3], 'fee': [{'a':'b'}, {'a':['c','d']}], 1.2341: 'stuff', 1: 'fish', 'go': False }
    feature.properties = prop_dict
    assert feature.properties != prop_dict
    assert feature.properties == {'foo': [1,2,3], 'fee': [{'a':'b'}, {'a':['c','d']}], 'go': False }

def test_create_point_feature():
    vt = VectorTile()
    layer = vt.add_layer('test')
    feature = layer.add_point_feature()
    assert isinstance(feature, PointFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    feature.add_points([10,11])
    geometry = feature.get_points()
    assert geometry[0] == [10,11]
    # add points simply adds to end
    # BE WARNED THIS IS NOT IDEAL ENCODING -- use other example further below to achieve better results
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

def test_create_line_feature():
    vt = VectorTile()
    layer = vt.add_layer('test')
    feature = layer.add_line_string_feature()
    assert isinstance(feature, LineStringFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    line_string = [[10,11],[10,12],[10,13],[10,14]]
    feature.add_line_string(line_string)
    # note that we pull back possible multi line string here
    assert feature.get_line_strings() == [line_string]
    
    bad_line_string = [[1,1]]
    with pytest.raises(Exception):
        feature.add_line_string(bad_line_string)
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

def test_create_polygon_feature():
    vt = VectorTile()
    layer = vt.add_layer('test')
    feature = layer.add_polygon_feature()
    assert isinstance(feature, PolygonFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    polygon = [[[0,0],[10,0],[10,10],[0,10],[0,0]],[[3,3],[3,5],[5,5],[3,3]]]
    feature.add_ring(polygon[0])
    feature.add_ring(polygon[1])
    assert feature.get_rings() == polygon
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

def test_create_spline_feature():
    vt = VectorTile()
    layer = vt.add_layer('test')
    feature = layer.add_spline_feature()
    assert isinstance(feature, SplineFeature)
    assert len(layer.features) == 1
    assert feature == layer.features[0]
    control_points = [[8,10],[9,11],[11,9],[12,10]]
    knots = [0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0]
    feature.add_control_points(control_points)
    feature.add_knots(knots)

    assert feature.get_control_points() == control_points
    assert feature.get_knots() == knots
    
