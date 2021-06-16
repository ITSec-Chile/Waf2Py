#!/bin/bash
#add /sbin to path
PATH=$PATH:/sbin
export PATH
current_dir=$(pwd)
#Install some deps
apt-get update
apt-get -y install apt-utils openssl autoconf net-tools python3-pip libapache2-mod-wsgi-py3 automake libtool m4 build-essential git sudo apache2 libcurl4-openssl-dev libpcre3 libpcre3-dev unzip geoip-bin libgeoip-dev liblmdb-dev tar libpcre++-dev libtool m4 libxml2-dev libyajl-dev pkgconf zlib1g-dev
pip3 install psutil netifaces geoip
#Create the ssl folder and delete default sites of apache
rm /etc/apache2/sites-enabled/*.conf
mkdir /etc/apache2/ssl

#Configure the 62443 port in apache & Enable some apache modules
echo -e  "\e[32mConfigure the 62443 port in apache & Enable some apache modules\e[39m"
cd /etc/apache2/
mv /etc/apache2/ports.conf /etc/apache2/ports.conf.bkp
echo '
<IfModule ssl_module>
  #Listen 443
  Listen 62443
</IfModule>
<IfModule mod_gnutls.c>
  Listen 443
</IfModule>
' > /etc/apache2/ports.conf
sudo a2enmod ssl
sudo a2enmod headers
sudo a2enmod expires
sudo a2enmod wsgi


#Creating the apache config
echo -e "\e[32mCreating the apache config\e[39m"
echo '
<VirtualHost *:62443>
  #SSL certs
  SSLEngine on
  SSLCertificateFile /etc/apache2/ssl/self_signed.cert
  SSLCertificateKeyFile /etc/apache2/ssl/self_signed.key
  WSGIDaemonProcess Waf2Py user=www-data group=www-data
  WSGIProcessGroup Waf2Py
  WSGIScriptAlias / /home/www-data/waf2py_community/wsgihandler.py
  WSGIPassAuthorization On
<Location /admin>
  Require all granted
  #Comment line above and uncomment lines below to restrict access to the admin interfaces of web2py (Totally recommended):
  #Require ip X.X.X.X
  #Require all denied
  </Location>
  <LocationMatch ^/([^/]+)/appadmin>
    Require all granted
    #Comment line above and uncomment lines below to restrict access to the admin interfaces of web2py (Totally recommended):
    #Require ip X.X.X.X
    #Require all denied
  </LocationMatch>
  <Directory /home/www-data/waf2py_community>
    AllowOverride None
    Require all granted
    #Comment line above and uncomment lines below to restrict access to the waf2py app:
    #Require ip X.X.X.X
    #Require all denied
    <Files wsgihandler.py>
       Require all granted
       #Comment line above and uncomment lines below to restrict access to the waf2py app:
       #Require ip X.X.X.X
       #Require all denied
    </Files>
  </Directory>
  AliasMatch ^/([^/]+)/static/(?:_[\d]+.[\d]+.[\d]+/)?(.*) \
        /home/www-data/waf2py_community/applications/$1/static/$2
  <Directory /home/www-data/waf2py_community/applications/*/static/>
    Options -Indexes
    ExpiresActive On
    ExpiresDefault "access plus 1 hour"
    Require all granted
    #Comment line above and uncomment lines below to restrict access to the static content:
    #Require ip X.X.X.X
    #Require all denied
  </Directory>
  #Access and error logs files
  CustomLog /var/log/apache2/waf2py_access.log common
  ErrorLog /var/log/apache2/waf2py_error.log
</VirtualHost> ' > /etc/apache2/sites-available/waf2py.conf

#Enable Waf2Py on apache
echo -e "\e[32mEnable Waf2Py on apache\e[39m"
cd /etc/apache2/sites-enabled
ln -s ../sites-available/waf2py.conf .

#Create the ssl certificate.
echo -e "\e[32mCreating the ssl certificate.\e[39m"
cd /etc/apache2/ssl
openssl genrsa 4096 > /etc/apache2/ssl/self_signed.key
chmod 400 /etc/apache2/ssl/self_signed.key
openssl req -new -x509 -nodes -sha1 -days 365 -key /etc/apache2/ssl/self_signed.key > /etc/apache2/ssl/self_signed.cert
openssl x509 -noout -fingerprint -text < /etc/apache2/ssl/self_signed.cert > /etc/apache2/ssl/self_signed.info

mkdir /home/www-data

