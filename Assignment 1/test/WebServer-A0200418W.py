import sys
from socket import *
import time

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

keyValueStore = {}
counterStore = {}


def decodeHeader(httpHeader, conn):
    print(httpHeader)
    substrings = httpHeader.split('/', 2)
    httpMethod = substrings[0].upper()
    httpPath = substrings[1]
    print(httpMethod)
    print(httpPath)

    if (httpMethod == 'GET ' or httpMethod == 'DELETE'):
        key = substrings[2][:-2]
        return [httpMethod, httpPath, key, 'NULL']
    elif (httpMethod == 'POST '):
        keyAndOtherInfo = substrings[2].split(' ')
        key = keyAndOtherInfo[0]
        for i in range(len(keyAndOtherInfo)):
            headerInfoName = keyAndOtherInfo[i].upper()
            if (headerInfoName == 'CONTENT-LENGTH'):
                clength = int(keyAndOtherInfo[i+1])
        # get the data
        data = ''.encode()
        while(clength != 0):
            data += conn.recv(clength)
            clength -= 1
        return [httpMethod, httpPath, key, data]


def keyHandler(decodedHeader, keyValueStore, counterStore):
    httpMethod = decodedHeader[0]
    key = decodedHeader[2]
    data = decodedHeader[3]

    if(httpMethod == 'POST '):
        if(key in counterStore and counterStore[key] > 0):
            return '405 MethodNotAllowed  '.encode()
        else:
            keyValueStore[key] = data
            return '200 OK  '.encode()
    elif(httpMethod == 'GET '):
        if(key not in keyValueStore):
            return '404 NotFound  '.encode()
        elif(key in keyValueStore and key in counterStore):
            counterStore[key] -= 1
            keyValue = keyValueStore[key]
            if(counterStore[key] == 0):
                del keyValueStore[key]
                del counterStore[key]
            return ('200 OK Content-Length ' + str(len(keyValue)) + '  ').encode() + keyValue
        elif(key in keyValueStore):
            return ('200 OK Content-Length ' + str(len(keyValueStore[key])) + '  ').encode() + keyValueStore[key]
    elif(httpMethod == 'DELETE '):
        if(key not in keyValueStore):
            return '404 NotFound  '.encode()
        elif(key in keyValueStore and key in counterStore):
            if(counterStore[key] > 0):
                return '405 MethodNotAllowed  '.encode()
            else:
                del keyValueStore[key]
                del counterStore[key]
                return '200 OK  '.encode()
        elif(key in keyValueStore):
            keyValue = keyValueStore[key]
            del keyValueStore[key]
            return ('200 OK Content-Length ' + str(len(keyValue)) + '  ').encode() + keyValue

    return 'keyHandler error'


def counterHandler(decodedHeader, keyValueStore, counterStore):
    httpMethod = decodedHeader[0]
    key = decodedHeader[2]
    data = decodedHeader[3]

    if(httpMethod == 'POST '):
        if(key not in keyValueStore):
            return '405 MethodNotAllowed  '.encode()
        elif(key in counterStore):
            counterStore[key] += int(data)
            return '200 OK  '.encode()
        elif(key not in counterStore):
            counterStore[key] = int(data)
            return '200 OK  '.encode()
    elif(httpMethod == 'GET '):
        if(key not in keyValueStore):
            return '404 NotFound  '.encode()
        elif(key in counterStore and key in keyValueStore):
            return ('200 OK Content-Length ' + str(len(str(counterStore[key]))) + '  ' + str(counterStore[key])).encode()
        elif(key in keyValueStore):
            return '200 OK Content-Length 8  Infinity'.encode()
    elif(httpMethod == 'DELETE '):
        if(key not in counterStore):
            return '404 NotFound  '.encode()
        else:
            countValue = counterStore[key]
            del counterStore[key]
            return ('200 OK Content-Length ' + str(len(str(countValue))) + '  ' + str(countValue)).encode()

    return 'counterHandler error'


def pathSplitter(decodedHeader):
    httpPath = decodedHeader[1]

    if(httpPath == 'key'):
        reply = keyHandler(decodedHeader, keyValueStore, counterStore)
    elif(httpPath == 'counter'):
        reply = counterHandler(decodedHeader, keyValueStore, counterStore)

    return reply


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

        start = time.time()
        decodedHeader = decodeHeader(header, conn)
        reply = pathSplitter(decodedHeader)
        end = time.time()
        print(end - start)
        conn.send(reply)
