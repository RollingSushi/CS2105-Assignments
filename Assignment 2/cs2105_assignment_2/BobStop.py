import sys
from socket import *
import zlib

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(('', serverPort))


def main():
    serverSeqNo = 0
    totalPackets = 0
    corruptedPackets = 0
    try:
        while True:
            packet, clientAddress = serverSocket.recvfrom(64)

            try:
                totalPackets += 1
                packet = packet.decode()
                header = packet.split('/', 2)  # splitting packet by /
                clientSeqNo = int(header[0])
                clientCheckSum = header[1]
                data = header[2]

            except:
                # # corrupted packet, give an ACK of 0, a NAK OK
                # seqNoNAck = str(serverSeqNo) + '0'
                # serverCheckSum = str(zlib.crc32(seqNoNAck.encode()))
                # resp = (str(serverSeqNo) + "/" +
                #         serverCheckSum + "/" + '0').encode()
                # #resp = (str(serverSeqNo) + '0').encode()
                # corruptedPackets += 1
                # print("problem with decoding")
                # serverSocket.sendto(resp, clientAddress)
                corruptedPackets += 1

            finally:
                # corruption check
                if (checkCheckSum(clientCheckSum, data, clientSeqNo)):
                    # correct seqNo, send ACK OK
                    if serverSeqNo == clientSeqNo:
                        seqNoNAck = str(serverSeqNo) + '1'
                        serverCheckSum = str(zlib.crc32(seqNoNAck.encode()))
                        resp = (str(serverSeqNo) + "/" +
                                serverCheckSum + "/" + '1').encode()
                        #resp = (str(serverSeqNo) + '1').encode()
                        serverSocket.sendto(resp, clientAddress)
                        serverSeqNo += 1
                        print(data, end='')
                    # wrong seq number, request for older packet OK
                    else:
                        seqNoNAck = str(serverSeqNo - 1) + '1'
                        serverCheckSum = str(zlib.crc32(seqNoNAck.encode()))
                        resp = (str(serverSeqNo - 1) + "/" +
                                serverCheckSum + "/" + '1').encode()
                        #resp = (str(serverSeqNo - 1) + '1').encode()
                        serverSocket.sendto(resp, clientAddress)
                # else:  # failed checksum, send Nak
                #     seqNoNAck = str(serverSeqNo) + '0'
                #     serverCheckSum = str(zlib.crc32(seqNoNAck.encode()))
                #     resp = (str(serverSeqNo) + "/" +
                #             serverCheckSum + "/" + '0').encode()
                #     #resp = (str(serverSeqNo) + '0').encode()
                #     corruptedPackets += 1
                #     serverSocket.sendto(resp, clientAddress)

    finally:
        writer = open('Bob.txt', 'w')
        writer.write(format(corruptedPackets / totalPackets, '.2f'))
        writer.flush()
        writer.close()


def checkCheckSum(clientCheckSum, data, clientSeqNo):
    dataNSeq = data + str(clientSeqNo)
    dataCheckSum = str(zlib.crc32(dataNSeq.encode()))
    return clientCheckSum == dataCheckSum


main()
