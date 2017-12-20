#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz
# 2017.12.10: Switched into Tornado

import model,config,utils
import time,json,gc
from action.base import base as BaseAction
from tornado import gen
import tornado.web

class PublishIndex(BaseAction):
    '''#生成后台管理的报表并且显示'''
    @tornado.web.authenticated
    def get(self):
        models = model.get_devices()
        prefs = model.get_preferences()
        usrrpt = model.get_user_report_counts()
        devices =[]
        for post in models:
            devi={}
            devi['m_device'] = post['m_device']
            devi['m_modname'] = post['m_modname']
            devi['m_modpicture'] = post['m_modpicture']
            devi['m_moddescription'] = post['m_moddescription']
            devi['m_time'] = int(post['m_time'])
            devi['m_count'] = model.get_devices_counts_byname(devi['m_device'])
            devi['m_detail'] = {'version':""}
            mdtop = model.get_roms_by_devicesname(devi['m_device'],5)
            for itm in mdtop:
                devi['m_detail'] = itm
                break
            devices.append(devi)
        self.render("publish_index.html", models=devices,  prefs=prefs, netpref=config.netpref, usrrpt=usrrpt, strtime=utils.strtime)


class ChangePwd(BaseAction):
    '''#更换管理员密码'''
    @tornado.web.authenticated
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        pwd2 = self.get_argument("password2")
        if(password and password == pwd2):
            model.post_changeuser(str(username),password)
            self.seeother('/publish')
        else: 
            self.write("password not match!")
        
class PublishNewApp(BaseAction):
    '''#发布新的应用'''
    @tornado.web.authenticated
    def get(self):
        if self.primissived():
            x={
            'a':self.get_argument("a",""),
            'mdevice':self.get_argument("mdevice",""),
            'mmod':self.get_argument("mmod","")
            }
            tmd = None
            if (x['a']=='del'):
                mdevice =x['mdevice']
                model.del_device(mdevice)
                #管理员更改了数据，把产品数据导出成json文件
                self.dumpAllProduct2Json()
                self.seeother("/publish")
                return
            elif (x['a']=='edit'):
                mdevice =x['mdevice']
                tmd = model.get_devices_byname(mdevice)
            self.render("publish_device.html",pupdate=tmd,ptitle="发布新产品")
    
    @tornado.web.authenticated   
    def post(self):
        if self.primissived():
            x={
            'a':self.get_argument("a",""),
            'mdevice':self.get_argument("mdevice",""),
            'mname':self.get_argument("mname",""),
            'mpicture':self.request.files.items(),
            'mdescription':self.get_argument("mdescription","")
            }
            if (x['a']=='add'):
                mdevice =x['mdevice']
                mname = x['mname']
                mdscpt = x['mdescription']
                mtime = int(time.time())
                picname ="static/images/appdefault.png"
                if (len(x['mpicture'])>0):
                    (field, mpic) = x['mpicture'][0]
                    for picfile in mpic:
                        picname ="static/images/"+ (picfile["filename"])
                        #1, 保存新应用的图标
                        utils.saveBin(picname, picfile["body"])
                #2, 为上传的增加保存目录，请确保这里有权限操作
                utils.createDirs("static/downloads/"+mdevice)
                #3, 保存在数据库里
                model.save_device(mdevice, mname, picname, mdscpt, mtime, self.current_user)
            #管理员更改了数据，把产品数据导出成json文件
            self.dumpAllProduct2Json()
            self.seeother("/publish")

