import io
import lz4

# Reference:
# https://developer.apple.com/documentation/compression/compression_algorithm/compression_lz4
def decompress(src : bytearray) -> bytearray:
    src : io.BytesIO = io.BytesIO(src)
    dst : bytearray = bytearray()

    working : bool = True
    plaintext : bytearray = bytearray()
    header : bytes

    while working:
        header = src.read(4)
        match header:

            # Compressed block header
            case b'\x62\x76\x34\x31':
                decoded_size : int = int.from_bytes(src.read(4), byteorder='little', signed=False)
                encoded_size : int = int.from_bytes(src.read(4), byteorder='little', signed=False)
                compressed_data : bytes = src.read(encoded_size)
                plaintext = lz4.uncompress(compressed_data, dst)

            # Uncompressed block header
            case b'\x62\x76\x34\x2d':
                size : int = int.from_bytes(src.read(4), byteorder='little', signed=False)
                plaintext = bytearray(src.read(size))

            # End of stream
            case b'\x62\x76\x34\x24':
                working = False
                break
        
        dst.extend(plaintext)
        plaintext = bytearray()
    
    return dst