cd /home/www-data
if [ -f web2py_src.zip ]; then rm web2py_src.zip; fi
wget http://web2py.com/examples/static/web2py_src.zip
unzip web2py_src.zip
mv web2py waf2py_community
mv /home/www-data/waf2py_community/handlers/wsgihandler.py /home/www-data/waf2py_community/wsgihandler.py
cd $current_dir
echo "
routers = dict( 
    BASE = dict( 
        default_application='Waf2Py', 
    ) 
)" > /home/www-data/waf2py_community/routes.py
#Remove default apps in web2py
rm -r /home/www-data/waf2py_community/applications/examples
rm -r /home/www-data/waf2py_community/applications/welcome


#Set up the admin password for Web2Py administration
echo -e "\e[32mSet up the admin password for Web2Py administration\e[39m"
echo -e "\e[33m[!]Change the admin password for the admin interface of web2py\e[39m"
cd /home/www-data/waf2py_community
python3 -c "from gluon.widget import console; console(3);"
python3 -c "from gluon.main import save_password; save_password(input('Choose an admin password for web2py admin: '),62443)"
cd ../

#Add user www-data to sudo
echo -e "\e[32mAdd user www-data to sudo\e[39m"
/sbin/adduser www-data sudo
echo '
www-data ALL=(ALL) NOPASSWD: /opt/waf/nginx/sbin/nginx
www-data ALL=(ALL) NOPASSWD: /bin/netstat
www-data ALL=(ALL) NOPASSWD: /bin/chmod
www-data ALL=(ALL) NOPASSWD: /bin/chown
www-data ALL=(ALL) NOPASSWD: /sbin/ifconfig
www-data ALL=(ALL) NOPASSWD: /sbin/route
www-data ALL=(ALL) NOPASSWD: /usr/bin/lsof
' >> /etc/sudoers.d/Waf2Py
cd $current_dir

#Create crontabs
echo '
@reboot /usr/bin/python3 /home/www-data/waf2py_community/applications/Waf2Py/scripts/check_services.py
@reboot nohup /home/www-data/waf2py_community/applications/Waf2Py/scripts/nginx_start_check.sh &
2 0 * * * /usr/bin/python3 /home/www-data/waf2py_community/applications/Waf2Py/scripts/index_logs_files.py
0 */2 * * * /bin/bash /home/www-data/waf2py_community/applications/Waf2Py/scripts/remove_tmp.sh
1 0 * * * /bin/bash /home/www-data/waf2py_community/applications/Waf2Py/scripts/logrotate
*/5 * * * * /usr/bin/python3 /home/www-data/waf2py_community/applications/Waf2Py/scripts/summary.py
' >> /var/spool/cron/crontabs/root



#Download and Compile the ModSecurity 3.0 Source Code
echo -e "\e[32mDownload and Compile the ModSecurity 3.0 Source Code\e[39m"
mkdir -p /usr/src/waf
cd /usr/src/waf

git clone --depth 1 -b v3/master --single-branch https://github.com/SpiderLabs/ModSecurity
cd ModSecurity
git submodule init
git submodule update
./build.sh
./configure
make
make install
#The compilation takes about 15 minutes, depending on the processing power of your system.
#Note: It’s safe to ignore messages like the following during the build process. Even when they appear, the compilation completes and creates a working object.
#fatal: No names found, cannot describe anything.

#Download Nginx Connector
cd ..
echo -e "\e[32mDownload Nginx Connector\e[39m"
git clone --depth 1 https://github.com/SpiderLabs/ModSecurity-nginx.git

#Download openssl
echo -e "\e[32mDownload openssl\e[39m"
wget https://www.openssl.org/source/openssl-1.1.1k.tar.gz
tar xvzf openssl-1.1.1k.tar.gz


#OPTIONAL - Get PageSpeed module for nginx
#wget https://github.com/apache/incubator-pagespeed-ngx/archive/v${NPS_VERSION}.zip
#NPS_VERSION=1.13.35.1-beta
#unzip v${NPS_VERSION}.zip
#nps_dir=$(find . -name "*pagespeed-ngx-${NPS_VERSION}" -type d)
#cd "$nps_dir"
#NPS_RELEASE_NUMBER=${NPS_VERSION/beta/}
#NPS_RELEASE_NUMBER=${NPS_VERSION/stable/}
#psol_url=https://dl.google.com/dl/page-speed/psol/${NPS_RELEASE_NUMBER}.tar.gz
#[ -e scripts/format_binary_url.sh ] && psol_url=$(scripts/format_binary_url.sh PSOL_BINARY_URL)
#wget ${psol_url}
#tar -xzvf $(basename ${psol_url})  # extracts to psol/

