#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# lzo_decomp.py
#
# Author:   Toke Høiland-Jørgensen (toke@toke.dk)
# Date:     13 August 2019
# Copyright (c) 2019, Toke Høiland-Jørgensen
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import struct
# import logging

# logging.basicConfig(level=logging.DEBUG)

# logger = logging.getLogger("lzo")


class LZOError(Exception):
    pass


class EOFError(LZOError):
    pass


class FormatError(LZOError):
    pass


class LZODecompressor:

    def __init__(self, instream):
        self.instream = instream
        self.pos = 0
        self.output = b''
        self.read_buf = b''
        self.trailing_bytes = 0

    def read_bytes(self, length):
        # logger.debug("Reading %d bytes", length)
        while len(self.read_buf) < length:
            b = self.instream.read(length - len(self.read_buf))
            if b is None:
                continue  # No bytes at the moment
            if not len(b):
                raise EOFError("EOF at pos %d" % (self.pos + len(self.read_buf)))
            self.read_buf += b

        output = self.read_buf[:length]
        self.read_buf = self.read_buf[length:]
        self.pos += len(output)
        return output

    def read_1(self):
        return struct.unpack("B", self.read_bytes(1))[0]

    def read_le16(self):
        return struct.unpack("<H", self.read_bytes(2))[0]

    def process_first_byte(self):
        val = self.read_1()
        # logger.debug("First byte is 0x%x", val)
        if val == 0x10:
            raise FormatError("LZOv1")
        elif val < 0x12:
            return self.process_instruction(val)

        self.copy_literal(val - 0x11)
        return True

    def copy_literal(self, length):
        if not length:
            return
        # logger.debug("Copying %d literal bytes at pos %d", length, self.pos)
        self.output += self.read_bytes(length)

    def copy_block(self, length, distance, trailing):
        orig_len = length
        if distance > len(self.output):
            raise LZOError("Distance %d > bufsize %d" % (distance,
                                                         len(self.output)))
        # logger.debug("Copying %d bytes from dict at distance %d", length,
        #              distance)
        block = self.output[-distance:]
        length -= len(block)
        while length > 0:
            assert length > 0
            # logger.debug("Block %s remaining length %d", block, length)
            add = block[:length]
            length -= len(add)
            block += add

        self.output += block[:orig_len]
        # logger.debug(f"Ended with block {block} len {len(block)} output now {len(self.output)} bytes")
        self.copy_literal(trailing)
        self.trailing_bytes = trailing

    def count_zeroes(self):
        length = 0
        val = self.read_1()
        while val == 0:
            length += 255
            val = self.read_1()
            if length > 2**20:
                raise LZOError("Too many zeroes")

        # logger.debug("Counted zeroes to length %d", length + val)
        return length + val

    def process_instruction(self, val):
        # logger.debug("Processing instruction 0x%x", val)
        if val <= 0xf:
            if not self.trailing_bytes:
                if val == 0:
                    self.copy_literal(self.count_zeroes() + 18)
                else:
                    self.copy_literal(val + 3)
            else:
                h = self.read_1()
                dist = (h << 2) + (val >> 2) + 1
                length = 2
                self.copy_block(length, dist, val & 3)
        elif val <= 0x1f:
            if val & 7 == 0:
                length = 9 + self.count_zeroes()
            else:
                length = (val & 7) + 2
            ds = self.read_le16()
            dist = 16384 + ((val & 8) >> 3) + (ds >> 2)
            # logger.debug("ds %d len %d dist %d", ds, length, dist)
            if dist == 16384:
                # logger.debug("Ret false")
                return False
            self.copy_block(length, dist, ds & 3)
        elif val <= 0x3f:
            length = val & 31
            if length == 0:
                length = self.count_zeroes() + 31

            length += 2
            ds = self.read_le16()
            dist = 1 + (ds >> 2)
            self.copy_block(length, dist, ds & 3)
        else:
            if val <= 0x7f:
                length = 3 + ((val >> 5) & 1)
            else:
                length = 5 + ((val >> 5) & 3)
            h = self.read_1()
            d = (val >> 2) & 7
            dist = (h << 3) + d + 1
            self.copy_block(length, dist, val & 3)

        return True

    def decompress(self):
        try:
            if self.process_first_byte():
                while self.process_instruction(self.read_1()):
                    pass

            return self.output
        except LZOError as e:
            raise e
            return b''
