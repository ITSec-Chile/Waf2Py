#!/usr/bin/python3
#################################################################################################################
# Script check if the nginx is running and configure the missing virtual interfaces in the operating system		#	    
# 										Web Application Firewall ITSec											#
#											By Fabian Lagos														#
#################################################################################################################


import subprocess
import os
import sqlite3
import logging

process_uptime = subprocess.Popen(['uptime', '-p'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
uptime = str(process_uptime.communicate()[0])
uptime = uptime.replace('\n','')

logging.basicConfig(filename='/var/log/waf_services.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - ' + uptime + ' - %(message)s', datefmt='%m-%d-%Y %H:%M:%S')

###########################################################################################################
# 								         Check Interfaces												  #
###########################################################################################################

db = sqlite3.connect('/home/www-data/waf2py_community/applications/Waf2Py/databases/waf2py.sqlite')

cmd = "/sbin/ifconfig | grep 'Link encap' |awk '{print $1}'  | sort -u | sed 's/lo//g' |sed '/^$/d'"

#Check interfaces in operative system
process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
names_if_os, err = process.communicate()
if err:
	err = err.replace('\n', '')
	logging.error(err)

names_if_os = names_if_os.split()

#Check interfaces in database
cursor = db.cursor()
cursor.execute('''SELECT iface_ip, iface_name FROM system''')
#NOTE: in the table the data of the netmask is missing

#Compare interfaces
for row in cursor:
	if not row[1] in names_if_os:
		logging.info("It has been detected that interface " + row[1] + " was not created")
		logging.info("Creating interface " + row[1] + " with ip address " + row[0] +  "...")
		process2 = subprocess.Popen(['/sbin/ifconfig', row[1], row[0], 'netmask', '255.255.255.0'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		ok, nok = process2.communicate()
		print(ok)
		print(nok)
		if nok:
			nok = nok.replace('\n','')
			logging.error(nok)
		else:
			logging.info("Interface " + row[1] + " with ip address " + row[0] + " created")



###########################################################################################################
# 								         Check Nginx												  	  #
###########################################################################################################

subprocess.call(['sudo', '/opt/waf/nginx/sbin/nginx'])
 
###########################################################################################################
# 								         Check Routes 												  		  #
###########################################################################################################

cmd = "/sbin/route | tail -n +4"
routes = os.popen(cmd)
routes_os = routes.read()
routes_os = routes_os.splitlines()


cursor2 = db.cursor()
cursor2.execute('''SELECT ip, gw_ip, iface FROM routes;''')

for row_db in cursor2:
	check_out = True
	for line_os in routes_os:
		if row_db[0] == line_os.split()[0] and row_db[1] == line_os.split()[1] and row_db[2] == line_os.split()[7]:
			check_out = False
	if check_out:
		process = subprocess.Popen(['sudo', '/sbin/route', 'add', str(row_db[0]), 'gw', str(row_db[1]), 'dev', str(row_db[2])], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		process,nok = process.communicate()
		
		if nok:
			nok = str(nok).replace('\n','')
			logging.error(err)
		else:
			logging.info("Route added. Destination " + row_db[0] + ", gateway " + row_db[1] + " and dev " + row_db[2] )
		
		

db.close() 

