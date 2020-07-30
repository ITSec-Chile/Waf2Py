#!/usr/bin/env python
# Chris - cvaras@itsec.cl
# -*- coding: utf-8 -*-

import sqlite3
import os

conn = sqlite3.connect('/home/www-data/waf2py_community/applications/Waf2Py/databases/waf2py.sqlite')
con = conn.cursor()

os.system('rm names')
os.system('touch names')
f = open('names', 'ab')
for row in con.execute('SELECT app_name FROM production'):
    f.write(row[0]+'\n')

f.close()
conn.close()
