#!/bin/path
import os
import sys
from time import gmtime
from time import strftime
from time import time
import datetime
import re

ctime = datetime.datetime.now()
# Test for list function
file = open("cmd/create.txt")
#file = open("cmd/list.txt")
try:
    all_lines = file.readlines()
    old_run = ''
    for line in all_lines:
         if len(line)<10:
             continue
         run_name = "pylarion-cmd-unittest-%s" % int(time())

         if 'RUNNAME' in line:
	     line = line.replace('RUNNAME', run_name)
	     old_run = run_name
	 if 'SAMERUN' in line:
	     line = line.replace('SAMERUN', old_run)
         print("[%s] %s" % (ctime, line))
         ret = os.system("%s" %line)
         if ret != 0:
             print("++++++++++++ Result FAIL +++++++++++++++++\n")
         else:
             print("++++++++++++ Result PASS +++++++++++++++++\n")
finally:
    file.close()

