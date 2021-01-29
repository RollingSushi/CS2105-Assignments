import sys
import zlib

fileinput = str(sys.argv[1])
with open(f"{fileinput}", mode="rb") as f:
    bytes = f.read()
    checksum = zlib.crc32(bytes)
print(checksum)
