import pytest
import os
from vector_tile_base import VectorTile

def load_vector_tile(name):
    divided = name.split('_')
    if divided[1] == 'invalid':
        name = '_'.join(divided[2:])
        filename = os.path.join('tests', 'data', 'invalid', name + '.mvt')
    elif divided[1] == 'valid':
        name = '_'.join(divided[2:])
        filename = os.path.join('tests', 'data', 'valid', name + '.mvt')
    else:
        name = '_'.join(divided[1:])
        filename = os.path.join('tests', 'data', name + '.mvt')
    f = open(filename, 'rb')
    test_data = f.read()
    f.close()
    return VectorTile(test_data)

@pytest.fixture()
def vt(request):
    if request.node.originalname is None:
        return load_vector_tile(request.node.name)
    else:
        return load_vector_tile(request.node.originalname)
