from vector_tile_base import VectorTile, SplineFeature, PointFeature, PolygonFeature, LineStringFeature, Layer, FeatureAttributes, FloatList

def test_valid_single_layer_v2_points(vt):
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'points'
    assert layer.extent == 4096
    assert layer.version == 2
    assert len(layer.features) == 4
    expected_id = 2
    # Test layer features
    for feature in layer.features:
        assert isinstance(feature, PointFeature)
        assert feature.type == 'point'
        assert feature.id == expected_id
        assert not feature.has_elevation
        geometry = feature.get_points()
        assert geometry == feature.get_geometry()
        assert isinstance(geometry, list)
        assert len(geometry) == 1
        point = geometry[0]
        assert isinstance(point, list)
        assert len(point) == 2
        assert point[0] == 20
        assert point[1] == 20
        props = feature.attributes
        assert isinstance(props, FeatureAttributes)
        assert len(props) == 1
        if expected_id == 2:
            assert props['some']
            assert props['some'] == 'attr'
        elif expected_id == 3:
            assert props['some']
            assert props['some'] == 'attr'
        elif expected_id == 4:
            assert props['some']
            assert props['some'] == 'otherattr'
        elif expected_id == 5:
            assert props['otherkey']
            assert props['otherkey'] == 'attr'
        expected_id = expected_id + 1

def test_valid_single_layer_v2_linestring(vt):
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'lines'
    assert layer.extent == 4096
    assert layer.version == 2
    assert layer.zoom == None
    assert layer.x == None
    assert layer.y == None
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, LineStringFeature)
    assert feature.type == 'line_string'
    assert feature.id == 6
    assert not feature.has_elevation
    geometry = feature.get_line_strings()
    assert geometry == feature.get_geometry()
    assert isinstance(geometry, list)
    assert len(geometry) == 2
    geometry == [[[10,10],[10,20],[20,20]],[[11,11],[12,13]]]
    props = feature.attributes
    assert isinstance(props, FeatureAttributes)
    assert len(props) == 2
    assert props['highway']
    assert props['highway'] == 'primary'
    assert props['maxspeed']
    assert props['maxspeed'] == 50

def test_valid_single_layer_v2_polygon(vt):
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'polygons'
    assert layer.extent == 4096
    assert layer.version == 2
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, PolygonFeature)
    assert feature.type == 'polygon'
    assert feature.id == 7
    assert not feature.has_elevation
    geometry = feature.get_rings()
    multi_polygons = feature.get_polygons()
    assert multi_polygons == feature.get_geometry()
    assert isinstance(geometry, list)
    assert isinstance(multi_polygons, list)
    assert len(multi_polygons) == 1
    assert geometry == multi_polygons[0]
    assert len(geometry) == 2
    assert geometry == [[[0,0],[10,0],[10,10],[0,10],[0,0]],[[3,3],[3,5],[5,5],[3,3]]]
    props = feature.attributes
    assert isinstance(props, FeatureAttributes)
    assert len(props) == 1
    assert props['natural']
    assert props['natural'] == 'wood'

def test_valid_single_layer_v3_spline(vt):
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'splines'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, SplineFeature)
    assert feature.type == 'spline'
    assert feature.id == 8
    assert not feature.has_elevation
    assert feature.degree == 3
    splines = feature.get_splines()
    assert isinstance(splines, list)
    assert len(splines) == 1
    assert len(splines[0]) == 2
    control_points = splines[0][0]
    assert isinstance(control_points, list)
    assert len(control_points) == 4
    assert control_points == [[8,10],[9,11],[11,9],[12,10]]
    knots = splines[0][1]
    assert [[control_points, knots]] == feature.get_geometry()
    assert len(knots) == 8
    assert knots == [0.0, 2.0, 3.0, 4.0, 5.875, 6.0, 7.0, 8.0]
    props = feature.attributes
    assert isinstance(props, FeatureAttributes)
    assert len(props) == 1
    assert props['natural']
    assert props['natural'] == 'spline'

