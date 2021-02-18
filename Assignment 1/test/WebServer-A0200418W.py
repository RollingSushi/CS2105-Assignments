import sys
from socket import *

serverPort = int(sys.argv[1])
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(1)

keyValueStore = {}
counterStore = {}


def getHandler(httpPath, keyValueStore, counterStore, key):
    print('GET got called')
    if (httpPath == 'key'):
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
    elif (httpPath == 'counter'):
        if(key not in keyValueStore):
            return '404 NotFound  '.encode()
        elif(key in counterStore and key in keyValueStore):
            return ('200 OK Content-Length ' + str(len(str(counterStore[key]))) + '  ' + str(counterStore[key])).encode()
        elif(key in keyValueStore):
            return '200 OK Content-Length 8  Infinity'.encode()
    return 'getHandler error'


def deleteHandler(httpPath, keyValueStore, counterStore, key):
    print('DELETE got called')
    if (httpPath == 'key'):
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
    if (httpPath == 'counter'):
        if(key not in counterStore):
            return '404 NotFound  '.encode()
        else:
            countValue = counterStore[key]
            del counterStore[key]
            return ('200 OK Content-Length ' + str(len(str(countValue))) + '  ' + str(countValue)).encode()
    return 'deleteHandler error'


def postHandler(httpPath, keyValueStore, counterStore, key, data):
    print("posthandler got called")
    if(httpPath == 'key'):
        if(key in counterStore and counterStore[key] > 0):
            return '405 MethodNotAllowed  '.encode()
        else:
            keyValueStore[key] = data
            return '200 OK  '.encode()
    if(httpPath == 'counter'):
        if(key not in keyValueStore):
            return '405 MethodNotAllowed  '.encode()
        elif(key in counterStore):
            counterStore[key] += int(data)
            return '200 OK  '.encode()
        elif(key not in counterStore):
            counterStore[key] = int(data)
            return '200 OK  '.encode()
    return 'postHandler error'


def decodeHeader(httpHeader):
    print(httpHeader)
    substrings = httpHeader.split('/', 2)
    httpMethod = substrings[0].upper()
    httpPath = substrings[1]
    print(httpMethod)
    print(httpPath)

    if (httpMethod == 'GET '):
        key = substrings[2][:-2]
        return getHandler([httpPath, key])
    elif (httpMethod == 'DELETE '):
        key = substrings[2][:-2]
        return deleteHandler([httpPath, key])
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
        return postHandler(httpPath, keyValueStore, counterStore, key, data)
    return 'decodeHeader error'


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
        conn.send(reply)
