# Chris - cvaras@itsec.cl
# -*- coding: utf-8 -*-
import json
import sqlite3
import os

conn = \
    sqlite3.connect('/home/www-data/waf2py_community/applications/Waf2Py/databases/waf2py.sqlite'
                    )
con = conn.cursor()
a = con.execute('SELECT app_name,id_rand FROM production')
b = a.fetchall()
for app in b:
        d = con.execute('SELECT size FROM log_size WHERE id_rand="{}" AND log_type="modsec"'.format(app[1]))
        old_size = d.fetchall()
        actual_size  = os.path.getsize('/opt/waf/nginx/var/log/{}/{}_audit.log'.format(app[0], app[0]))
        #print('old:{} new:{}'.format(str(old_size[0]), str(actual_size)))
        if old_size[0][0] < actual_size:
            #print('bigger file')
            f = open('/opt/waf/nginx/var/log/{}/{}_audit.log'.format(app[0], app[0]),'r', encoding='utf8', errors='ignore')
            x = f.read()
            f.close()
            notice = 0
            warning = 0
            critical = 0
            error = 0
            total = 0
            transactions = x.splitlines()
            requests = len(transactions)
            for i in transactions:
                total += 1
                row = json.loads(i)
                for ii in row['transaction']['messages']:
                    if ii['details']['severity'] == '0':
                        notice +=1
                    elif ii['details']['severity'] == '1':
                        warning +=1
                    elif ii['details']['severity'] == '2':
                        critical +=1
            con.execute('UPDATE summary SET critical={}, warning={}, notice={}, error={}, total_requests={} WHERE id_rand="{}"'.format(int(critical), int(warning), int(notice), int(error), int(total), app[1]))
            con.execute('UPDATE log_size SET size={} WHERE id_rand="{}" AND log_type="modsec"'.format(int(actual_size), app[1]))
            #print('Critical: {}, Warning: {}, Notice: {}, Error: {} - Total: {}'.format(critical, warning, notice,error, total))
        #else:
        #    print("log hasn't changed") 
conn.commit()
conn.close()
