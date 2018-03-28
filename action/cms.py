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

class Latest(CMSBase):
    def get(self):
        """ Show page """
        ##lookup Cache
        cachename="Latest"
        result = model.get_Cache(cachename, None)
        if(result):
            self.write(result)
            return
        # Real page
        models = model.get_devices()
        prefs = model.get_preferences()
        for post in models:
            post['m_detail']=model.get_available_roms_by_modelid(post['m_device'],"release")
            #1. rewrie the url, 2. create the softlink for latest downloadfile.
            for detail in post['m_detail']:
                i_realName = detail.get('filename','')
                i_path = 'static/downloads/'+ post['m_device'] +'/'
                fcut =  detail.get('filename','').split('.')
                if(len(fcut)<=0):continue
                f_apx = fcut[-1]
                detail['filename'] = post['m_device']+'.latest.'+f_apx
                detail['url']= prefs.get('site_domain_ipv4','')+ "/" + i_path + detail['filename']
        result  = self.render_string("index_latest.html", models=models, prefs=prefs, strtime=utils.strtime,getStatuStr=config.getStatuStr)
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
