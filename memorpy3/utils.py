# Author: Nicolas VERDIER
# This file is part of memorpy.
#
# memorpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# memorpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with memorpy.  If not, see <http://www.gnu.org/licenses/>.

import re
import struct


def re_to_unicode(s):
    new_string = ""
    for c in s:
        new_string += re.escape(c) + "\\x00"

    return new_string


def type_unpack(data_type):
    """ return the struct and the len of a particular type """
    data_type = data_type.lower()

    # data_type: (struct_type, struct_len)
    data_types = {
        'short':  ('h', 2),
        'ushort': ('H', 2),
        'int':    ('i', 4),
        'uint':   ('I', 4),
        'long':   ('l', 4),
        'ulong':  ('L', 4),
        'float':  ('f', 4),
        'double': ('d', 8),
    }

    if data_type in data_types:
        struct_type, struct_len = data_types[data_type]
        return f'<{struct_type}', struct_len

    raise TypeError(f'Unknown data type: {data_type}')


def hex_dump(data, address=0, prefix="", ftype="bytes"):
    """
    function originally from pydbg, modified to display other types
    """
    dump = prefix
    data_slice = ""
    if ftype != "bytes":
        struct_type, struct_len = type_unpack(ftype)
        for i in range(0, len(data), struct_len):
            if address % 16 == 0:
                dump += " "
                for char in data_slice:
                    if 32 <= ord(char) <= 126:
                        dump += char
                    else:
                        dump += "."

                dump += "\n%s%08X: " % (prefix, address)
                data_slice = ""
            tmp_val = "NaN"
            try:
                packed_val = data[i: i + struct_len]
                tmp_val = struct.unpack(struct_type, packed_val)[0]
            except Exception as e:
                print(e)

            if tmp_val == "NaN":
                dump += "{:<15} ".format(tmp_val)
            elif ftype == "float":
                dump += "{:<15.4f} ".format(tmp_val)
            else:
                dump += "{:<15} ".format(tmp_val)
            address += struct_len

    else:
        for byte in data:
            if address % 16 == 0:
                dump += " "
                for char in data_slice:
                    if 32 <= ord(char) <= 126:
                        dump += char
                    else:
                        dump += "."

                dump += "\n%s%08X: " % (prefix, address)
                data_slice = ""
            dump += "%02X " % ord(byte)
            data_slice += byte
            address += 1

    remainder = address % 16
    if remainder != 0:
        dump += "   " * (16 - remainder) + " "
    for char in data_slice:
        if 32 <= ord(char) <= 126:
            dump += char
        else:
            dump += "."

    return dump + "\n"
