vector-tile-base
================

This library encodes and decodes [Mapbox Vector Tiles](https://github.com/mapbox/vector-tile-spec). It is intended for use by developers with clear understanding of the Vector Tile format. The code is written as a pure python implementation with support of the google protobuf python format. 

## Depends

 - Google protobuf python bindings

## Development

Install the python locally with pip:

```
pip install -e .
```

To run tests use [pytest](https://docs.pytest.org/en/latest/):

```
pytest
```

## Example

Some very simple code examples

### Encode

```
import vector_tile_base

vt = vector_tile_base.VectorTile()
layer = vt.add_layer('my_locations')
feature = layer.add_point_feature()
feature.add_points([[10,10],[20,20]])
feature.id = 1
feature.properties = { 'type': 1, 'name': 'my_points' }

encoded_tile = vt.serialize()

```

### Decode

```
import vector_tile_base

raw_tile = open('tile.mvt', 'r').read()

vt = vector_tile_base.VectorTile(raw_tile)
for l in layers:
    print layer.name
    for f in features:
        print f.type
        print f.properties
        print f.get_geometry()
```

