from vector_tile_base.engine import zig_zag_encode_64, zig_zag_encode, zig_zag_decode

def test_zig_zag_encode():
    assert zig_zag_encode(0) == 0
    assert zig_zag_encode(-1) == 1
    assert zig_zag_encode(1) == 2
    assert zig_zag_encode(-2) == 3
    assert zig_zag_encode(2) == 4
    assert zig_zag_encode(-((2**31)-1)) == 4294967293
    assert zig_zag_encode((2**31)-1) == 4294967294
    assert zig_zag_encode(-(2**31)) == 4294967295
    ## Fails after this value
    assert zig_zag_encode(2**31) != 4294967296

def test_zig_zag_encode_64():
    assert zig_zag_encode_64(0) == 0
    assert zig_zag_encode_64(-1) == 1
    assert zig_zag_encode_64(1) == 2
    assert zig_zag_encode_64(-2) == 3
    assert zig_zag_encode_64(2) == 4
    assert zig_zag_encode_64(-(2**31-1)) == 4294967293
    assert zig_zag_encode_64(2**31-1) == 4294967294
    assert zig_zag_encode_64(-(2**31)) == 4294967295
    assert zig_zag_encode_64(2**31) == 4294967296
    assert zig_zag_encode_64(-(2**63-1)) == 18446744073709551613
    assert zig_zag_encode_64(2**63-1) == 18446744073709551614
    assert zig_zag_encode_64(-(2**63)) == 18446744073709551615
    # Fails after this value
    assert zig_zag_encode_64(2**63) != 18446744073709551616

def test_zig_zag_decode():
    assert zig_zag_decode(0) == 0
    assert zig_zag_decode(1) == -1
    assert zig_zag_decode(2) == 1
    assert zig_zag_decode(3) == -2
    assert zig_zag_decode(4) == 2
    assert zig_zag_decode(4294967293) == -2147483647
    assert zig_zag_decode(4294967294) == 2147483647
    assert zig_zag_decode(4294967295) == -2147483648
    assert zig_zag_decode(4294967296) == 2147483648
    assert zig_zag_decode(18446744073709551613) == -9223372036854775807
    assert zig_zag_decode(18446744073709551614) == 9223372036854775807
    assert zig_zag_decode(18446744073709551615) == -9223372036854775808
    # Upper limit not the same due to implementation
    assert zig_zag_decode(18446744073709551616) == 9223372036854775808
    # show round trip fails before after the point
    assert zig_zag_encode_64(zig_zag_decode(18446744073709551615)) == 18446744073709551615
    assert zig_zag_encode_64(zig_zag_decode(18446744073709551616)) != 18446744073709551616
