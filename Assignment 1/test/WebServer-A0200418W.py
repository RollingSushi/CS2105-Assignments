import sys
from socket import *

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

keyValueStore = {}
counterStore = {}


def decodeHeader(httpHeader):
    print(httpHeader)
    substrings = httpHeader.split('/', 2)
    httpMethod = substrings[0].upper()
    httpPath = substrings[1]

    if (httpMethod == 'GET'):
        key = substrings[2][:-2]
        return getHandler([httpPath, key])
    elif (httpMethod == 'DELETE'):
        key = substrings[2][:-2]
        return deleteHandler([httpPath, key])
    elif (httpMethod == 'POST'):
        keyAndOtherInfo = substrings[2].split(' ')
        key = keyAndOtherInfo[0]
        indexOfCL = keyAndOtherInfo.upper().find('CONTENT-LENGTH')

        if (indexOfCL == -1):
            print("no content length found")
        else:
            print(indexOfCL + 15)
            contentLength = keyAndOtherInfo[indexOfCL + 15]
            content = keyAndOtherInfo[contentLength + 3:]
            print(contentLength)
            print(content)
            return postHandler(httpPath, key, content)


def getHandler(httpPath, key):
    return 'magicGet'


def deleteHandler(httpPath, key):
    return 'magicDelete'


def postHandler(httpPath, key):
    return 'magicPost'


while True:
    conn, addr = serverSocket.accept()
    print('Server is ready to receive')

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