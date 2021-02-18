import sys
from socket import *

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

keyValueStore = {}
counterStore = {}


def getHandler(httpPath, key):
    return 'magicGet'


def deleteHandler(httpPath, key):
    return 'magicDelete'


def postHandler(httpPath, key):
    return 'magicPost'


def decodeHeader(httpHeader):
    print(httpHeader)
    substrings = httpHeader.split('/', 2)
    httpMethod = substrings[0].upper()
    httpPath = substrings[1]
    print(httpMethod)
    print(httpPath)

    if (httpMethod == 'GET'):
        key = substrings[2][:-2]
        return getHandler([httpPath, key])
    elif (httpMethod == 'DELETE'):
        key = substrings[2][:-2]
        return deleteHandler([httpPath, key])
    elif (httpMethod == 'POST'):
        keyAndOtherInfo = substrings[2].split(' ')
        print(keyAndOtherInfo)
        key = keyAndOtherInfo[0]
        print(key)
        for i in range(len(keyAndOtherInfo)):
            headerInfoName = keyAndOtherInfo[i].upper()
            if (headerInfoName == 'CONTENT-LENGTH'):
                clength = int(keyAndOtherInfo[i+1])
        # get the data
        data = ' '.encode()
        while(clength != 0):
            data += conn.recv(clength)
            clength -= 1
        print(clength)
        print(data.decode())
        return postHandler(httpPath, key)


while True:
    print('Server is ready to receive')
    conn, addr = serverSocket.accept()

    while True:
        header = ''
        while(len(header) < 3 or header[-2:] != '  '):
            reading = conn.recv(1).decode()
            header += reading
            if(len(reading) == 0):
                break
        if(len(header) == 0):
            conn.close()
            break

        reply = decodeHeader(header)
