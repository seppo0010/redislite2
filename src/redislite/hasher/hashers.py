from . import crc32

HASHERS = {}

for h in (crc32.Hasher('c'), ):
    HASHERS[h.identifier] = h
