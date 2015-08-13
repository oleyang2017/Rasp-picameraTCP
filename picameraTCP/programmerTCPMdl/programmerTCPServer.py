
#!/usr/bin/python

__author__ = 'macOzone'

import os
import sys
import getopt
import socket
import threading
import select
from logger import Logger

from datetime import datetime

SCHEDULE_MODE = 0
SYNCRO_MODE = 1


# log File
#sys.stdout = Logger('programmerTCPServer.log')
path, thisFilename = os.path.split(os.path.realpath(__file__))
thisFilenameSplitted = thisFilename.split('.')
myLogger = Logger(path + '/' + thisFilenameSplitted[0] + '.log')


###############################
###############################


def printHelp():
    print('Usage: %s -c capturingTime(seconds) -t \
        captureSchedule(H:M:S) -h help' % sys.argv[0])
    return


###############################
###############################

class ClientThread(threading.Thread):

    def __init__(self, ip, port, socket, capturingTime, captureSchedule):
        threading.Thread.__init__(self)
        self._ip = ip
        self._port = port
        self._socket = socket
        self._capturingTime = capturingTime
        self._captureSchedule = captureSchedule
        self._strIP_Port = ip + ' : ' + str(port)
        self._mode = SCHEDULE_MODE

        myLogger.log('[+] New thread started for ' + self._strIP_Port)
        self.start()

    def setNewSchedule(self, capturingTime, captureSchedule):
        self._mode = SCHEDULE_MODE
        self._capturingTime = capturingTime
        self._captureSchedule = captureSchedule
        self.run()

    def sycroClients(self):
        self._mode = SYNCRO_MODE
        self.run()

    def run(self):
        data = ""
        if self._mode == SCHEDULE_MODE:
            data = 'SCM---'
        elif self._mode == SYNCRO_MODE:
            data = 'SYM---'

        data += self._captureSchedule.strftime('%H:%M:%S') + '---'
        data += str(self._capturingTime) + '---'
        data += "::FolderDestination"

        try:
            self._socket.send(data)
            myLogger.log('Cliente: ' + self._strIP_Port + ' configured')
        except:
            myLogger.log('Error en el envio de \
                   datos a: '+self._strIP_Port+'socket desconectado')

    def close(self):
        if (self._socket is not(None)):
            myLogger.log('ClientThread: Close Socket')
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
            self.join()

        self._ip = ''
        self._port = 0
        self._socket = None

    def __del__(self):
        self.close()


###############################
###############################

class bindThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self._tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._port = 0
        self._host = '0.0.0.0'
        self._bIsConnected = False
        self._threads = []
        self._exitFlag = 1
        self._captureSchedule = datetime.now()
        self._capturingTime = 10

    def setNewSchedule(self, capturingTime, captureSchedule):
        if capturingTime != 0 and captureSchedule is not None:
            self._captureSchedule = captureSchedule
            self._capturingTime = capturingTime
            for t in self._threads:
                t.setNewSchedule(capturingTime, captureSchedule)

    def sycroClients(self):
        for t in self._threads:
            t.sycroClients()

    def connect(self, host, port):
        if self._bIsConnected is True:
            self.close()

        self._port = port
        self._host = host
        self._exitFlag = 0
        try:
            self._tcpsock.bind((self._host, self._port))
            self._tcpsock.listen(4)
            self._bIsConnected = True
            self.start()
        except:
            pass

    def run(self):
        while self._exitFlag == 0:
            try:
                sread, swrite, sexc = select.select([self._tcpsock], [], [], 1)
                if self._tcpsock in sread:
                    (clientsock, (ip, port)) = self._tcpsock.accept()
                    if (clientsock is not(None)):
                        myLogger.log('*** NEW CLIENT *** --> '+ip+" : "+str(port))
                        newthread = ClientThread(ip, port, clientsock, self._capturingTime, self._captureSchedule)
                        self._threads.append(newthread)
                    else:
                        myLogger.log('Fallo del accept: Socket servidor cerrado')
                        self._exitFlag = 1
            except:
                self._exitFlag = 1

    def close(self):
        if (self._bIsConnected is True):
            self._bIsConnected = False
            myLogger.log('Flag finalizar thread = 1')
            self._exitFlag = 1

            myLogger.log('Cerramos el socket servidor')
            self._tcpsock.close()
            self.join()

            self._port = 0
            self._host = '0.0.0.0'

            for t in self._threads:
                t.close()
            self._threads = []

    def __del__(self):
        self.close()

###############################
###############################

HOST = '0.0.0.0'
PORT = 18200
capturingTime = 0
captureSchedule = datetime.now()  # +timedelta(minutes=10)

try:
    myopts, args = getopt.getopt(sys.argv[1:], 's:t:h')
except getopt.GetoptError as e:
    myLogger.write(str(e))
    printHelp()
    sys.exit(2)

# o == option
# a == argument passed to the o
for o, a in myopts:
    if o == '-h':
        #Print help
        printHelp()
        sys.exit(0)
    elif o == '-s':
        try:
            captureSchedule = datetime.strptime(a, '%H:%M:%S')
        except:
            captureSchedule = datetime.now()
    elif o == '-t':
        try:
            capturingTime = int(a)
        except:
            capturingTime = 0

connectionsManager = bindThread()
connectionsManager.connect(HOST, PORT)
connectionsManager.setNewSchedule(capturingTime, captureSchedule)

try:
    bFinish = False
    while not bFinish:
        ## Show menu ##
        print(30 * '-')
        print('   M A I N - M E N U')
        print(30 * '-')
        print('1. Set New Schedule')
        print('2. Syncro clients')
        print('3. Quit')
        print(30 * '-')
        ## Get input ###
        choice = raw_input('Enter your choice [1-3] : ')
        ### Convert string to int type ##
        choice = int(choice)
        ### Take action as per selected menu-option ###
        if choice == 1:
            myLogger.write('Setting new schedule...')
            connectionsManager.setNewSchedule(capturingTime, captureSchedule)
        elif choice == 2:
            myLogger.write('Syncronizing clients...')
            connectionsManager.sycroClients()
        elif choice == 3:
            myLogger.write('Closing system...')
            connectionsManager.close()
            bFinish = True
        else:
            print('Invalid number. Try again...')
except:
    connectionsManager.close()
