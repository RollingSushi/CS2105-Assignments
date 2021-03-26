import time
import sys
import socket
import zlib

port = int(sys.argv[1])
packetSize = 56
timeOut = 0.05
waitTime = 2.5

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSocket.setblocking(False)
clientAddress = ('localhost', port)


def main():

    timerQ = []
    corruptRecvCount = 0
    ackRecvCount = 0
    exitFlag = False
    exitTime = float('inf')

    try:
        messages = "".join(sys.stdin.readlines()).encode()
        pkts = splitMessages(messages)

        for seqNo, packet in pkts.items():
            sendPacket(packet, clientAddress)
            timerQ.append((time.time() + timeOut, seqNo, packet))

        while len(timerQ) > 0 or time.time() < exitTime:
            try:
                newTimerQ = []
                for expireTime, seqNo, packet in timerQ:
                    if seqNo in pkts:
                        if time.time() > expireTime:
                            sendPacket(packet, clientAddress)
                            newTimerQ.append(
                                (time.time() + timeOut, seqNo, packet))
                        else:
                            newTimerQ.append(
                                (time.time(), seqNo, packet))

                timerQ = newTimerQ

                if len(timerQ) == 0 and not exitFlag:
                    exitTime = time.time() + waitTime
                    exitFlag = True

                resp, serverAddress = clientSocket.recvfrom(11)
                if (isValidAck(resp)):
                    respSeqNo = int.from_bytes(resp[:4], byteorder='big')

                    if(respSeqNo in pkts):
                        del pkts[respSeqNo]
                    ackRecvCount += 1
                else:
                    corruptRecvCount += 1

            except socket.error as msg:
                errorType = msg.args[0]
                if errorType == socket.EAGAIN or errorType == socket.EWOULDBLOCK:
                    continue
    finally:
        writer = open('Alice.txt', 'w')
        writer.write(
            f"{format(corruptRecvCount / (ackRecvCount + corruptRecvCount), '.2f')}\n")
        writer.flush()
        writer.close()


def sendPacket(packet, address):
    clientSocket.sendto(packet, address)


def createPacket(seqNo, data):
    seqNoNData = seqNo.to_bytes(4, byteorder='big') + data
    checksum = calculateCheckSum(seqNoNData)
    # packet format is  seqNo, data, checksum
    return seqNoNData + checksum


def calculateCheckSum(data):
    return zlib.crc32(data).to_bytes(4, byteorder='big')


def splitMessages(messages):
    seqNo = 0
    pkts = {}
    for i in range(0, len(messages), packetSize):
        pkts[seqNo] = createPacket(seqNo, messages[i:i+packetSize])
        seqNo += 1
    return pkts


def checkCheckSum(data):
    content = data[:-4]
    return calculateCheckSum(content) == data[-4:]


def isValidAck(resp):
    return checkCheckSum(resp) and resp[4:-4] == b"ACK"


main()
