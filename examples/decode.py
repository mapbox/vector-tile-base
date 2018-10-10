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
