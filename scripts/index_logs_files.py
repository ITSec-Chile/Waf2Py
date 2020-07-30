#!/usr/bin/python
# -*- coding: utf-8 -*-

# Chris - cvaras@itsec.cl

import sqlite3
import os
import subprocess
import random
import string

conn = \
    sqlite3.connect('/home/www-data/waf2py_community/applications/Waf2Py/databases/waf2py.sqlite'
                    )
con = conn.cursor()

a = con.execute('SELECT app_name,id_rand FROM production')
b = a.fetchall()
chars = string.ascii_letters + string.digits
pwdSize = 30

result = ''.join(random.choice(chars) for x in range(pwdSize))
for row in b:
    rand = ''.join(random.choice(chars) for x in range(pwdSize))
    con.execute('DELETE FROM logs_file WHERE id_rand = "%s"' % row[1])
    os.chdir('/opt/waf/nginx/var/log/' + row[0])
    cmd = "ls -lthgG --time-style=full-iso *.gz | awk '{print $3,$4,$7}'"
    out1 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    msg = out1.communicate()[0]
    for i in str(msg, 'utf-8').splitlines():
        logs = i.split(' ')
        #print(logs)
        #print(i)
        if 'access' in logs[2]:
            log_type = 'Access'
        elif 'error' in logs[2]:
            log_type = 'Error'
        elif 'debug' in logs[2]:
            log_type = 'Debug'
        elif 'audit' in logs[2]:
            log_type = 'Audit'

        id_rand2 = log_type + rand
        con.execute('INSERT INTO logs_file (id_rand, log_name, type, size, date, id_rand2) VALUES ("%s","%s","%s", "%s", "%s", "%s")'
                     % (
            row[1],
            logs[2],
            log_type,
            logs[0],
            logs[1],
            id_rand2,
            ))
        con.execute('UPDATE summary SET critical=0, warning=0, notice=0, error=0, total_requests=0 WHERE id_rand="{}"'.format(row[1]))
conn.commit()
conn.close()
