#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz

import web
import model,config,utils
import time,json
from action.base import base as BaseAction

class PublishIndex(BaseAction):
    '''#生成后台管理的报表并且显示'''
    def GET(self):
        if self.logged():
            models = model.get_devices()
            prefs = model.get_preferences()
            usrrpt = model.get_user_report_counts()
            r_index =self.renderAdmin.publish_index(models,prefs,config.netpref,usrrpt)
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
                raise web.seeother('/publish')
            else: 
                return "password not match!"
        else:
            return ""
        
class PublishNewApp(BaseAction):
    '''#发布新的应用'''
    def GET(self):
        if self.logged():
            x= web.input(a="",mdevice="",mmod="")
            if (x['a']=='del'):
                did =x['did']
                mdevice =x['mdevice']
                model.del_device(did,mdevice)
                #管理员更改了数据，把产品数据导出成json文件
                dumpAllProduct2Json()
                web.seeother("/publish")
                return
            return self.renderAdmin.publish_device()
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
                picname ="static/images/"+ (mpic.filename.decode('utf-8'))
                #1, 保存新应用的图标
                utils.saveBin(picname, mpic.value)
                #2, 为上传的增加保存目录，请确保这里有权限操作
                utils.createDirs("static/downloads/"+mdevice)
                #3, 保存在数据库里
                model.save_device(mdevice, mname, picname, mdscpt, mtime)
            #管理员更改了数据，把产品数据导出成json文件
            dumpAllProduct2Json()
            web.seeother("/publish")
        else:
            raise web.notfound(" operation not authrized.")

class PublishNewVersion(BaseAction):
    '''发布更新版本'''
    def GET(self,modid,modname):
        if self.logged():
            pdelta =None 
            pupgrade =None 
            x=web.input(a="",t="")
            if (x['a']=='edit' and x['t']=='delta'):
                wid = x['wid']
                pdelta = model.get_romdelta_by_wid(wid)
            if (x['a']=='edit' and x['t']=='full'):
                wid = x['wid']
                pupgrade = model.get_rom_by_wid(wid)
            return self.renderAdmin.publish_rom(pdelta,pupgrade)
        else:
            raise web.notfound(" operation not authorized.")
    
    def POST(self,modid,modname):
        x=web.input(a='',t='',api_level=23,channels="nightly", ptoken="", muploadedfile={})
        ptoken = x['ptoken']
        privileged = self.hasPrivilege(ptoken)
        #计算特权的token，只有持有预置secret的自动发布程序才有特权。
        if self.logged() or privileged:
            if (x['a']=='add' and x['t']=='full'):
                wid = x['wid']
                mod_id=int(modid)
                if mod_id==999999:
                    tmd = model.find_modid_bydevice(modname)[0]['mod_id']
                    mod_id=int(tmd)
                incremental = x['incremental']
                changelog=x['changelog']
                #filename =x['filename']
                upedFile= x['muploadedfile']
                url = x['url']
                filename = x['url'].split('/')[-1]
                if not (upedFile.filename==u""):
                    #如果是管理员上传的文件，则覆盖掉表单上填写的值
                    filename = upedFile.filename.decode('utf-8')
                    print 'filename=',filename, type(filename)
                    upFileName = u'static/downloads/'+modname+ u'/' + filename
                    print upFileName
                    utils.saveBin(upFileName, upedFile.value)
                    url =  config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+"/"+ upFileName
                md5sum=x['md5sum']
                api_level=x["api_level"]
                channels = x["channels"]
                #m_time = int(incremental.split('.')[-1])
                issuetime = int(time.time())
                m_time = issuetime
                model.save_rom_new(wid,mod_id, incremental, changelog, filename, url, md5sum, 2, channels, api_level, issuetime, m_time)
            if(x['a']=='add' and x['t']=='delta'):
                wid = x['wid']
                mod_id=int(modid)
                source_incremental = x['source_incremental']
                target_incremental=x['target_incremental']
                #filename =x['filename']
                filename = x['url'].split('/')[-1]
                url = x['url']
                md5sum=x['md5sum']
                m_time = int(time.time())
                model.save_romdelta_new(wid,mod_id, 0, filename, url, md5sum, 2, source_incremental, target_incremental,  m_time)
            #管理员更改了数据，把产品数据导出成json文件
            dumpAllProduct2Json()
            if(privileged):
                return "Post rom ok!."
            else:
                web.seeother("/publish")
        else:
            raise web.notfound(" operation not authrized.")
       