def test_valid_single_layer_v3_points_3d(vt):
    expected_id = 10
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'points_3d'
    assert layer.extent == 4096
    assert layer.version == 3
    assert layer.zoom == 4
    assert layer.x == 3
    assert layer.y == 2
    assert len(layer.features) == 4
    # Test layer features
    point_z = 10
    for feature in layer.features:
        assert isinstance(feature, PointFeature)
        assert feature.type == 'point'
        assert feature.id == expected_id
        assert feature.has_elevation
        geometry = feature.get_points()
        assert isinstance(geometry, list)
        assert len(geometry) == 1
        point = geometry[0]
        assert isinstance(point, list)
        assert len(point) == 3
        assert point[0] == 20
        assert point[1] == 20
        assert point[2] == point_z
        point_z += 10
        props = feature.attributes
        assert isinstance(props, FeatureAttributes)
        assert len(props) == 1
        if expected_id == 2:
            assert props['some']
            assert props['some'] == 'attr'
        elif expected_id == 3:
            assert props['some']
            assert props['some'] == 'attr'
        elif expected_id == 4:
            assert props['some']
            assert props['some'] == 'otherattr'
        elif expected_id == 5:
            assert props['otherkey']
            assert props['otherkey'] == 'attr'
        expected_id += 1

def test_valid_single_layer_v3_linestring_3d(vt):
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'lines_3d'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, LineStringFeature)
    assert feature.type == 'line_string'
    assert feature.id == 14
    assert feature.has_elevation
    geometry = feature.get_line_strings()
    assert isinstance(geometry, list)
    assert len(geometry) == 2
    geometry == [[[10,10,10],[10,20,20],[20,20,30]],[[11,11,10],[12,13,20]]]
    props = feature.attributes
    assert isinstance(props, FeatureAttributes)
    assert len(props) == 2
    assert props['highway']
    assert props['highway'] == 'primary'
    assert props['maxspeed']
    assert props['maxspeed'] == 50

def test_invalid_single_layer_v3_polygon_3d(vt):
    # This test is officially invalid currently,
    # because polygons in 3d are undefined, but
    # the decoder will handle it just fine.
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'polygons_3d'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, PolygonFeature)
    assert feature.type == 'polygon'
    assert feature.id == 15
    assert feature.has_elevation
    geometry = feature.get_rings()
    multi_polygons = feature.get_polygons()
    assert isinstance(geometry, list)
    assert isinstance(multi_polygons, list)
    assert len(multi_polygons) == 1
    assert geometry == multi_polygons[0]
    assert len(geometry) == 2
    assert geometry == [[[0,0,10],[10,0,20],[10,10,30],[0,10,20],[0,0,10]],[[3,3,20],[3,5,40],[5,5,30],[3,3,20]]]
    props = feature.attributes
    assert isinstance(props, FeatureAttributes)
    assert len(props) == 1
    assert props['natural']
    assert props['natural'] == 'wood'

def test_valid_single_layer_v3_spline_3d(vt):
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'splines_3d'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, SplineFeature)
    assert feature.type == 'spline'
    assert feature.id == 16
    assert feature.has_elevation
    assert feature.degree == 3
    splines = feature.get_splines()
    assert isinstance(splines, list)
    assert len(splines) == 1
    assert len(splines[0]) == 2
    control_points = splines[0][0]
    assert isinstance(control_points, list)
    assert len(control_points) == 4
    assert control_points == [[8,10,10],[9,11,11],[11,9,12],[12,10,13]]
    knots = splines[0][1]
    assert [[control_points, knots]] == feature.get_geometry()
    assert len(knots) == 8
    assert knots == [0.0, 2.0, 3.0, 4.0, 5.875, 6.0, 7.0, 8.0]
    props = feature.attributes
    assert isinstance(props, FeatureAttributes)
    assert len(props) == 1
    assert props['natural']
    assert props['natural'] == 'spline'

def test_valid_all_attribute_types_v3(vt):
    assert len(vt.layers) == 1
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'example'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    feature = layer.features[0]
    assert isinstance(feature, PointFeature)
    assert feature.type == 'point'
    assert feature.id == 1
    expected_attributes = {
        'bool_true': True,
        'bool_false': False,
        'null': None,
        'string': 'a_string',
        'float': 1.0,
        'double': 2.0,
        'inline_uint': 1,
        'inline_sint': -1,
        'uint': 2**60,
        'int': -2**60,
        'dlist': [1.0, 2.0, 3.0, 3.5, 4.5, 6.899999998509884],
        'map': {'key1': 1, 'nested_map': { 'key': 1 }, 'nested_list': [1, 2, 3]},
        'list': [True, False, None, 'a_string', 1.0, 2.0, 1, -1, 2**60, -2**60, {'key1': 1}, [1,2,3], [1.0, 2.0, 3.0, 3.5, 4.5, 6.899999998509884]]
    }
    assert feature.attributes == expected_attributes

