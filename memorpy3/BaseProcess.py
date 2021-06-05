#!/usr/bin/env python
# -*- coding: UTF8 -*-

import struct
from typing import Union

from .Address import Address
from .utils import type_unpack

""" Base class for process not linked to any platform """


class ProcessException(Exception):
    pass


class BaseProcess:
    def __init__(self, *args, **kwargs):
        """ Create and Open a process object from its pid or from its name """
        self.h_process = None
        self.pid = None
        self.isProcessOpen = False
        self.buffer = None
        self.buffer_len = 0

    def __del__(self):
        self.close()

    def close(self):
        pass

    def iter_region(self, *args, **kwargs):
        raise NotImplementedError

    def write_bytes(self, address, data):
        raise NotImplementedError

    def read_bytes(self, address, length=4):
        raise NotImplementedError

    def get_symbolic_name(self, address):
        return "0x%08X" % int(address)

    def read(self,
             address: Union[Address, int],
             data_type: str = 'uint',
             max_len: int = 50,
             errors: str = 'raise',
             encoding: str = 'utf-8',
             decode_errors: str = 'ignore'  # strict / ignore / replace
             ):

        if data_type == 's' or data_type == 'string':
            data = self.read_bytes(int(address), length=max_len)

            new_data = []

            for char in data:
                if char == ord('\x00'):
                    return bytes(new_data).decode(encoding, decode_errors)

                new_data.append(char)

            if errors == 'ignore':
                return new_data

            raise ProcessException('string > max_len')

        else:
            if data_type == 'bytes' or data_type == 'b':
                return self.read_bytes(int(address), length=max_len)

            struct_type, struct_len = type_unpack(data_type)
            return struct.unpack(struct_type, self.read_bytes(int(address), length=struct_len))[0]

    def write(self, address, data, data_type="uint"):
        if data_type != "bytes":
            struct_type, struct_len = type_unpack(data_type)
            return self.write_bytes(int(address), struct.pack(struct_type, data))
        else:
            return self.write_bytes(int(address), data)