class PublishRomList(BaseAction):
    '''#查看已经发布的rom列表'''
    def GET(self,modid,modname):
        if self.logged():
            x=web.input(a="",t="")
            if (x['a']=='del' and x['t']=="full"):
                wid = x['wid']
                model.delete_rom_by_id(wid)
                web.seeother("/publish/romslist/"+modid+"/"+modname)
            if (x['a']=='edit' and x['t'] =="full"):
                wid = x['wid']
                web.seeother("/publish/rom/"+modid+"/"+modname+"?a=edit&t=full&wid="+wid)
            if (x['a']=='del' and x['t'] =="delta"):
                wid = x['wid']
                model.delete_romdelta_by_id(wid)
                web.seeother("/publish/romslist/"+modid+"/"+modname)
            if (x['a']=='edit' and x['t'] =="delta"):
                wid = x['wid']
                web.seeother("/publish/rom/"+modid+"/"+modname+"?a=edit&t=delta&wid="+wid)
            romlists = model.get_all_roms_by_modelid(modid)
            deltaromlists =model.get_romdelta_bymodid(modid)
            return self.renderAdmin.publish_romlist(config.netpref, modname,romlists,deltaromlists,"已经发布的rom列表")
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
                web.seeother('')
            pg = int(x['p'])
            pgcon = 50
            pages = 1+ model.get_user_report_counts()/pgcon
            result = model.get_user_report(pg ,pgcon)
            return self.renderAdmin.publish_ureport(result, pages, "后台用户反馈")
        else:
            raise web.notfound(" operation not authorized.")
       
class Login(BaseAction):
    '''#管理员登录后台'''
    form = web.form.Form(
        web.form.Textbox('uname', web.form.notnull, size=30,description="uname:"),
        web.form.Password('pword', web.form.notnull, size=30,description="pword:"),
        web.form.Button('Login'),
    )
    
    def GET(self):
        """ View single post """
        if self.logged():
            raise web.seeother('/publish')
        form = self.form()
        return self.renderDefault.login(form,config.ADMIN_LOGIN)
        
    def POST(self):
        render = self.renderDefault
        form = self.form()
        if not form.validates():
            return render.login(form)
        if (model.login_post(form.d.uname,form.d.pword)):
            #return "login success"
            web.ctx.session.login= 1
            raise web.seeother('/publish')
        else:
            web.ctx.session.login= 0
            raise web.seeother(config.ADMIN_LOGIN)
            
class Quit(BaseAction):
    '''#管理员退出登录'''
    def GET(self):
        web.ctx.session.kill()
        raise web.seeother(config.ADMIN_LOGIN)

def dumpAllProduct2Json():
    '''把所有的数据库中的数据输出到json文件'''
    print("Dumping all products data to one json file....")
    models = model.get_devices()
    devices =[]
    body={}
    products=[]
    for post in models:
        devi={}
        devi['mod_id']= post['mod_id']
        devi['m_device'] = post['m_device']
        devi['m_modname'] = post['m_modname']
        devi['m_modpicture'] = post['m_modpicture']
        devi['m_moddescription'] = post['m_moddescription']
        #devi['m_detail']=model.get_top5_roms_by_modelid(devi['mod_id'])
        devi['m_detail']=model.get_all_roms_by_modelid(devi['mod_id'])
        devices.append(devi)
    for devi in devices:
        devbody =[]
        for x in devi['m_detail']:
            temp={}
            temp['incremental']=x['incremental']
            temp["api_level"]= x['api_level']
            temp["filename"] = x['filename']
            temp["url"] = x['url']
            temp["timestamp"] =x['m_time']
            temp["time"] =x['issuetime']
            temp["md5sum"] =x['md5sum']
            temp["changes"] = config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+'/api/changelog/'+devi['m_device']+'/changelog'+str(x['id'])+'.txt'
            temp["changelog"] = x['changelog']
            temp["channel"] = x['channels']
            devbody.append(temp)
        devi['m_detail']= devbody
        products.append(devi)
    body['id']=None
    body['result']=products
    body['error']=None
    result = json.dumps(body,ensure_ascii=False)
    utils.saveBin(r'static/downloads/allproducts.json',result.encode('utf-8'))
