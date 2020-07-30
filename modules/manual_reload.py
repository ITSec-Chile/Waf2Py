#!/usr/bin/env python
#@author: chris cvaras@itsec.cl
#this script is used by clean_logs.sh, after delete all audit logs that doesn't containt an attack, nginx will be reloaded 
#otherwise new audit logs and access logs will be not recorded everithing properly, we need to confirm is this affect to access log (pending)
import os
from stuffs import Nginx
a = Nginx()
r = a.Reload()
os.system("echo %s >> /home/www-data/waf2py_community/applications/Waf2Py/scripts/cleaning.log" %(r))
