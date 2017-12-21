#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz
# 2017.12.10: Switched into Tornado

import tornado.web
import model,config,utils
import hashlib,json,time,base64,urllib2
import re
import os

class base(tornado.web.RequestHandler):

    ### Templates
    t_globals = {
        'strdate':utils.strtime,
        'inttime':utils.inttime,
        'urlquote':utils.urllib2.quote,
        'abs2rev':utils.abs2rev,
        'getStatuStr':config.getStatuStr
    }

    def get_current_user(self):
        user_id =  self.get_secure_cookie("uname")
        if not user_id:
            return None
        return user_id
    
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
    
    def isAdmin(self):
        '''判断当前用户是否有管理员权限'''
        uinfo = model.get_user_by_uname(self.current_user)
        return (uinfo['u_role'] == "admin")
    
    def seeother(self,path):
        self.redirect(config.netpref['SCHEME']+"://"+config.netpref['SERVER_HOST']+":"+config.netpref['SERVER_PORT']+path)

    def dump2Json(self, channels):
        '''把所有的数据库中的数据输出到json文件, channels 可以写 release, nightly, all'''
        print("Dumping products data to latest_%s.json...."%channels)
        models = model.get_devices()
        devices =[]
        body={}
        products=[]
        dumpfilename = r'static/downloads/latest_'+channels+'.json'
        for post in models:
            devi={}
            devi['id'] = post['m_device']
            devi['m_modname'] = post['m_modname']
            devi['m_modpicture'] = post['m_modpicture']
            devi['m_moddescription'] = post['m_moddescription']
            #devi['m_detail']=model.get_top5_roms_by_modelid(post['m_device'],5)
            if (channels==r'all'):
                devi['m_detail']=model.get_roms_by_devicesname(post['m_device'],-1)
            else: 
                devi['m_detail']=model.get_available_roms_by_modelid(post['m_device'], channels)
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
                temp['size']=int(x['size'])
                temp['status']=int(x['status'])
                temp["timestamp"] =int(x['m_time'])
                temp["time"] =int(x['issuetime'])
                temp["md5sum"] =x['md5sum']
                temp["changes"] = config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+'/api/changelog/'+devi['id']+'/changelog'+str(x['id'])+'.txt'
                temp["changelog"] = x['changelog']
                temp["channel"] = x['channels']
                temp["source_incremental"] = x['source_incremental']
                temp["target_incremental"] = x['target_incremental']
                temp["extra"] = x['extra']
                devbody.append(temp)
            devi['m_detail']= devbody
            products.append(devi)
        body['id']=None
        body['result']=products
        body['error']=None
        result = json.dumps(body,ensure_ascii=False)
        utils.saveBin(dumpfilename,result)
    
    def dumpAllProduct2Json(self):
        self.dump2Json(r"release")
        self.dump2Json(r"nightly")
        self.dump2Json(r"all")
