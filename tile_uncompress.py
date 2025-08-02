import lz4_apple
import lzo_decomp
import zipfile
import re
from raw_procreate_document import RawProcreateDocument

import asyncio
from PyQt5.QtWidgets import QProgressDialog

RE_CHUNK_FILE_POSITION = re.compile("(\d+)~(\d+)\.\w{3,5}$")

async def decompress_layer_data(zf : zipfile, blocks : list, procreate_doc : RawProcreateDocument, layer, progress : QProgressDialog, exceptions : list, async_lock : asyncio.Lock, krita_document, should_refresh = False, channels : int = 4):
    tile_size : int = procreate_doc.tileSize

    for block in blocks:
        block : zipfile.ZipInfo = block

        column, row = RE_CHUNK_FILE_POSITION.findall(block.filename)[0]
        x : int = int(row) * tile_size
        y : int = int(column) * tile_size
        w : int = min(x + tile_size, procreate_doc.clean_width) % tile_size
        h : int = min(y + tile_size, procreate_doc.clean_height) % tile_size

        w = tile_size if w == 0 else w
        h = tile_size if h == 0 else h

        decompressed : bytearray

        with zf.open(block.filename) as raw:
            match (block.filename.split(".")[-1]):
                case "lz4":
                    decompressed = lz4_apple.decompress(raw.read())
                    
                case "chunk":
                    # TODO: LZO decompression does not appear to be completely accurate
                    lzo_buffer = lzo_decomp.LZODecompressor(raw)
                    decompressed = bytearray(lzo_buffer.decompress())
                case _:
                    break
        
        if channels == 4:
            # thank you lily ilysm
            integer_view : memoryview = memoryview(decompressed).cast('I')
            for i in range(len(integer_view)):
                # Through trial and error this is the channel layout of the generic
                # sRGB as an integer.
                # A R G B
                if integer_view[i] & 0xff_00_00_00 == 0:
                    continue

                z = integer_view[i]
                integer_view[i] = (z & 0xff_00_ff_00) | (((z & 0x00_ff_00_00) >> 16)) | (((z & 0x00_00_00_ff)) << 16)

                if z & 0xff_00_00_00 == 0xff_00_00_00:
                    continue

                a = float((z & 0xff_00_00_00) >> 24) / 255.0
                r = float((z & 0xff_00_00) >> 16)
                g = float((z & 0xff_00) >> 8)
                b = float(z & 0xff)

                r = int(min(255, max(0, r / a)))
                g = int(min(255, max(0, g / a)))
                b = int(min(255, max(0, b / a)))

                integer_view[i] = (z & 0xff_00_00_00) | (b << 16) | (g << 8) | r
                
            integer_view.release()

        for i in range(w):
            position = channels * i * h
            async with async_lock:
                layer.setPixelData(decompressed[position:position+(channels * h)], x + i, y, 1, h)
        
        async with async_lock:
            progress.setValue(progress.value() + 1)
            if should_refresh:
                krita_document.refreshProjection()
