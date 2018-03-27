#!/usr/bin/env python3
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
        users = model.get_all_users()
        curusr = model.get_user_by_uname(self.current_user)
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
        self.render("publish_index.html", models=devices,  prefs=prefs, netpref=config.netpref, usrrpt=usrrpt,users=users,curusr=curusr, strtime=utils.strtime, getStatuStr=config.getStatuStr, accessAdmin = self.accessAdmin())

class PublishNewApp(BaseAction):
    '''#发布新的应用'''
    @tornado.web.authenticated
    def get(self):
        x={
        'a':self.get_argument("a",""),
        'mdevice':self.get_argument("mdevice",""),
        'mmod':self.get_argument("mmod","")
        }
        tmd = None
        if (x['a']=='del'):
            mdevice =x['mdevice']
            model.del_device(mdevice)
            self.logW(u"删除产品线:%s"%(mdevice))
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
        a = self.get_argument("a","")
        if (a == 'add'):
            mdevice = self.get_argument("mdevice","")
            mname = self.get_argument("mname","")
            mdscpt = self.get_argument("mdescription","")
            mupfiles = list(self.request.files.items())
            mtime = int(time.time())
            picname =config.DEFAULT_APPCAPTION
            #2, 保存标题图和封面图
            for (field, mpic) in mupfiles:
                for picfile in mpic:
                    picname ="/static/images/"+ (picfile["filename"])
                    #1, 保存新应用的图标
                    utils.saveBin('.'+picname, picfile["body"])
            #2, 为上传的增加保存目录，请确保这里有权限操作
            utils.createDirs("static/downloads/"+mdevice)
            #3, 保存在数据库里
            model.save_device(mdevice, mname, picname, mdscpt, mtime, self.current_user)
            self.logI(u"保存发布产品线信息:%s:%s"%(mdevice, mname))
        #管理员更改了数据，把产品数据导出成json文件
        self.dumpAllProduct2Json()
        self.seeother("/publish")

class PublishNewVersion(BaseAction):
    '''发布更新版本'''
    @tornado.web.authenticated
    def get(self,modname):
        pupgrade =None 
        x={
        'a':self.get_argument("a",""),
        't':self.get_argument("t",""),
        'wid':self.get_argument("wid",0)
        }
        if (x['a']=='edit' and x['t']=='full'):
            wid = x['wid']
            pupgrade = model.get_rom_by_wid(wid)
        if (x['a']=='del' and x['t']=="full"):
            wid = x['wid']
            model.delete_rom_by_id(wid)
            self.logW(u"删除版本信息:%s:%s"%(modname, wid))
            self.dumpAllProduct2Json()
            self.seeother("/publish/romslist/"+modname)
            return
        self.render("publish_rom.html",pupgrade=pupgrade,ptitle="添加新条目", accessAdmin = self.accessAdmin())
    
    @tornado.web.authenticated
    def post(self,modname):
        a = self.get_argument("a","")
        t = self.get_argument("t","")
        ptoken = self.get_argument("ptoken","")
        privileged = self.hasPrivilege(ptoken)
        #计算特权的token，只有持有预置secret的自动发布程序才有特权。
        if True or privileged:
            if (a=='add' and t =='full'):
                wid = self.get_argument("wid","0")
                version = self.get_argument("version","")
                versioncode = self.get_argument("versioncode","")
                changelog= self.get_argument("changelog","")
                md5sum= self.get_argument("md5sum","")
                url = self.get_argument("url","")
                size = self.get_argument("size",0)
                #自定义的状态，从后台传递过来
                status = self.get_argument("status",0)
                filename = url.split('/')[-1]
                muploadedfile = list(self.request.files.items())
                if (len(muploadedfile)>0):
                    (field, upedF) = muploadedfile[0]
                    for upedFile in upedF:
                        #如果是管理员上传的文件，则覆盖掉表单上填写的值
                        filename = upedFile["filename"]
                        print('filename=' + filename)
                        upFileName = u'/static/downloads/'+modname+ u'/' + filename
                        print(upFileName)
                        utils.createDirs("static/downloads/"+modname)
                        utils.saveBin('.'+upFileName, upedFile["body"])
                        url =  config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+ upFileName
                        size = len(upedFile["body"])
                        if (md5sum== u""):
                            md5sum = utils.GetFileMd5('.'+ upFileName)
                api_level= self.get_argument("api_level",23)
                #一个条目支持多个标签
                ch1 = self.get_argument("ch1","")
                ch2 = self.get_argument("ch2","")
                channels = ch1
                if self.accessAdmin():
                    channels = ch1 + ch2
                #用于增量升级的选项
                source_incremental = self.get_argument("source_incremental","")
                target_incremental = self.get_argument("target_incremental","")
                #额外的信息，用户自己填写
                extra = self.get_argument("extra","")
                issuetime = int(time.time())
                m_time = issuetime
                model.save_rom_new(wid,modname, version, versioncode, changelog, filename, url, size, md5sum, status, channels, source_incremental, target_incremental, extra, api_level, self.current_user,issuetime, m_time)
                self.logI(u"保存发布版本信息:%s:%s"%(modname, version))
            #管理员更改了数据，把产品数据导出成json文件
            self.dumpAllProduct2Json()
            if(privileged):
                self.write("Post rom ok!.")
            else:
                self.seeother("/publish/romslist/"+modname)
       
class PublishRomList(BaseAction):
    '''#查看已经发布的rom列表'''
    @tornado.web.authenticated
    def get(self,modname):
        romlists = model.get_roms_by_devicesname(modname,-1)
        users = model.get_all_users()
        self.render("publish_romlist.html", netpref=config.netpref, name=modname, roms=romlists,users=users,  ptitle ="已经发布的更新列表", strdate=utils.strtime, getStatuStr=config.getStatuStr)
            
