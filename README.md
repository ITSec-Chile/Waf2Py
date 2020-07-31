
# Waf2Py

Waf2Py is a nice and easy to use web interface for modsecurity v3 with nginx connector. Waf2Py is free and powered by Web2Py that controls modsecurity and nginx configuration in an easy way, allowing you to configure protection for any web application in just minutes.

## Features

- Protect a site in just minutes
- Create global or local exclusions for any rule
- Add virtual interfaces
- Create static routes for the desired app
- Analyze debug, access, error and audit logs
- Download logs
- Check the stats for every application
- Disable/Enable protection with just 1 click
- Enable/Disable rules
- Modify rules
- Restrict paths or files
- Insert headers
- Start/Stop/Reload/Check Syntax of NGINX
- CAPTCHA on login (Google Recaptcha2)
- Two-step Login Authentication (Email code)
- Writed on Python3

##Photos

https://photos.app.goo.gl/kXrsQTPPMuAXi8Tr5


## Compiled version
You can download a compiled version, the bundle contains a compiled version of nginx and modsecurity in a debian 10 system, also contains a copy a of web2py framework with waf2py app loaded, and a script which install some dependences and put everything in his place.
you can find this in the releases section: https://github.com/ITSec-Chile/Waf2Py/releases



## Installation steps


```
git clone https://github.com/ITSec-Chile/Waf2Py
cd Waf2Py/installer/
su root
chmod +x waf2py_installer.sh
#the following script will download and compile the components needed.
./waf2py_installer.sh
```

After the installation you need to run the command "crontab -e" as "root", select an editor and save the file without making any change. 
waf2py need crontajobs but they will are not active until  **crontab: installing new crontab** message is returned.

Example:
```
root@debian:/home/chris# crontab -e
Select an editor.  To change later, run 'select-editor'.
  1. /bin/nano        <---- easiest
  2. /usr/bin/vim.tiny

Choose 1-2 [1]: 1
**crontab: installing new crontab**
```


once is installed go to:
```
https://your_server_ip:62443
Login:
admin:admin (don't forget to change this password!, also you should check the apache conf and look for the /admin and /appadmin path and restrict them to loclahost or trusted IPs)
next step:
go to system --> manage engine --> start engine (this will start nginx, then you can add an application)
```

## Status box explanation
```
Not Running = Nginx not running
Running but 0 apps running = Nginx running but no web app created
Nginx running and apps running = Nginx is running an there is at least 1 web app running
```

## Creating a website
```
1 - Create a virtual IP
      --> Interfaces menu

2 - Create a new app
      --> Click "Deploy" button

3 - Configure the new app
      --> Websites running menu
      --> Click over the application
      --> Configure the backend
      --> Configure ports (leave it blank if you dont need https ports, same thing apply to http ports)
      --> Configure certificates if ssl ports are set
      --> Choose a virtual ip (previusly created on Interfaces menu)
      --> Press the "play" button to enable the new app
      --> Done.
```
## Cronjobs
There is used to restore the virtual interface and bring up nginx when on every reboot
There is a cronjob to update the dashboard stadistics every 5 minutes
There is a cronjob for log rotation every night. Rotated logs are available under "Download logs" tab.




## Built With

* [Web2Py](http://www.web2py.com/) - The web framework used
* [Modsecurity v3](https://www.modsecurity.org/) - WAF Engine
* [Openresty](https://openresty.org/) - Reverse proxy
* [Apache](https://httpd.apache.org/) - Webserver to hold Web2Py
* [AdminLTE](https://adminlte.io/) - Template in the web interface


## About this bundle
```
Tested in Debian 10 (No docker).
Components for this build:
Waf2Py 1.0 App
Web2Py 2.20.2
Nginx version: openresty 1.17.6.2
ModSecurity v3 - libmodsecurity3;
Modsecurity Nginx connector   
OWASP ModSecurity Core Rule Set (CRS) 3.3



```

<b>Note 1</b>: By now not all options of nginx and modsecurity are implemented with nice switches. Advanced configurations can be made throught the "expert configuration" tab.



## Support
We invite you to test and support this development to make something powerfull and free.

## License

Waf2py is Licensed under the LGPL license version 3


