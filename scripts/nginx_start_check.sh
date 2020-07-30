#!/bin/bash
#This script start nginx when user send start signal from web interface
while true
do
nginx_pid=$(cat /opt/waf/nginx/var/run/nginx.pid)
action=$(cat /home/www-data/waf2py_community/applications/Waf2Py/scripts/.nginx.action)
if [ -z "$nginx_pid" ] && [ "$action" == "start" ]
then 
echo "Starting Nginx"
sudo /opt/waf/nginx/sbin/nginx
echo "wait" > /home/www-data/waf2py_community/applications/Waf2Py/scripts/.nginx.action
fi
sleep 5
done
