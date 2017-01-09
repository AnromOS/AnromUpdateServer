#!/usr/bin/env python
#coding=utf-8
# web.py  In Memery of Aaron Swartz
import model
from action.base import base as BaseAction

class Index(BaseAction):
    def GET(self):
        """ Show page """
        #self.session.kill()
        models = model.get_devices()
        prefs = model.get_preferences()
        devices =[]
        for post in models:
            devi={}
            devi['mod_id']= post['mod_id']
            devi['m_device'] = post['m_device']
            devi['m_modname'] = post['m_modname']
            devi['m_modpicture'] = post['m_modpicture']
            devi['m_moddescription'] = post['m_moddescription']
            devi['m_time'] = post['m_time']
            devi['m_detail']=model.get_top5_roms_by_modelid(devi['mod_id'])
            devices.append(devi)
        r_index =self.renderCMS.index(devices,prefs)
        return r_index

class Allroms(BaseAction):
     def GET(self,mdevice):
        """ Show single page """
        #web.ctx.session.kill()
        self.mod_id =-1
        tmd = model.find_modid_bydevice(mdevice)
        for ff in tmd:
            self.mod_id= int(ff['mod_id'])
            self.modname = ff['m_modname']
            self.modpic = ff['m_modpicture']
            self.moddstp = ff['m_moddescription']
            self.mtime = ff['m_time']
        if(self.mod_id ==-1):
            return self.renderDefault.plaintext('该设备不支持。')
        models = model.get_devices()
        devi={}
        devi['mod_id']= self.mod_id
        devi['m_device'] = mdevice
        devi['m_modname'] = self.modname
        devi['m_modpicture'] = self.modpic
        devi['m_moddescription'] = self.moddstp
        devi['m_time'] = self.mtime
        devi['m_detail']=model.get_all_roms_by_modelid(self.mod_id)
        r_index =self.renderCMS.index_allroms(models,devi)
        return r_index

class redirect(BaseAction):
    def GET(self, path):
        self.seeother('/' + path)