#Install OpenResty
#https://openresty.org/en/changelog-1017008.html
echo -e "\e[32mInstall OpenResty\e[39m"
#wget https://openresty.org/download/openresty-1.13.6.2.tar.gz
wget https://openresty.org/download/openresty-1.17.8.2.tar.gz
tar xvzf openresty-1.17.8.2.tar.gz
cd openresty-1.17.8.2
./configure --user=www-data --group=www-data \
--with-http_ssl_module \
--with-http_geoip_module \
--with-http_v2_module \
--with-http_realip_module \
--with-openssl=/usr/src/waf/openssl-1.1.1k \
--prefix=/opt/waf \
--sbin-path=/opt/waf/nginx/sbin/nginx \
--conf-path=/opt/waf/nginx/etc/nginx.conf \
--http-log-path=/opt/waf/nginx/var/log/access \
--error-log-path=/opt/waf/nginx/var/log/error \
--pid-path=/opt/waf/nginx/var/run/nginx.pid \
--lock-path=/opt/waf/nginx/var/run/nginx.lock \
--with-compat --add-dynamic-module=../ModSecurity-nginx
# OPTIONAL - if you downloaded PageSpeed, add the following compile option:
#--add-module=/usr/src/waf/incubator-pagespeed-ngx-1.13.35.1-beta
make
make install

#create folders and set permissions
mkdir -p /opt/waf/nginx/etc/{sites-available,geoip,sites-available,sites-enabled,backend,modsec_rules,modsecurity_conf,ssl,listen,rewrite/paths,rewrite/headers,crs,static/html}
mkdir -p /opt/waf/nginx/cache/{static,temp}

#download rules
cd /usr/src/waf
git clone https://github.com/coreruleset/coreruleset owasp-modsecurity-crs
cd owasp-modsecurity-crs
mv crs-setup.conf.example  crs-setup.conf
cd ..
cp -r owasp-modsecurity-crs /opt/waf/nginx/etc/crs/
cd /opt/waf/nginx/etc/crs/owasp-modsecurity-crs
sed -i 's/SecDefaultAction/#SetDefaultAction/g' crs-setup.conf
cd /usr/src/waf

echo '
### SET GEOIP Variables ###
fastcgi_param GEOIP_COUNTRY_CODE $geoip_country_code;
fastcgi_param GEOIP_COUNTRY_CODE3 $geoip_country_code3;
fastcgi_param GEOIP_COUNTRY_NAME $geoip_country_name;
fastcgi_param GEOIP_CITY_COUNTRY_CODE $geoip_city_country_code;
fastcgi_param GEOIP_CITY_COUNTRY_CODE3 $geoip_city_country_code3;
fastcgi_param GEOIP_CITY_COUNTRY_NAME $geoip_city_country_name;
fastcgi_param GEOIP_REGION $geoip_region;
fastcgi_param GEOIP_CITY $geoip_city;
fastcgi_param GEOIP_POSTAL_CODE $geoip_postal_code;
fastcgi_param GEOIP_CITY_CONTINENT_CODE $geoip_city_continent_code;
fastcgi_param GEOIP_LATITUDE $geoip_latitude;
fastcgi_param GEOIP_LONGITUDE $geoip_longitude;' > /opt/waf/nginx/etc/geoip/fastcgi.conf
cd $current_dir 
cp nginx.conf /opt/waf/nginx/etc/
cp 403.html /opt/waf/nginx/etc/static/html/
cp 404.html /opt/waf/nginx/etc/static/html/
# adjust permissions
chown www-data /opt/waf/nginx/var/log/
chown www-data /opt/waf/nginx/etc/{sites-available,sites-enabled,modsecurity_conf,modsec_rules,backend,listen,ssl}
chown www-data -R /opt/waf/nginx/etc/{rewrite,crs}

cd ../../
mv Waf2Py /home/www-data/waf2py_community/applications/
#Create logrotation folder andscript
echo '#!/bin/sh
test -x /usr/sbin/logrotate || exit 0
ls /home/www-data/waf2py_community/applications/Waf2Py/logrotation.d | while read i; do /usr/sbin/logrotate -v /home/www-data/waf2py_community/applications/Waf2Py/logrotation.d/$i;done
' > /home/www-data/waf2py_community/applications/Waf2Py/scripts/logrotate

# put files in place
cp /usr/src/waf/ModSecurity/unicode.mapping /opt/waf/nginx/etc/
cp /home/www-data/waf2py_community/applications/Waf2Py/geoip/GeoIP.dat /opt/waf/nginx/etc/geoip/
cp /home/www-data/waf2py_community/applications/Waf2Py/geoip/GeoLiteCity.dat /opt/waf/nginx/etc/geoip/
chown -R www-data:www-data /home/www-data
chown -R www-data:www-data /home/www-data/*
echo -e "\e[32mRebooting system\e[39m"
/sbin/reboot

