"""
@author: fabian flagos@itsec.cl
"""
import time

#directory to save file
dir_waflog = "/home/www-data/waf2py_community/applications/Waf2Py/logs/waf.log"
dir_waferror = "/home/www-data/waf2py_community/applications/Waf2Py/logs/waf.err"


class Logger:
    def __init__(self):
        pass

    def NewLogApp(db2, username, msg):
        msg = msg
        times = time.strftime("%Y-%m-%d %H:%M")
        file = open(dir_waflog, 'a+')
        file.write("[" + times + "] " + username + ": " + msg + "\n")
        file.close()

        db2.log_app.insert(username=username, time=times, msg=msg)
    
    def NewLogError(db2, username, msg):

        msg = msg
        times = time.strftime("%Y-%m-%d %H:%M")
        file = open(dir_waflog, 'a+')
        file.write("[" + times + "] ERROR " + username + ": " + msg + "\n")
        file.close()


        db2.log_error.insert(username=username, time=times, msg=msg)
