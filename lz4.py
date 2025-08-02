# Copyright 2016,2020 Jan Kneschke <jan@kneschke.de>, 2024 Xubiod
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# SPDX-License-Identifier: MIT

from io import BytesIO


class CorruptError(Exception):
    pass


def uncompress(src, previous : bytearray | None = None):
    """Uncompress a block of lz4 data.
    
    Slightly modified by Xubiod from Jan Kneschke's original to implement changes
    used by Apple APIs.

    :param bytes src: LZ4 compressed data (LZ4 Blocks) as bytes-like or io.BytesIO
    :param bytearray previous: Previous plaintext if it exists, can be None
    :returns: uncompressed data
    :rtype: bytearray

    .. seealso:: http://cyan4973.github.io/lz4/lz4_Block_format.html
    """
    
    if type(src) is not BytesIO:    # Change by xubiod, check if already BytesIO.
        src = BytesIO(src)

    # if we have the original size, we could pre-allocate the buffer with
    # bytearray(original_size), but then we would have to use indexing
    # instad of .append() and .extend()
    dst = bytearray()
    
    # Changes by xubiod.
    dst_new : int = 0
    if previous is not None:
        dst.extend(previous)
        dst_new = len(previous)
    # End of changes

    min_match_len = 4

    def byte2int(bs):
        if type(bs[0]) is int:
            return bs[0]
        return ord(bs[0])

    def get_length(src, length):
        """get the length of a lz4 variable length integer."""
        if length != 0x0f:
            return length

        while True:
            read_buf = src.read(1)
            if len(read_buf) != 1:
                raise CorruptError("EOF at length read")
            len_part = byte2int(read_buf)

            length += len_part

            if len_part != 0xff:
                break

        return length

    while True:
        # decode a block
        read_buf = src.read(1)
        if len(read_buf) == 0:
            raise CorruptError("EOF at reading literal-len")
        token = byte2int(read_buf)

        literal_len = get_length(src, (token >> 4) & 0x0f)

        # copy the literal to the output buffer
        read_buf = src.read(literal_len)

        if len(read_buf) != literal_len:
            raise CorruptError("not literal data")
        dst.extend(read_buf)

        read_buf = src.read(2)
        if len(read_buf) == 0:
            if token & 0x0f != 0:
                raise CorruptError("EOF, but match-len > 0: %u" % (token % 0x0f, ))
            break

        if len(read_buf) != 2:
            raise CorruptError("premature EOF")

        offset = byte2int([read_buf[0]]) | (byte2int([read_buf[1]]) << 8)

        if offset == 0:
            raise CorruptError("offset can't be 0")

        match_len = get_length(src, (token >> 0) & 0x0f)
        match_len += min_match_len

        # append the sliding window of the previous literals
        for _ in range(match_len):
            dst.append(dst[-offset])

    return dst[dst_new:] # Changed by xubiod