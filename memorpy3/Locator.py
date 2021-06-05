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

import copy
import struct

from memorpy3.Address import Address


class Locator:
    """
    take a MemoryWorker and a type to search then you can feed the locator
    with values and it will reduce the addresses possibilities
    """

    def __init__(self, mw, data_type="unknown", start=None, end=None):
        self.mw = mw
        self.type = data_type
        self.last_iteration = {}
        self.last_value = None
        self.start = start
        self.end = end

    def find(self, value, erase_last=True):
        return self.feed(value, erase_last)

    def feed(self, value, erase_last=True):
        self.last_value = value
        new_iter = copy.copy(self.last_iteration)
        if self.type == "unknown":
            all_types = [
                "uint",
                "int",
                "long",
                "ulong",
                "float",
                "double",
                "short",
                "ushort",
            ]
        else:
            all_types = [self.type]

        for data_type in all_types:
            if data_type not in new_iter:
                try:
                    new_iter[data_type] = [
                        Address(x, self.mw.process, data_type)
                        for x in self.mw.mem_search(
                            value, data_type, start_offset=self.start, end_offset=self.end
                        )
                    ]
                except struct.error:
                    new_iter[data_type] = []
            else:
                l = []
                for address in new_iter[data_type]:
                    try:
                        found = self.mw.process.read(address, data_type)
                        if int(found) == int(value):
                            l.append(Address(address, self.mw.process, data_type))
                    except Exception as e:
                        pass

                new_iter[data_type] = l

        if erase_last:
            del self.last_iteration
            self.last_iteration = new_iter
        return new_iter

    def get_addresses(self):
        return self.last_iteration

    def diff(self, erase_last=False):
        return self.get_modified_addresses(erase_last)

    def get_modified_addresses(self, erase_last=False):
        last = self.last_iteration
        new = self.feed(self.last_value, erase_last=erase_last)
        ret = {}

        for data_type, l in iter(last.items()):
            typeset = set([int(a) for a in new[data_type]])
            for address in l:
                if int(address) not in typeset:
                    if data_type not in ret:
                        ret[data_type] = []
                    ret[data_type].append(address)

        return ret
