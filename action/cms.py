#!/usr/bin/env python
#coding=utf-8
# web.py  In Memery of Aaron Swartz
import model,utils
from action.base import base as BaseAction

class Index(BaseAction):
    def get(self):
        """ Show page """
        #self.session.kill()
        models = model.get_devices()
        prefs = model.get_preferences()
        devices =[]
        for post in models:
            devi={}
            devi['m_device'] = post['m_device']
            devi['m_modname'] = post['m_modname']
            devi['m_modpicture'] = post['m_modpicture']
            devi['m_moddescription'] = post['m_moddescription']
            devi['m_time'] = post['m_time']
            devi['m_detail']=model.get_roms_by_devicesname(devi['m_device'],5)
            devices.append(devi)
        self.render("index.html", devices=devices, prefs=prefs, strtime=utils.strtime)

class Allroms(BaseAction):
     def get(self,mdevice):
        """ Show single page """
        #web.ctx.session.kill()
        tmd = model.get_devices_byname(mdevice)
        models = model.get_devices()
        tmd['m_detail']=model.get_roms_by_devicesname(mdevice,-1)
        self.render("index_allroms.html",models=models, roms=tmd, strtime=utils.strtime)

class ErrorPage(BaseAction):
    def get(self):
        self.write("Windows IIS 5.0: Operation not authorized.")
    
class redirect(BaseAction):
    def get(self, path):
        self.seeother('/' + path)
