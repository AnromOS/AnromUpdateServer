#!/usr/bin/env python3
#coding=utf-8
# web.py  In Memery of Aaron Swartz
# 2017.12.10: Switched into Tornado

import model,utils,config
from action.base import base as BaseAction

class CMSBase(BaseAction):
    def get_template_path(self):
        return config.DEFAULT_FRONT_THEME

class Index(CMSBase):
    def get(self):
        """ Show page """
        ##lookup Cache
        cachename="Index"
        result = model.get_Cache(cachename, None)
        if(result):
            self.write(result)
            return
        # Real page
        models = model.get_devices()
        prefs = model.get_preferences()
        for post in models:
            post['m_detail']=model.get_roms_by_devicesname(post['m_device'],5)
        result  = self.render_string("index.html", models=models, prefs=prefs, strtime=utils.strtime,getStatuStr=config.getStatuStr)
        self.write(result)
        ## Put result into cache.
        model.set_Cache(cachename, result)
        return

class Allroms(CMSBase):
     def get(self,mdevice):
        """ Show single page """
        ##lookup Cache
        cachename="Allroms_"+mdevice
        result = model.get_Cache(cachename, None)
        if(result):
            self.write(result)
            return
        # Real page
        tmd = model.get_devices_byname(mdevice)
        models = model.get_devices()
        prefs = model.get_preferences()
        tmd['m_detail']=model.get_roms_by_devicesname(mdevice,-1)
        result  = self.render_string("index_allroms.html",models=models, roms=tmd, prefs=prefs, strtime=utils.strtime,getStatuStr=config.getStatuStr)
        self.write(result)
        ## Put result into cache.
        model.set_Cache(cachename, result)
        return

class ErrorPage(BaseAction):
    def get(self):
        self.write("Windows IIS 5.0: Operation not authorized.")
    
class redirect(BaseAction):
    def get(self, path):
        self.seeother('/' + path)
