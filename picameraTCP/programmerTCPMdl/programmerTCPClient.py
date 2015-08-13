
#!/usr/bin/python

__author__ = 'macOzone'

import sys
import os
import getopt
import socket
import time
from datetime import datetime
from crontab import CronTab
from logger import Logger

SERVER_ADDRESS = '192.168.168.143'
SERVER_PORT = 18200

# log File
#sys.stdout = Logger('programmerTCPServer.log')
path, thisFilename = os.path.split(os.path.realpath(__file__))
thisFilenameSplitted = thisFilename.split('.')
myLogger = Logger(path + '/' + thisFilenameSplitted[0] + '.log')

#Crontab
tab = CronTab(user=True)


def printHelp():
    print('Usage: %s -s serverAddress -h help' % sys.argv[0])
    return


try:
    myopts, args = getopt.getopt(sys.argv[1:], 's:h')
except getopt.GetoptError as e:
    myLogger.write(str(e))
    printHelp()
    sys.exit(2)


# o == option
# a == argument passed to the o
for o, a in myopts:
    if o == '-s':
        #server address
        TCP_IP = a
    elif o == '-h':
        #Print help
        printHelp()
        sys.exit(0)

while True:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((SERVER_ADDRESS, SERVER_PORT))
        myLogger.write('Connected to: '+SERVER_ADDRESS+' AT '+str(SERVER_PORT))

        while True:
            data = s.recv(1024)
            if data:
                #time_to_start_capture---capturing_time_in_seconds---rsyncDir
                myLogger.log("POST: " + data)
                arg = data.split('---')
                if len(arg) == 4:
                    if arg[0] == 'SCM':
                        doit = False
                        while not(doit):
                            #time_to_start_capture---capturing_time_in_seconds---rsyncDir
                            startTime = datetime.strptime(arg[1], '%H:%M:%S')
                            #remove previous job
                            tab.remove_all(comment='CAPTURE_JOB')
                            #new job
                            path, filename = os.path.split(os.path.realpath(__file__))
                            cmd = 'python ' + path
                            cmd += '/capture.py -t ' + arg[2] + ' -r ' + SERVER_ADDRESS + arg[3]
                            cron_job = tab.new(command=cmd, comment='CAPTURE_JOB')
                            cron_job.minute.on(startTime.minute)
                            cron_job.hour.on(startTime.hour)
                            tab.write()
                            cron_job_checker = tab.find_comment('CAPTURE_JOB')
                            if cron_job_checker > 0:
                                doit = True
                                myLogger.write('done')
                    elif arg[0] == 'SYM':
                        cmd = 'python ' + path + '/syncro.py -r ' + SERVER_ADDRESS + arg[3]
                        os.system(cmd)
                        myLogger.log(cmd)
                        myLogger.write('done')
            else:
                # el servidor se ha cerrado y salimos del bucle
                myLogger.log('El servidor se ha cerrado y salimos del bucle')
                break
        s.close()
    except:
        myLogger.write('Error: no server reachable')
        s.close()
        time.sleep(2)

sys.exit(0)
