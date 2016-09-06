#!/usr/bin/python3
#coding: utf-8

import struct
import io

class BinaryDataStream(io.BytesIO):
    """
    Extends io.BytesIO
    Class for reading specific variable types from binary data stream.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.byte_order = "<" # little-endian, default on X86/x86_64
        self.string_encoding = "ascii"

    def getLength(self):
        """ Returns length of stream """
        last_pos = self.tell()
        self.seek(0x0, io.SEEK_END) # seek EOF
        length = self.tell()
        self.seek(last_pos, io.SEEK_SET)
        return length

    def setByteOrder(self, byte_order):
        """
        Set byte order of binary data in stream.

        Character   Byte order              Size        Alignment
        @           native                  native      native
        =           native                  standard    none
        <           little-endian           standard    none
        >           big-endian              standard    none
        !           network (= big-endian)  standard    none
        """
        if byte_order in ["@", "=", "<", ">", "!"]:
            self.byte_order = byte_order
        else:
            raise Exception("Unknown byte order value! (%s)" % byte_order)

    ## Generic

    def readByteArray(self, length):
        """
        Returns bytearray() with read bytes.
        Input:
            length - number of bytes to read
        """
        buff = bytearray(length)
        self.readinto(buff)
        return buff

    def readStruct(self, length, struct_format):
        """
        Works the same way as struct.unpack(fmt, buffer) function from standard Python library.
        https://docs.python.org/3/library/struct.html#struct.unpack
        """
        buff = self.readByteArray(length)
        if struct_format[0] in ["@", "=", "<", ">", "!"]:
            # format string already has byte order char
            return struct.unpack(struct_format, buff)
        else:
            return struct.unpack(self.byte_order+struct_format, buff)

    def readType(self, type_str):
        val_type = type_str.lower().strip()

        if val_type == "int8":
            val = self.readInt8()
        elif val_type == "uint8":
            val = self.readUInt8()
        elif val_type == "bool8":
            val = self.readBool8()
        elif val_type == "int16":
            val = self.readInt16()
        elif val_type == "uint16":
            val = self.readUInt16()
        elif val_type == "int32":
            val = self.readInt32()
        elif val_type == "uint32":
            val = self.readUInt32()
        elif val_type == "long32":
            val = self.readLong32()
        elif val_type == "ulong32":
            val = self.readULong32()
        elif val_type == "long64":
            val = self.readLong64()
        elif val_type == "ulong64":
            val = self.readULong64()
        elif val_type == "float32":
            val = self.readFloat32()
        elif val_type == "double64":
            val = self.readDouble64()
        elif val_type == "nullstring":
            val = self.readStringNull()
        else:
            raise Exception("Unsupported value type %s" % val_type)

        return val

    ## Numbers

    def readBits8(self, num=1):
        """
        Reads 8 bits as bools
        Returns list of all bits as boolean values.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(1*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'B', buff)

        # convert to bits
        bits = []
        for byte in unpacked:
            bits.extend([ bool(int(bit_str)) for bit_str in "{:08b}".format(byte) ])

        return bits

    def readInt8(self, num=1):
        """
        Reads 1 byte as Int8
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(1*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'b', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readUInt8(self, num=1):
        """
        Reads 1 byte as unsigned UInt8
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(1*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'B', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readBool8(self, num=1):
        """
        Reads 1 byte as bool8
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(1*num)
        unpacked = [ v!=0 for v in struct.unpack(self.byte_order+str(num)+'B', buff) ]
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readInt16(self, num=1):
        """
        Reads 2 bytes as Int16 (SHORT, short)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(2*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'h', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readUInt16(self, num=1):
        """
        Reads 2 bytes as unsigned Int16 (WORD, unsigned short)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(2*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'H', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readInt32(self, num=1):
        """
        Reads 4 bytes as Int32 (int)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'i', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readUInt32(self, num=1):
        """
        Reads 4 bytes as unsigned Int32 (DWORD, int)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'I', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readLong32(self, num=1):
        """
        Reads 4 bytes as Long32 (long)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'l', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readULong32(self, num=1):
        """
        Reads 4 bytes as unsigned Long32 (unsigned long)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'L', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readLong64(self, num=1):
        """
        Reads 8 bytes as unsigned Long64 (long long)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(8*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'q', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readULong64(self, num=1):
        """
        Reads 8 bytes as unsigned Long64 (unsigned long long)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(8*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'Q', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readFloat32(self, num=1):
        """
        Reads 4 bytes as Float32 (float)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(4*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'f', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    def readDouble64(self, num=1):
        """
        Reads 8 bytes as Double64 (double)
        Returns tupple if reading multiple values, else returns just value.
        Input:
            [num - number of values to read. Must be num>=1. (Default==1) ]
        """
        if num < 1:
            raise Exception("Number of values to read must be greater or equal to 1!")
        buff = self.readByteArray(8*num)
        unpacked = struct.unpack(self.byte_order+str(num)+'d', buff)
        if num > 1:
            return unpacked
        else:
            return unpacked[0]

    ## Strings

    def setStringEncoding(self, encoding):
        """
        Enables to auto-decode read strings to unicode() with readNullString() function.
        Will return binary string if encoding is set to None.
        Input:
            Encoding of strings in binary data OR 'None' to disable automatic decoding.
            (Examples: "utf-8", "ascii", "None", None)
        """
        if not isinstance(encoding, str):
            self.string_encoding = None
        elif encoding.lower() in ['none', '']:
            self.string_encoding = None
        else:
            self.string_encoding = encoding.lower()

    def readString(self, length, strip_null=False, raw=False):
        """
        Reads string of specified length from binary data.

        Input:
            length - number of bytes to read
            [strip_null - True if you want to cut read string before first null char]
            [raw - True if you want to disable auto-decoding for this function call]
        """
        buff = self.readByteArray(length)
        s = struct.unpack(self.byte_order+str(length)+'s', buff)[0]

        if strip_null:
            s = s.split(b'\x00')[0]
        if (self.string_encoding is not None) and (not raw):
            s = s.decode(self.string_encoding)

        return s

    def readStringNull(self, raw=False):
        """
        Reads a null-terminated string of unspecified length from stream.

        Input:
            [raw - True if you want to disable auto-decoding for this function call]
        """
        output_string = b""
        char = self.read(1)
        while char != b'\x00':
            output_string += char
            char = self.read(1)
            if len(char) == 0:
                break

        if (self.string_encoding is not None) and (not raw):
            output_string = output_string.decode(self.string_encoding)

        return output_string

    def readText(self, size=-1, raw=False):
        data = super().read(size)
        if (self.string_encoding is not None) and (not raw):
            data = data.decode(self.string_encoding)
        return data
