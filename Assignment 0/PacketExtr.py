import sys


def readHeader():
    headerInfo = []
    while True:
        data = sys.stdin.buffer.read1(1)
        # The end of the head
        if data == b'B':
            return b''.join(headerInfo)
        elif data == b'':
            return None
        else:
            headerInfo.append(data)


while True:
    headerInfo = readHeader()
    if headerInfo == None:
        break
    # Split bytes into segments
    packetTypeB = headerInfo.split(b',')[0]
    packetSizeB = headerInfo.split(b',')[1][1:]

    # Get values from segment
    packetType = packetTypeB[6:]
    packetSize = int(packetSizeB[6:])

    if packetType == b"CS2105":
        index = 0
        while index < packetSize:
            data = sys.stdin.buffer.read1(packetSize - index)
            index += len(data)
            sys.stdout.buffer.write(data)
            sys.stdout.buffer.flush()
    else:
        index = 0
        while index < packetSize:
            data = sys.stdin.buffer.read1(packetSize - index)
            index += len(data)
