from vector_tile_base import VectorTile, SplineFeature, PointFeature, PolygonFeature, LineStringFeature, Layer, FeatureProperties

f = open('tests/test.mvt', 'rb')
test_data = f.read()
f.close()

def test_decode_vector_tile():
    vt = VectorTile(test_data)
    expected_id = 2
    assert len(vt.layers) == 8
    
    # Test first layer
    layer = vt.layers[0]
    assert isinstance(layer, Layer)
    assert layer.name == 'points'
    assert layer.extent == 4096
    assert layer.dimensions == 2
    assert layer.version == 2
    assert len(layer.features) == 4
    # Test layer features
    for feature in layer.features:
        assert isinstance(feature, PointFeature)
        assert feature.type == 'point'
        assert feature.id == expected_id
        geometry = feature.get_points()
        assert geometry == feature.get_geometry()
        assert isinstance(geometry, list)
        assert len(geometry) == 1
        point = geometry[0]
        assert isinstance(point, list)
        assert len(point) == 2
        assert point[0] == 20
        assert point[1] == 20
        props = feature.properties
        assert isinstance(props, FeatureProperties)
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
    assert layer.dimensions == 2
    assert layer.version == 2
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, LineStringFeature)
    assert feature.type == 'line_string'
    assert feature.id == expected_id
    expected_id += 1
    geometry = feature.get_line_strings()
    assert geometry == feature.get_geometry()
    assert isinstance(geometry, list)
    assert len(geometry) == 2
    geometry == [[[10,10],[10,20],[20,20]],[[11,11],[12,13]]]
    props = feature.properties
    assert isinstance(props, FeatureProperties)
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
    assert layer.dimensions == 2
    assert layer.version == 2
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, PolygonFeature)
    assert feature.type == 'polygon'
    assert feature.id == expected_id
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
    props = feature.properties
    assert isinstance(props, FeatureProperties)
    assert len(props) == 1
    assert props['natural']
    assert props['natural'] == 'wood'

    # Test fourth layer
    layer = vt.layers[3]
    assert isinstance(layer, Layer)
    assert layer.name == 'splines'
    assert layer.extent == 4096
    assert layer.dimensions == 2
    assert layer.version == 2
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, SplineFeature)
    assert feature.type == 'spline'
    assert feature.id == expected_id
    expected_id += 1
    control_points = feature.get_control_points()
    assert isinstance(control_points, list)
    assert len(control_points) == 4
    assert control_points == [[8,10],[9,11],[11,9],[12,10]]
    knots = feature.get_knots()
    assert [control_points, knots] == feature.get_geometry()
    assert len(knots) == 7
    assert knots == [0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0]
    props = feature.properties
    assert isinstance(props, FeatureProperties)
    assert len(props) == 1
    assert props['natural']
    assert props['natural'] == 'curve'
    
    # Test fifth layer
    expected_id += 1
    layer = vt.layers[4]
    assert isinstance(layer, Layer)
    assert layer.name == 'points_3d'
    assert layer.extent == 4096
    assert layer.dimensions == 3
    assert layer.version == 2
    assert len(layer.features) == 4
    # Test layer features
    point_z = 10
    for feature in layer.features:
        assert isinstance(feature, PointFeature)
        assert feature.type == 'point'
        assert feature.id == expected_id
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
        props = feature.properties
        assert isinstance(props, FeatureProperties)
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
    assert layer.dimensions == 3
    assert layer.version == 2
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, LineStringFeature)
    assert feature.type == 'line_string'
    assert feature.id == expected_id
    expected_id += 1
    geometry = feature.get_line_strings()
    assert isinstance(geometry, list)
    assert len(geometry) == 2
    geometry == [[[10,10,10],[10,20,20],[20,20,30]],[[11,11,10],[12,13,20]]]
    props = feature.properties
    assert isinstance(props, FeatureProperties)
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
    assert layer.dimensions == 3
    assert layer.version == 2
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, PolygonFeature)
    assert feature.type == 'polygon'
    assert feature.id == expected_id
    expected_id += 1
    geometry = feature.get_rings()
    multi_polygons = feature.get_polygons()
    assert isinstance(geometry, list)
    assert isinstance(multi_polygons, list)
    assert len(multi_polygons) == 2
    assert geometry[0] == multi_polygons[0][0]
    assert geometry[1] == multi_polygons[1][0]
    assert len(geometry) == 2
    assert geometry == [[[0,0,10],[10,0,20],[10,10,30],[0,10,20],[0,0,10]],[[3,3,20],[3,5,40],[5,5,30],[3,3,20]]]
    props = feature.properties
    assert isinstance(props, FeatureProperties)
    assert len(props) == 1
    assert props['natural']
    assert props['natural'] == 'wood'

    # Test eighth layer
    layer = vt.layers[7]
    assert isinstance(layer, Layer)
    assert layer.name == 'splines_3d'
    assert layer.extent == 4096
    assert layer.dimensions == 3
    assert layer.version == 2
    assert len(layer.features) == 1
    # Test layer features
    feature = layer.features[0]
    assert isinstance(feature, SplineFeature)
    assert feature.type == 'spline'
    assert feature.id == expected_id
    expected_id += 1
    control_points = feature.get_control_points()
    assert isinstance(control_points, list)
    assert len(control_points) == 4
    assert control_points == [[8,10,10],[9,11,11],[11,9,12],[12,10,13]]
    knots = feature.get_knots()
    assert len(knots) == 7
    assert knots == [0.0, 0.0, 0.0, 1.0, 2.0, 2.0, 2.0]
    props = feature.properties
    assert isinstance(props, FeatureProperties)
    assert len(props) == 1
    assert props['natural']
    assert props['natural'] == 'curve'
