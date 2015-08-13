__author__ = 'macOzone'

import sys
from datetime import datetime
from crontab import CronTab

#Crontab
tab = CronTab(user=True)

startTime = datetime.now()

#new job
cmd = 'python capture.py -t 3'
cron_job = tab.new(command=cmd, comment='CAPTURE_JOB')
cron_job.minute.on(33)
cron_job.hour.on(11)
tab.write()

sys.exit(0)
