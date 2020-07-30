#!/usr/bin/env python
#@author: chris cvaras@itsec.cl
# -*- coding: utf-8 -*-
#

import subprocess
import stuffs
import netifaces


class Network:
    def __init__(self):
        pass

    def IpsUsed(self):

        #Get all Ips used from all interfaces
        #for debian 8
        cmd = "ip addr | grep inet | sed 's/inet/- inet/g'"
        self.process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.sum, self.sum_err = self.process.communicate()
        return self.sum.splitlines()

    def Interfaces(self, iface):
        #list all interfaces
        self.iface = iface
        self.process = subprocess.Popen(['ip', 'addr', 'show', 'dev', '%s' %(self.iface)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        interfaces,error = process.communicate()
        
        return interfaces
    
    def AddIface(self,iface_ip, netmask, iface_name, db):
        self.iface_name = iface_name
        self.netmask = netmask
        self.iface_ip = iface_ip
        #get main ip
        #cmd = "/sbin/ifconfig | head -n2 |grep 'inet ' | awk '{print $2}' | cut -d ':' -f2"
        cmd = "ip addr show | grep 'scope global' | grep -v ':' | awk '{print $2}' | sed 's/\/.*//g'"
        self.process3 = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.out3, self.err3 = self.process3.communicate()
        self.ips = self.out3.splitlines()
        
        
        if self.iface_ip in self.ips or self.iface_ip == '127.0.0.1':
            message = 'This ip is reserved for Me!'
            self.name = None
            
        else:
            n_iface = db(db.n_interfaces.id==1).select().first()
            n_iface = int(n_iface.number)+1
            db(db.n_interfaces.id==1).update(number=n_iface)
            self.name = str(self.iface_name) + ':' + str(n_iface)

            #Add interface
            self.process2 = subprocess.Popen(['sudo', '/sbin/ifconfig', str(self.name), str(self.iface_ip), 'netmask', str(self.netmask)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.out, self.err = self.process2.communicate()
            message = 'Interface Added'

        return dict(message=message, device=self.name)

    def iface_names(self):
        self.ifaces = netifaces.interfaces()
        #remove virtuals and loopback interfaces from the list
        self.new_iface_list = []
        for i in self.ifaces:
            if i == "lo" or ":" in i:
                pass
            else:
                self.new_iface_list.append(i)
                
        return self.new_iface_list
