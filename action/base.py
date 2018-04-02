#!/usr/bin/env python3
#coding=utf-8
# web.py In Memery of Aaron Swartz
# 2017.12.10: Switched into Tornado

import tornado.web
import tornado.template
import model,config,utils
import json,time,base64
import urllib.request,urllib.error,urllib.parse
import re

class base(tornado.web.RequestHandler):

    ### Templates
    t_globals = {
        'strdate':utils.strtime,
        'inttime':utils.inttime,
        'abs2rev':utils.abs2rev,
        'getStatuStr':config.getStatuStr
    }

    def get_current_user(self):
        user_id =  self.get_secure_cookie("uname")
        if not user_id:
            return None
        if(self.isValidUser(user_id)):
            return user_id
        else: return None
    
    def get_template_path(self):
        return "templates/backend"
    
    def countPrivilege(self):
        '''根据预置的秘密计算一个时间相关的随机数，每分钟变一次，用来发布ROM的时候做验证。'''
        secret = config.AUTOPUB_SECRET
        salt = time.strftime("%Y-%m-%d %H:00",time.localtime(time.time()))
        ptoken = utils.sha256(secret+salt)
        print("hasPrivilege: ptoken is:",ptoken)
        return ptoken
        
    def hasPrivilege(self,ptoken):
        token = self.countPrivilege()
        print("hasPrivilege: token is:"+ token + " ptoken is:"+ ptoken)
        return token == ptoken
    
    def login_post(self, username,password):
        '''验证网站管理员登录'''
        user = model.get_user_by_uname(username)
        if (user is None):
            return False
        usr = user["u_name"]
        pwd = user["u_password"]
        j1 = (username == usr)
        j2 = (pwd ==  utils.sha256(password))
        return j1 and j2
    
    def accessAdmin(self):
        '''判断当前用户是否有管理员权限'''
        uinfo = model.get_user_by_uname(self.current_user)
        return (uinfo['u_role'] == "admin")
    
    def accessSelf(self,uname):
        '''判断参数用户名是否是自己'''
        curuname = self.current_user.decode()
        return curuname ==  uname
    
    def isValidUser(self, uname):
        '''本地存在此用户'''
        uinfo = model.get_user_by_uname(uname)
        return not(uinfo == None)
    
    def permissionDenied(self):
        self.write("Permission denied!")
        return
       
    def logI(self, fcontent):
        self.log("INFO",fcontent)
    
    def logW(self, fcontent):
        self.log("WARNING",fcontent)
    
    def logE(self, fcontent):
        self.log("ERROR",fcontent)
    
    def log(self, ftag, fcontent):
        x_real_ip = self.request.headers.get("X-Real-IP")
        x_forwarded_ip = self.request.headers.get("X-Forwarded-For")
        remote_ip = x_real_ip or x_forwarded_ip or self.request.remote_ip
        uname = self.current_user or b""
        model.post_audit_log(ftag, remote_ip+": "+uname.decode()+":"+fcontent,int(time.time()) )
    
    def seeother(self,path):
        self.redirect(config.netpref['SCHEME']+"://"+config.netpref['SERVER_HOST']+":"+config.netpref['SERVER_PORT']+path)

    def dumpLatestReleaseSymbols(self):
        '''Follow these rules:
        1. Export all newest release version into ONE standalone HTML file. 
        2. Copy all newest relaesed file into standalone folder.
        3. Administrator could copy this folder to anywhere he wanted to.
         '''
        models = model.get_devices()
        prefs = model.get_preferences()
        exportRoot= prefs.get('site_export_path','/tmp/export/')
        # create exported path
        utils.createDirs(exportRoot)
        # start export
        for post in models:
            if(post.get('m_pub_ipv4','0') != '1'):
                continue
            post['m_detail']=model.get_available_roms_by_modelid(post['m_device'],"release")
            #1. rewrie the url, 2. create the softlink for latest downloadfile.
            for detail in post['m_detail']:
                i_realName = detail.get('filename','')
                i_path = 'static/downloads/'+ post['m_device'] +'/'
                fcut =  detail.get('filename','').split('.')
                if(len(fcut)<=0):continue
                f_apx = fcut[-1]
                detail['filename'] = post['m_device']+'.latest.'+f_apx
                # detail['url']= prefs.get('site_domain_ipv4','')+ "/" + detail['filename']
                detail['url']= "/" + detail['filename']
                # create softlink
                print('dumping symbol link:'+ i_path + detail['filename'])
                utils.cp(config.ROOT_PATH + i_path + i_realName, exportRoot + detail['filename'])
        # render to standalone html.
        tloader = tornado.template.Loader(config.DEFAULT_FRONT_THEME)
        result  = tloader.load("index_latest.html").generate(models=models, prefs=prefs, strtime=utils.strtime,getStatuStr=config.getStatuStr)
        utils.saveBin(exportRoot+'index.html',result)
        # copy rest static files
        utils.cp_r(config.ROOT_PATH + 'static/bootstrap', exportRoot +'static/bootstrap')
        utils.cp_r(config.ROOT_PATH + 'static/images', exportRoot +'static/images')
        utils.cp(config.ROOT_PATH + 'static/jquery-1.12.4.min.js', exportRoot +'static/jquery-1.12.4.min.js')

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
        '''
        for post in models:
            post['id'] = post['m_device']
            if (channels==r'all'):
                post['m_detail']=model.get_roms_by_devicesname(post['m_device'],-1)
            else:
                post['m_detail']=model.get_available_roms_by_modelid(post['m_device'], channels)
        '''
        body['id']=None
        body['result']=products
        body['error']=None
        result = json.dumps(body,ensure_ascii=False)
        utils.saveBin(dumpfilename,result)
    
    def dumpAllProduct2Json(self):
        self.dump2Json(r"release")
        self.dump2Json(r"nightly")
        self.dump2Json(r"all")
        self.dumpLatestReleaseSymbols()
