import vector_tile_base
import sys

vt = vector_tile_base.VectorTile()
layer = vt.add_layer('my_locations')
feature = layer.add_point_feature()
feature.add_points([[10,10],[20,20]])
feature.id = 1
feature.attributes = { 'type': 1, 'name': 'my_points' }

encoded_tile = vt.serialize()

f = open(sys.argv[1], "wb")
f.write(encoded_tile)
f.close()
