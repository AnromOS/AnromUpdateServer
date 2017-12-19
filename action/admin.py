#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz

import web
import model,config,utils
import time,json,gc
from action.base import base as BaseAction

class PublishIndex(BaseAction):
    '''#生成后台管理的报表并且显示'''
    def GET(self):
        if self.logged():
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
            r_index =self.renderAdmin.publish_index(devices,prefs,config.netpref,usrrpt)
            return r_index
        else:
            raise web.notfound(' operation not authorized.')

class ChangePwd(BaseAction):
    '''#更换管理员密码'''
    def POST(self):
        if self.logged():
            username = web.input().username
            password = web.input().password
            pwd2 = web.input().password2
            if(password == pwd2):
                model.post_changeuser(str(username),password)
                raise self.seeother('/publish')
            else: 
                return "password not match!"
        else:
            return ""
        
class PublishNewApp(BaseAction):
    '''#发布新的应用'''
    def GET(self):
        if self.logged():
            x= web.input(a="",mdevice="",mmod="")
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
            return self.renderAdmin.publish_device(tmd)
        else:
           raise web.notfound(" operation not authorized.")
            
    def POST(self):
        if self.logged():
            x= web.input(a="",mdevice="",mname="",mpicture={},mdescription="")
            if (x['a']=='add'):
                mdevice =x['mdevice']
                mname = x['mname']
                mpic = x.mpicture
                mdscpt = x['mdescription']
                mtime = int(time.time())
                picname ="/static/images/appdefault.png"
                if not (mpic.filename == u""):
                    picname ="static/images/"+ (mpic.filename.decode('utf-8'))
                    #1, 保存新应用的图标
                    utils.saveBin(picname, mpic.value)
                #2, 为上传的增加保存目录，请确保这里有权限操作
                utils.createDirs("static/downloads/"+mdevice)
                #3, 保存在数据库里
                model.save_device(mdevice, mname, picname, mdscpt, mtime, self.getCurrentUser())
            #管理员更改了数据，把产品数据导出成json文件
            self.dumpAllProduct2Json()
            self.seeother("/publish")
        else:
            raise web.notfound(" operation not authrized.")

class PublishNewVersion(BaseAction):
    '''发布更新版本'''
    def GET(self,modname):
        if self.logged():
            pupgrade =None 
            x=web.input(a="",t="")
            if (x['a']=='edit' and x['t']=='full'):
                wid = x['wid']
                pupgrade = model.get_rom_by_wid(wid)
            return self.renderAdmin.publish_rom(pupgrade)
        else:
            raise web.notfound(" operation not authorized.")
    
    def POST(self,modname):
        x=web.input(a='',t='',wid='0', api_level=23,status=0, ch1="", ch2="", ptoken="", muploadedfile={})
        ptoken = x['ptoken']
        privileged = self.hasPrivilege(ptoken)
        #计算特权的token，只有持有预置secret的自动发布程序才有特权。
        if self.logged() or privileged:
            if (x['a']=='add' and x['t']=='full'):
                wid = x['wid']
                upedFile= x['muploadedfile']
                version = x['version']
                versioncode = x['versioncode']
                changelog=x['changelog']
                md5sum=x['md5sum']
                url = x['url']
                size = x['size']
                #自定义的状态，从后台传递过来
                status = x['status']
                filename = x['url'].split('/')[-1]
                if not (upedFile=={}):
                    if not (upedFile.filename==u""):
                        #如果是管理员上传的文件，则覆盖掉表单上填写的值
                        filename = upedFile.filename.decode('utf-8')
                        print 'filename=',filename, type(filename)
                        upFileName = u'static/downloads/'+modname+ u'/' + filename
                        print upFileName
                        utils.createDirs("static/downloads/"+modname)
                        utils.saveBin(upFileName, upedFile.value)
                        url =  config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+"/"+ upFileName
                        size = len(upedFile.value)
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
                model.save_rom_new(wid,modname, version, versioncode, changelog, filename, url, size, md5sum, status, channels, source_incremental, target_incremental, extra, api_level, self.getCurrentUser(),issuetime, m_time)
            #管理员更改了数据，把产品数据导出成json文件
            self.dumpAllProduct2Json()
            if(privileged):
                return "Post rom ok!."
            else:
                self.seeother("/publish/romslist/"+modname)
        else:
            raise web.notfound(" operation not authrized.")
       
class PublishRomList(BaseAction):
    '''#查看已经发布的rom列表'''
    def GET(self,modname):
        if self.logged():
            x=web.input(a="",t="")
            if (x['a']=='del' and x['t']=="full"):
                wid = x['wid']
                model.delete_rom_by_id(wid)
                self.seeother("/publish/romslist/"+modname)
            if (x['a']=='edit' and x['t'] =="full"):
                wid = x['wid']
                self.seeother("/publish/rom/"+modname+"?a=edit&t=full&wid="+wid)
            romlists = model.get_roms_by_devicesname(modname,-1)
            return self.renderAdmin.publish_romlist(config.netpref, modname,romlists,"已经发布的更新列表")
        else:
            raise web.notfound(" operation not authorized.")
            
class UserReport(BaseAction):
    '''#查看后台用户反馈'''
    def GET(self):
        if self.logged():
            x =web.input(a="",p=0)
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
            return self.renderAdmin.publish_ureport(result, pages, "后台用户反馈")
        else:
            raise web.notfound(" operation not authorized.")
class UserAdmin():
    '''管理网站用户'''
    def GET(BaseAction):
        return self.renderAdmin.publish_users()
    
class Login(BaseAction):
    '''#管理员登录后台'''    
    def get(self):
        """ View single post """
        if self.logged():
            raise self.seeother('/publish')
        self.render("login.html",loginpoint=config.ADMIN_LOGIN)
        
    def post(self):
        form = self.form()
        if not form.validates():
            return self.renderDefault.login(form,config.ADMIN_LOGIN)
        if (model.login_post(form.d.uname,form.d.pword)):
            #return "login success"
            web.ctx.session.login= 1
            web.ctx.session.uname= form.d.uname
            raise self.seeother('/publish')
        else:
            web.ctx.session.login= 0
            web.ctx.session.uname= ""
            raise self.seeother(config.ADMIN_LOGIN)
            
class Quit(BaseAction):
    '''#管理员退出登录'''
    def GET(self):
        web.ctx.session.kill()
        raise self.seeother(config.ADMIN_LOGIN)
