import sys
import zlib
from socket import *

port = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverAddress = ('localhost', port)
serverSocket.bind(serverAddress)


def main():
    pkts = {}
    expectedSeqNo = 0
    pktRecvCount = 0
    corruptedRecvCount = 0
    try:
        while True:
            try:
                data, clientAddress = serverSocket.recvfrom(64)

                pktRecvCount += 1
                if (checkCheckSum(data)):
                    seqNo = int.from_bytes(data[:4], byteorder='big')
                    resp = createAck(seqNo)
                    sendAck(resp, clientAddress)
                    if not (seqNo in pkts):
                        content = data[4:-4].decode()
                        pkts[seqNo] = content

                        while expectedSeqNo in pkts:
                            print(pkts[expectedSeqNo], end="")
                            expectedSeqNo += 1
                else:
                    corruptedRecvCount += 1
            except KeyboardInterrupt as stop:
                raise stop
    finally:
        writer = open('Bob.txt', 'w')
        writer.write(
            f"{format(corruptedRecvCount / pktRecvCount, '.2f')}\n")
        writer.flush()
        writer.close()


def sendAck(ack, clientAddress):
    serverSocket.sendto(ack, clientAddress)


def createAck(seqNo):
    seqNoNAck = seqNo.to_bytes(4, byteorder='big') + b'ACK'
    checksum = calculateCheckSum(seqNoNAck)
    # packet format is  seqNo, data, checksum
    return seqNoNAck + checksum


def calculateCheckSum(data):
    return zlib.crc32(data).to_bytes(4, byteorder='big')


def checkCheckSum(data):
    content = data[:-4]
    return calculateCheckSum(content) == data[-4:]


main()
