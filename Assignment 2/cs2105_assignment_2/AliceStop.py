import sys
from socket import *
import zlib

portNo = int(sys.argv[1])
clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.settimeout(0.05)  # 50ms


def main():
    seqNo = 0
    totalACKs = 0
    corruptedACKs = 0
    timeoutAcks = 0
    checkSumOKbutcorreuptedACKs = 0
    wrongpacketnumber = 0
    naks = 0
    goodACKs = 0
    try:
        while True:
            data = sys.stdin.read(50)

            if not data:
                clientSocket.close()
                break
            dataNSeq = data + str(seqNo)
            checksum = str(zlib.crc32(dataNSeq.encode()))
            packet = (str(seqNo) + "/" + checksum + "/" + str(data)).encode()
            # Send packet
            sendPacket(packet)
            print("packet sent")

            # receving ACKs
            while True:
                try:
                    resp, serverAddress = clientSocket.recvfrom(2048)
                    totalACKs += 1
                    resp = resp.decode()
                    ackSplit = resp.split('/', 2)  # splitting packet by /
                    respSeqNo = int(ackSplit[0])
                    serverCheckSum = ackSplit[1]
                    ack = ackSplit[2]

                    # Bob's response is his seq number and ACK
                    #ack = resp[-1]
                    #respSeqNo = int(resp[:-1])
                    if (checkCheckSum(serverCheckSum, ack, respSeqNo)):
                        if ack == '1' and respSeqNo == seqNo:
                            seqNo += 1
                            goodACKs += 1
                            print("ack received success")
                            break
                        elif ack == '1':
                            wrongpacketnumber += 1
                            print("wrong packet number")
                            sendPacket(packet)
                        else:
                            naks += 1
                            print('got a NAK')
                            sendPacket(packet)
                    else:  # corrupted
                        checkSumOKbutcorreuptedACKs += 1
                        sendPacket(packet)
                except timeout:
                    print('timeout')
                    # timeout, send packet again
                    timeoutAcks += 1
                    sendPacket(packet)
                except:
                    print('cant decode')
                    # print("timed out or can't decode")
                    corruptedACKs += 1
                    # timeout, send packet again
                    sendPacket(packet)

    finally:
        writer = open('Alice.txt', 'w')
        print(corruptedACKs)
        print(totalACKs)
        print(timeoutAcks)
        print(checkSumOKbutcorreuptedACKs)
        print(wrongpacketnumber)
        print(naks)
        print(goodACKs)
        writer.write(format(corruptedACKs / totalACKs, '.2f'))
        writer.flush()
        writer.close()


def checkCheckSum(clientCheckSum, data, clientSeqNo):
    dataNSeq = str(clientSeqNo) + data
    dataCheckSum = str(zlib.crc32(dataNSeq.encode()))
    return clientCheckSum == dataCheckSum


def sendPacket(packet):
    clientSocket.sendto(packet, ('', portNo))  # pair of (host,port)


main()
