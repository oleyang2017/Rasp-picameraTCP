__author__ = 'macOzone'

import sys
import picamera
import getopt
import datetime
import os
from logger import Logger


# log File
#sys.stdout = Logger('programmerTCPServer.log')
path, thisFilename = os.path.split(os.path.realpath(__file__))
thisFilenameSplitted = thisFilename.split('.')
myLogger = Logger(path + '/' + thisFilenameSplitted[0] + '.log')


def printHelp():
    print('Usage: %s -t caputerTime -f FPS -r rsycDir -h help' % sys.argv[0])
    return

try:
    myopts, args = getopt.getopt(sys.argv[1:], 't:r:f:h')
except getopt.GetoptError as e:
    myLogger.write(str(e))
    printHelp()
    sys.exit(2)


raspiID = ''
try:
    f = open('/etc/hostname', 'r')
    raspiID = f.read()
    raspiID = raspiID.replace('\n', '')
except:
    raspiID = 'generic'


path, filename = os.path.split(os.path.realpath(__file__))
outputFileName = path + '/capture.h264'
FPS = 15
rsyncDir = '192.168.168.143::FolderDestination'
capturingTime = 10

###############################
# o == option
# a == argument passed to the o
###############################
for o, a in myopts:
    if o == '-t':
        #capturing time
        capturingTime = int(a)
        if capturingTime < 0:
            capturingTime = 10
    elif o == '-f':
        #FPS
        FPS = int(a)
        if FPS < 0:
            FPS = 15
    elif o == '-r':
        rsyncDir = a
    elif o == '-h':
        #Print help
        printHelp()
        sys.exit(0)


for filename in os.listdir(path):
    if filename.endswith('.h264'):
        myLogger.write(path + '/' + filename)
        os.remove(path + '/' + filename)

with picamera.PiCamera() as camera:
    camera.framerate = FPS
    camera.resolution = (2592, 1944)
    startTimeStr = datetime.datetime.now()
    camera.start_recording(outputFileName, resize=(1024, 768))
     # Camera warm-up time
    #time.sleep(2)
    camera.wait_recording(capturingTime)
    camera.stop_recording()
    fileName2Send = path + '/' + raspiID + '__' + str(startTimeStr) + '.h264'
    fileName2Send = fileName2Send.replace(' ', '_')
    fileName2Send = fileName2Send.replace(':', '_')
    os.rename(outputFileName, fileName2Send)
    command2Send = 'python ' + path + '/syncro.py -r ' + rsyncDir
    os.system(command2Send)
