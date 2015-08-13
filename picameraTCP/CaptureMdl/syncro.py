__author__ = 'macOzone'

import sys
import getopt
import os
from logger import Logger

# log File
#sys.stdout = Logger('programmerTCPServer.log')
path, thisFilename = os.path.split(os.path.realpath(__file__))
thisFilenameSplitted = thisFilename.split('.')
myLogger = Logger(path + '/' + thisFilenameSplitted[0] + '.log')


def printHelp():
    print('Usage: %s -r rsycDir -h help' % sys.argv[0])
    return

try:
    myopts, args = getopt.getopt(sys.argv[1:], 't:r:f:h')
except getopt.GetoptError as e:
    myLogger.write(str(e))
    printHelp()
    sys.exit(2)


path, filename = os.path.split(os.path.realpath(__file__))
rsyncDir = '192.168.168.143::FolderDestination'

# o == option
# a == argument passed to the o
for o, a in myopts:
    if o == '-r':
        rsyncDir = a
    elif o == '-h':
        #Print help
        printHelp()
        sys.exit(0)

for filename in os.listdir(path):
    if filename.endswith('.h264'):
        myLogger.write(path + '/' + filename)
        command2Send = 'rsync -avz ' + path + '/' + filename + " " + rsyncDir
        os.system(command2Send)
