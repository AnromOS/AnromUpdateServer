#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz

import web
import model,config,utils
import hashlib,json,time,base64,urllib2
import re
import os

class base:
    def __init__(self):
        auther="tweety"
        self.session = web.ctx.session

    ### Templates
    t_globals = {
        'datestr': web.datestr,
        'strdate':utils.strtime,
        'inttime':utils.inttime,
        'urlquote':utils.urllib2.quote,
        'abs2rev':utils.abs2rev,
        'getStatuStr':config.getStatuStr
    }
    renderAdmin = web.template.render('templates/theme_bootstrap', base='base', globals=t_globals)
    renderCMS = web.template.render('templates/theme_bootstrap', base='base_index', globals=t_globals)
    renderDefault = web.template.render('templates/theme_bootstrap')

    def logged(self):
        if web.ctx.session.login==1:
            return True
        else:
            return False

    def countPrivilege(self):
        '''根据预置的秘密计算一个时间相关的随机数，每分钟变一次，用来发布ROM的时候做验证。'''
        secret = config.AUTOPUB_SECRET
        salt = time.strftime("%Y-%m-%d %H:00",time.localtime(time.time()))
        ptoken = hashlib.sha256(secret+salt).hexdigest()
        print("hasPrivilege: ptoken is:",ptoken)
        return ptoken
        
    def hasPrivilege(self,ptoken):
        token = self.countPrivilege()
        print "hasPrivilege: token is:",token ," ptoken is:",ptoken
        return token == ptoken
    
    def seeother(self,path):
        return web.seeother(config.netpref['SCHEME']+"://"+config.netpref['SERVER_HOST']+":"+config.netpref['SERVER_PORT']+path)

    def dump2Json(self, channels):
        '''把所有的数据库中的数据输出到json文件, channels 可以写 release, nightly, all'''
        print("Dumping all products data to one json file....")
        models = model.get_devices()
        devices =[]
        body={}
        products=[]
        dumpfilename = r'static/downloads/latest_'+channels+'.json'
        for post in models:
            devi={}
            mod_id= post['mod_id']
            devi['id'] = post['m_device']
            devi['m_modname'] = post['m_modname']
            devi['m_modpicture'] = post['m_modpicture']
            devi['m_moddescription'] = post['m_moddescription']
            #devi['m_detail']=model.get_top5_roms_by_modelid(mod_id)
            if (channels==r'all'):
                devi['m_detail']=model.get_all_roms_by_modelid(mod_id)
            else: 
                devi['m_detail']=model.get_available_roms_by_modelid(mod_id, channels)
            devices.append(devi)
        for devi in devices:
            devbody =[]
            for x in devi['m_detail']:
                temp={}
                temp['version']=x['version']
                temp['versioncode']=x['versioncode']
                temp["api_level"]= x['api_level']
                temp["filename"] = x['filename']
                temp["url"] = x['url']
                temp['size']=x['size']
                temp['status']=x['status']
                temp["timestamp"] =x['m_time']
                temp["time"] =x['issuetime']
                temp["md5sum"] =x['md5sum']
                temp["changes"] = config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+'/api/changelog/'+devi['id']+'/changelog'+str(x['id'])+'.txt'
                temp["changelog"] = x['changelog']
                temp["channel"] = x['channels']
                devbody.append(temp)
            devi['m_detail']= devbody
            products.append(devi)
        body['id']=None
        body['result']=products
        body['error']=None
        result = json.dumps(body,ensure_ascii=False)
        utils.saveBin(dumpfilename,result.encode('utf-8'))
    
    def dumpAllProduct2Json(self):
        self.dump2Json(r"release")
        self.dump2Json(r"nightly")
        self.dump2Json(r"all")
