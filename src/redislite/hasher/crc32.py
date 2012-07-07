from zlib import crc32
from struct import pack

from . import BaseHasher


class Hasher(BaseHasher):
    hashed_length = 4

    def hash(self, string):
        return pack('!i', crc32(string))
