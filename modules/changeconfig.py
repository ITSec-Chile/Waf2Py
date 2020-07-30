# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 13:46:48 2017

@author: chris cvaras@itsec.cl
"""

class Change:
    def __init__(self):
        pass
    
    def Blocks(self, start, end, replaceWith, text):
        import re
        self.start = start
        self.end = end
        self.replaceWith = replaceWith
        self.text = text
        
        #print self.text
        #print type(self.text)
        self.config = re.sub(r'^(##\w+'+self.start+'\w+##\n).*(##\w+'+self.end+'\w+##)', r'\1'+self.replaceWith+'\2', self.text,  flags=re.S | re.M )
        
        return self.config
        
    def Text(self, text, oldstring, newstring):
        self.text = text
        self.oldstring = oldstring
        self.newstring = newstring
        self.text_list = []
        
        self.index = ''
     
        #Add text into a list
        for self.i in self.text.splitlines():
            self.text_list.append(self.i)
            
        for self.line in self.text_list:
            if self.oldstring in self.line:
                
                #get the index object
                self.index = self.text_list.index(self.line)
                try:
                    self.text_list[self.index] = self.newstring
                    self.message = 'success'
                except Exception as e:
                    self.message = e
            else:
                self.message = 'Rule id is not in exclusion list'
                
                
        
        return dict(message=self.message, new_list=self.text_list)
