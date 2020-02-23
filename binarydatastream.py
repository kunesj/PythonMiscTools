#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import io
from typing import Union, Iterable


class BinaryDataStream(io.BytesIO):
    """
    Extends io.BytesIO
    Class for reading specific variable types from binary data stream.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.byte_order = '<'  # little-endian, default on X86/x86_64
        self.string_encoding = 'ascii'

    def get_length(self) -> int:
        """ Returns length of stream """
        last_pos = self.tell()
        self.seek(0x0, io.SEEK_END)  # seek EOF
        length = self.tell()
        self.seek(last_pos, io.SEEK_SET)
        return length

    def set_byte_order(self, byte_order: str) -> None:
        """
        Set byte order of binary data in stream.

        Character   Byte order              Size        Alignment
        @           native                  native      native
        =           native                  standard    none
        <           little-endian           standard    none
        >           big-endian              standard    none
        !           network (= big-endian)  standard    none
        """
        if byte_order in ['@', '=', '<', '>', '!']:
            self.byte_order = byte_order
        else:
            raise Exception(f'Unknown byte order value! ({byte_order})')

    # Generic

    def read_byte_array(self, length: int) -> bytearray:
        """
        Returns bytearray() with read bytes.
        Input:
            length - number of bytes to read
        """
        buff = bytearray(length)
        self.readinto(buff)
        return buff

    def read_struct(self, length: int, struct_format: str) -> Iterable:
        """
        Works the same way as struct.unpack(fmt, buffer) function from standard Python library.
        https://docs.python.org/3/library/struct.html#struct.unpack
        """
        buff = self.read_byte_array(length)
        if struct_format[0] in ['@', '=', '<', '>', '!']:
            # format string already has byte order char
            return struct.unpack(struct_format, buff)
        else:
            return struct.unpack(self.byte_order+struct_format, buff)

    def read_type(self, type_str: str) -> Union[int, bool, float, str]:
        val_type = type_str.lower().strip()

        if val_type == 'int8':
            val = self.read_int8()
        elif val_type == 'uint8':
            val = self.read_uint8()
        elif val_type == 'bool8':
            val = self.read_bool8()
        elif val_type == 'int16':
            val = self.read_int16()
        elif val_type == 'uint16':
            val = self.read_uint16()
        elif val_type == 'int32':
            val = self.read_int32()
        elif val_type == 'uint32':
            val = self.read_uint32()
        elif val_type == 'long32':
            val = self.read_long32()
        elif val_type == 'ulong32':
            val = self.read_ulong32()
        elif val_type == 'long64':
            val = self.read_long64()
        elif val_type == 'ulong64':
            val = self.read_ulong64()
        elif val_type == 'float32':
            val = self.read_float32()
        elif val_type == 'double64':
            val = self.read_double64()
        elif val_type == 'nullstring':
            val = self.read_string_null()
        else:
            raise Exception(f'Unsupported value type {val_type}')

        return val

    # Numbers

    def read_bits8(self, num: int = 1) -> list:
        """
        Reads 8 bits as bools
        Returns list of all bits as boolean values.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(1*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'B', buff)

        # convert to bits
        bits = []
        for byte in unpacked:
            bits.extend([bool(int(bit_str)) for bit_str in '{:08b}'.format(byte)])

        return bits

    def read_int8(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 1 byte as Int8
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(1*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'b', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_uint8(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 1 byte as unsigned UInt8
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(1*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'B', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_bool8(self, num: int = 1) -> Union[bool, Iterable]:
        """
        Reads 1 byte as bool8
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(1*num)
        unpacked = [v != 0 for v in struct.unpack(self.byte_order+str(num)+'B', buff)]
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_int16(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 2 bytes as Int16 (SHORT, short)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(2*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'h', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_uint16(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 2 bytes as unsigned Int16 (WORD, unsigned short)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(2*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'H', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_int32(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 4 bytes as Int32 (int)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'i', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_uint32(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 4 bytes as unsigned Int32 (DWORD, int)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'I', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_long32(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 4 bytes as Long32 (long)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'l', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_ulong32(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 4 bytes as unsigned Long32 (unsigned long)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'L', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_long64(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 8 bytes as unsigned Long64 (long long)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(8*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'q', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_ulong64(self, num: int = 1) -> Union[int, Iterable]:
        """
        Reads 8 bytes as unsigned Long64 (unsigned long long)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(8*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'Q', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_float32(self, num: int = 1) -> Union[float, Iterable]:
        """
        Reads 4 bytes as Float32 (float)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'f', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def read_double64(self, num: int = 1) -> Union[float, Iterable]:
        """
        Reads 8 bytes as Double64 (double)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception('Number of values to read must be greater or equal to 1!')
        buff = self.read_byte_array(8*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'d', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    # Strings

    def set_string_encoding(self, encoding: Union[str, None]) -> None:
        """
        Enables to auto-decode read strings to unicode() with readNullString() function.
        Will return binary string if encoding is set to None.
        Input:
            Encoding of strings in binary data OR 'None' to disable automatic decoding.
            (Examples: 'utf-8', 'ascii', 'None', None)
        """
        if not isinstance(encoding, str):
            self.string_encoding = None
        elif encoding.lower() in ['none', '']:
            self.string_encoding = None
        else:
            self.string_encoding = encoding.lower()

    def read_string(self, length: int, strip_null: bool = False, raw: bool = False) -> Union[str, bytes]:
        """
        Reads string of specified length from binary data.

        Input:
            length - number of bytes to read
            [strip_null - True if you want to cut read string before first null char]
            [raw - True if you want to disable auto-decoding for this function call]
        """
        buff = self.read_byte_array(length)
        s = struct.unpack(self.byte_order+str(length)+'s', buff)[0]

        if strip_null:
            s = s.split(b'\x00')[0]
        if (self.string_encoding is not None) and (not raw):
            s = s.decode(self.string_encoding)

        return s

    def read_string_null(self, raw: bool = False) -> Union[str, bytes]:
        """
        Reads a null-terminated string of unspecified length from stream.

        Input:
            [raw - True if you want to disable auto-decoding for this function call]
        """
        output_string = b''
        char = self.read(1)
        while char != b'\x00':
            output_string += char
            char = self.read(1)
            if len(char) == 0:
                break

        if (self.string_encoding is not None) and (not raw):
            output_string = output_string.decode(self.string_encoding)

        return output_string

    def read_text(self, size: int = -1, raw: bool = False) -> Union[str, bytes]:
        data = super().read(size)
        if (self.string_encoding is not None) and (not raw):
            data = data.decode(self.string_encoding)
        return data
