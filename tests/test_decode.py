from vector_tile_base import VectorTile, SplineFeature, PointFeature, PolygonFeature, LineStringFeature, Layer, FeatureAttributes, FloatList

def test_decode_vector_tile():
    # Uncomment next line to recreate test data
    #create_decode_test_fixture()
    f = open('tests/test.mvt', 'rb')
    test_data = f.read()
    f.close()
    vt = VectorTile(test_data)
    expected_id = 2
    assert len(vt.layers) == 8
    
    # Test first layer
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'points'
    assert layer.extent == 4096
    assert layer.version == 2
    assert layer.zoom == 4
    assert layer.x == 3
    assert layer.y == 2
    assert len(layer.features) == 4
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
        expected_id += 1
    
    # Test second layer
    layer = vt.layers[1]
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
    assert feature.id == expected_id
    assert not feature.has_elevation
    expected_id += 1
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
    
    # Test third layer
    layer = vt.layers[2]
    assert isinstance(layer, Layer)
    assert layer.name == 'polygons'
    assert layer.extent == 4096
    assert layer.version == 2
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, PolygonFeature)
    assert feature.type == 'polygon'
    assert feature.id == expected_id
    assert not feature.has_elevation
    expected_id += 1
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

    # Test fourth layer
    layer = vt.layers[3]
    assert isinstance(layer, Layer)
    assert layer.name == 'splines'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, SplineFeature)
    assert feature.type == 'spline'
    assert feature.id == expected_id
    assert not feature.has_elevation
    assert feature.degree == 3
    expected_id += 1
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
    
    # Test fifth layer
    expected_id += 1
    layer = vt.layers[4]
    assert isinstance(layer, Layer)
    assert layer.name == 'points_3d'
    assert layer.extent == 4096
    assert layer.version == 3
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
    
    # Test sixth layer
    layer = vt.layers[5]
    assert isinstance(layer, Layer)
    assert layer.name == 'lines_3d'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, LineStringFeature)
    assert feature.type == 'line_string'
    assert feature.id == expected_id
    assert feature.has_elevation
    expected_id += 1
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
    
    # Test seventh layer
    layer = vt.layers[6]
    assert isinstance(layer, Layer)
    assert layer.name == 'polygons_3d'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, PolygonFeature)
    assert feature.type == 'polygon'
    assert feature.id == expected_id
    assert feature.has_elevation
    expected_id += 1
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

    # Test eighth layer
    layer = vt.layers[7]
    assert isinstance(layer, Layer)
    assert layer.name == 'splines_3d'
    assert layer.extent == 4096
    assert layer.version == 3
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, SplineFeature)
    assert feature.type == 'spline'
    assert feature.id == expected_id
    assert feature.has_elevation
    assert feature.degree == 3
    expected_id += 1
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

def create_decode_test_fixture():
    vt = VectorTile()
    # layer 0
    layer = vt.add_layer('points', version=2)
    layer.set_tile_location(zoom=4, x=3, y=2)
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
    #layer 1
    layer = vt.add_layer('lines', version=2)
    feature = layer.add_line_string_feature(has_elevation=False)
    feature.id = 6
    feature.add_line_string([[10,10],[10,20],[20,20]])
    feature.add_line_string([[11,11],[12,13]])
    feature.attributes = { 'highway': 'primary', 'maxspeed': 50 }
    #layer 2
    layer = vt.add_layer('polygons', version=2)
    feature = layer.add_polygon_feature(has_elevation=False)
    feature.id = 7
    feature.add_ring([[0,0],[10,0],[10,10],[0,10],[0,0]])
    feature.add_ring([[3,3],[3,5],[5,5],[3,3]])
    feature.attributes = { 'natural': 'wood' }
    #layer 3
    layer = vt.add_layer('splines', version=3)
    feature = layer.add_spline_feature(has_elevation=False, degree=3)
    feature.id = 8
    scaling = layer.add_attribute_scaling(precision=10.0**-8, min_value=0.0, max_value=25.0)
    knots = FloatList(scaling, [0.0, 2.0, 3.0, 4.0, 5.875, 6.0, 7.0, 8.0])
    feature.add_spline([[8,10],[9,11],[11,9],[12,10]], knots)
    feature.attributes = { 'natural': 'spline' }
    # layer 4
    layer = vt.add_layer('points_3d', version=3)
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
    #layer 5
    layer = vt.add_layer('lines_3d', version=3)
    feature = layer.add_line_string_feature(has_elevation=True)
    feature.id = 14
    feature.add_line_string([[10,10,10],[10,20,20],[20,20,30]])
    feature.add_line_string([[11,11,10],[12,13,20]])
    feature.attributes = { 'highway': 'primary', 'maxspeed': 50 }
    #layer 6
    layer = vt.add_layer('polygons_3d', version=3)
    feature = layer.add_polygon_feature(has_elevation=True)
    feature.id = 15
    feature.add_ring([[0,0,10],[10,0,20],[10,10,30],[0,10,20],[0,0,10]])
    feature.add_ring([[3,3,20],[3,5,40],[5,5,30],[3,3,20]])
    feature.attributes = { 'natural': 'wood' }
    #layer 7
    layer = vt.add_layer('splines_3d', version=3)
    feature = layer.add_spline_feature(has_elevation=True, degree=3)
    feature.id = 16
    scaling = layer.add_attribute_scaling(precision=10.0**-8, min_value=0.0, max_value=25.0)
    knots = FloatList(scaling, [0.0, 2.0, 3.0, 4.0, 5.875, 6.0, 7.0, 8.0])
    feature.add_spline([[8,10,10],[9,11,11],[11,9,12],[12,10,13]], knots)
    feature.attributes = { 'natural': 'spline' }
    f = open('tests/test.mvt', 'wb')
    f.write(vt.serialize())
    f.close()