class UserReport(BaseAction):
    '''#查看后台用户反馈'''
    @tornado.web.authenticated
    def get(self):
        x={
        'a':self.get_argument("a",""),
        'p':self.get_argument("t",0)
        }
        if (x['a']=="del"):
            model.del_user_report()
        pg = int(x['p'])
        pgcon = 50
        pages = 1+ int(model.get_user_report_counts()/pgcon)
        result = model.get_user_report(pg ,pgcon)
        self.render("publish_ureport.html", ureports=result, pages=pages, ptitle="后台用户反馈", strtime=utils.strtime)

class PublishNewUser(BaseAction):
    '''管理网站用户'''
    
    @tornado.web.authenticated
    def get(self):
        x ={
        'a':self.get_argument("a",""),
        'uname':self.get_argument("uname","")
        }
        tmd = None
        title = "添加用户"
        if (x['a']=='del'):
            if self.accessSelf(x['uname']) or (not self.accessAdmin()):
                ##1,不能删除自己, 2 非管理员不能删除别人
                self.permissionDenied()
                return
            self.logW(u"删除开发者信息:%s"%(x['uname']))
            model.del_user(x['uname'])
            self.seeother("/publish")
            return
        elif (x['a']=='edit'):
            if (not self.accessAdmin()) and (not self.accessSelf(x['uname'])) :
                ##1,只能编辑自己, 2 非管理员不能编辑别人
                self.permissionDenied()
                return
            tmd = model.get_user_by_uname(x['uname'])
            title = "编辑用户信息"
        elif not self.accessAdmin():
            self.permissionDenied()
            return
        self.render("publish_user.html",pupdate=tmd, ptitle=title,getStatuStr=config.getStatuStr)
    
    @tornado.web.authenticated
    def post(self):
        a = self.get_argument("a","")
        uname = self.get_argument("uname","")
        urole = self.get_argument("urole","developer")
        upwd1 = self.get_argument("upassword","")
        upwd2 = self.get_argument("upassword2","")
        picname = self.get_argument("upicname",config.DEFAULT_HEAD)
        uavatar = list(self.request.files.items())
        udscpt = self.get_argument("udescription","")
        if not (self.accessSelf(uname) or self.accessAdmin()):
            ##不是自己操作或者不是管理员则返回
            self.permissionDenied()
            return
        if (a =='add'):
            if (not (upwd1 == upwd2)) or (upwd1==""):
                self.write("密码输入不一致")
                return
            mtime = int(time.time())
            if (len(uavatar)>0):
                (field, mpic) = uavatar[0]
                for picfile in mpic:
                    picname ="/static/images/"+ (picfile["filename"])
                    #1, 保存新应用的图标
                    utils.saveBin("."+picname, picfile["body"])
            #3, 保存在数据库里
            self.logI(u"保存开发者信息:%s:%s"%(uname,urole))
            model.add_new_user(uname, utils.sha256(upwd1), urole, picname, udscpt, mtime)
        self.seeother("/publish")

class Audit(BaseAction):
    '''管理审计日志'''
    @tornado.web.authenticated
    def get(self):
        if not self.accessAdmin():
            self.write("Permission Denied.")
            return
        x = {'a':self.get_argument('a',''),
        'p':self.get_argument('p',0),
        'psz':self.get_argument('psz',50)}
        if x['a']=='del':
            model.del_audit_log()
        pg = int(x['p'])
        pgcon = int(x['psz'])
        pages = 1+ int(model.get_audit_log_counts()/pgcon)
        items = model.get_audit_log(pg, pgcon)
        self.render("publish_audit.html", items=items, pages=pages, ptitle="管理审计日志", strtime=utils.strtime)

class WebShell(BaseAction):
    '''shell for server'''
    @tornado.web.authenticated
    def get(self):
        if not self.accessAdmin():
            self.write("Permission Denied.")
            return
        content="You can run any linux command."
        self.render("publish_shell.html",tcontent=content,ptitle="Shell")
    
    @tornado.web.authenticated
    def post(self):
        if not self.accessAdmin():
            self.write("Permission Denied.")
            return
        x={'a':self.get_argument('a',''), 'cmd':self.get_argument('cmd','')}
        self.logW(u"执行命令:%s"%x['cmd'])
        content=utils.run(x['cmd'])
        self.render("publish_shell.html",tcontent=content,ptitle="Shell")

class Login(BaseAction):
    '''#管理员登录后台'''  
    @gen.coroutine  
    def get(self):
        """ View single post """
        if self.get_current_user():
            self.logI(u"登陆成功.")
            self.seeother('/publish')
        else:
            self.render("login.html",loginpoint=config.ADMIN_LOGIN)
    
    @gen.coroutine
    def post(self):
        uname = self.get_argument("uname",'')
        pword = self.get_argument("pword",'')
        if (self.login_post(uname,pword)):
            #return "login success"
            self.logI(u"%s:登陆成功."%uname)
            self.set_secure_cookie("uname", uname, expires_days=None, expires=time.time()+config.COOKIE_EXPIRE )
            self.seeother('/publish')
        else:
            self.logE(u"%s:登陆失败."%uname)
            self.clear_cookie(uname)
            self.seeother(config.ADMIN_LOGIN)
            
class Quit(BaseAction):
    '''#管理员退出登录'''
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("uname")
        self.seeother(config.ADMIN_LOGIN)