class PublishNewVersion(BaseAction):
    '''发布更新版本'''
    @tornado.web.authenticated
    def get(self,modname):
        if self.primissived():
            pupgrade =None 
            x={
            'a':self.get_argument("a",""),
            't':self.get_argument("t",""),
            'wid':self.get_argument("wid",0)
            }
            if (x['a']=='edit' and x['t']=='full'):
                wid = x['wid']
                pupgrade = model.get_rom_by_wid(wid)
            self.render("publish_rom.html",pupgrade=pupgrade,ptitle="添加新条目")
    
    @tornado.web.authenticated
    def post(self,modname):
        x={
            'a':self.get_argument("a",""),
            't':self.get_argument("t",""),
            'wid':self.get_argument("wid","0"),
            'version':self.get_argument("version",""),
            'versioncode':self.get_argument("versioncode",""),
            'changelog':self.get_argument("changelog",""),
            'md5sum':self.get_argument("md5sum",""),
            'url':self.get_argument("url",""),
            'size':self.get_argument("size",0),
            'source_incremental':self.get_argument("source_incremental",""),
            'target_incremental':self.get_argument("target_incremental",""),
            'extra':self.get_argument("extra",""),
            'md5sum':self.get_argument("md5sum",""),
            'api_level':self.get_argument("api_level",23),
            'status':self.get_argument("status",0),
            'ch1':self.get_argument("ch1",""),
            'ch2':self.get_argument("ch2",""),
            'ptoken':self.get_argument("ptoken",""),
            'muploadedfile':self.request.files.items()
        }
        ptoken = x['ptoken']
        privileged = self.hasPrivilege(ptoken)
        #计算特权的token，只有持有预置secret的自动发布程序才有特权。
        if self.primissived() or privileged:
            if (x['a']=='add' and x['t']=='full'):
                wid = x['wid']
                version = x['version']
                versioncode = x['versioncode']
                changelog=x['changelog']
                md5sum=x['md5sum']
                url = x['url']
                size = x['size']
                #自定义的状态，从后台传递过来
                status = x['status']
                filename = x['url'].split('/')[-1]
                if (len(x['muploadedfile'])>0):
                    (field, upedF) = x['muploadedfile'][0]
                    for upedFile in upedF:
                        #如果是管理员上传的文件，则覆盖掉表单上填写的值
                        filename = upedFile["filename"]
                        print 'filename=',filename, type(filename)
                        upFileName = u'static/downloads/'+modname+ u'/' + filename
                        print upFileName
                        utils.createDirs("static/downloads/"+modname)
                        utils.saveBin(upFileName, upedFile["body"])
                        url =  config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+"/"+ upFileName
                        size = len(upedFile["body"])
                        if (md5sum== u""):
                            md5sum = utils.GetFileMd5(upFileName)
                api_level=x["api_level"]
                #一个条目支持多个标签
                channels = x["ch1"] + x["ch2"]
                #用于增量升级的选项
                source_incremental = x['source_incremental']
                target_incremental=x['target_incremental']
                #额外的信息，用户自己填写
                extra =x['extra']
                issuetime = int(time.time())
                m_time = issuetime
                model.save_rom_new(wid,modname, version, versioncode, changelog, filename, url, size, md5sum, status, channels, source_incremental, target_incremental, extra, api_level, self.current_user,issuetime, m_time)
            #管理员更改了数据，把产品数据导出成json文件
            self.dumpAllProduct2Json()
            if(privileged):
                return "Post rom ok!."
            else:
                self.seeother("/publish/romslist/"+modname)
       
class PublishRomList(BaseAction):
    '''#查看已经发布的rom列表'''
    @tornado.web.authenticated
    def get(self,modname):
        if self.primissived():
            x={
            'a':self.get_argument("a",""),
            't':self.get_argument("t",""),
            'wid':self.get_argument("wid",0)
            }
            if (x['a']=='del' and x['t']=="full"):
                wid = x['wid']
                model.delete_rom_by_id(wid)
                self.seeother("/publish/romslist/"+modname)
            if (x['a']=='edit' and x['t'] =="full"):
                wid = x['wid']
                self.seeother("/publish/rom/"+modname+"?a=edit&t=full&wid="+wid)
            romlists = model.get_roms_by_devicesname(modname,-1)
            return self.render("publish_romlist.html", netpref=config.netpref, name=modname, roms=romlists, ptitle ="已经发布的更新列表", strdate=utils.strtime, getStatuStr=config.getStatuStr)
            
class UserReport(BaseAction):
    '''#查看后台用户反馈'''
    @tornado.web.authenticated
    def get(self):
        if self.primissived():
            x={
            'a':self.get_argument("a",""),
            'p':self.get_argument("t",0),
            'pid':self.get_argument("pid",0)
            }
            if (x['a']=="del"):
                pid = x['pid']
                model.del_user_report(pid)
                self.seeother('')
            pg = int(x['p'])
            pgcon = 50
            pages = 1+ model.get_user_report_counts()/pgcon
            result = model.get_user_report(pg ,pgcon)
            print(result)
            print(type(result))
            return self.render("publish_ureport.html", ureports=result, pages=pages, ptitle="后台用户反馈", strdate=utils.strtime)

class UserAdmin():
    '''管理网站用户'''
    @tornado.web.authenticated
    def get(BaseAction):
        self.render("publish_users.html")
    
class Login(BaseAction):
    '''#管理员登录后台'''  
    @gen.coroutine  
    def get(self):
        """ View single post """
        if self.get_current_user():
            self.seeother('/publish')
        self.render("login.html",loginpoint=config.ADMIN_LOGIN)
    
    @gen.coroutine
    def post(self):
        uname = self.get_argument("uname",'')
        pword = self.get_argument("pword",'')
        print uname, pword
        if (model.login_post(uname,pword)):
            #return "login success"
            self.set_secure_cookie("uname", uname, expires_days=2)
            self.seeother('/publish')
        else:
            self.clear_cookie(uname)
            self.seeother(config.ADMIN_LOGIN)
            
class Quit(BaseAction):
    '''#管理员退出登录'''
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("uname")
        self.seeother(config.ADMIN_LOGIN)
