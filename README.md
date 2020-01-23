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

There is an example encoding provided in `examples` and can be used to ecode a `.mvt` file.

```
python examples/encode.py my.mvt
```

```
import vector_tile_base
import sys

vt = vector_tile_base.VectorTile()
layer = vt.add_layer('my_locations')
feature = layer.add_point_feature()
feature.add_points([[10,10],[20,20]])
feature.id = 1
feature.properties = { 'type': 1, 'name': 'my_points' }

encoded_tile = vt.serialize()

f = open(sys.argv[1], "wb")
f.write(encoded_tile)
f.close()
```

### Decode

There is an example decoding provided in `examples` and can be used to decode a `.mvt` file.

```
python examples/decode.py my.mvt
```

```
import vector_tile_base
import sys

f = open(sys.argv[1], "rb")
raw_tile = f.read()
f.close()

vt = vector_tile_base.VectorTile(raw_tile)
for l in vt.layers:
    print(l.name)
    for f in l.features:
        print(f.type)
        print(f.attributes)
        print(f.get_geometry())
```

