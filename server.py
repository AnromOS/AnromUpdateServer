#!/usr/bin/env python
#coding=utf-8
# web.py 框架不错，只可惜作者自杀了, In Memery of Aaron Swartz
""" using webpy 0.37 """
import web
import model,config
import hashlib,json,time,base64,urllib2
import re

### Url mappings
urls = (
    ##for web view
    '/', 'Index',
    '/allroms/(.*?)', 'Allroms',
    '/api','API', #for client API
    '/api/v1/build/get_delta','API_DELTA', #for delta client API
    '/api/changelog/(.*?)/changelog(.*?).txt','API_CHANGELOG', #show changelogs 
    '/api/report','API_USER_REPORT', #for delta client API
    config.ADMIN_LOGIN, 'Login', #for web
    '/publish', 'PublishIndex',# for web 
    '/publish/device','PublishDevice', #for web
    '/publish/romslist/(.*?)/(.*?)','PublishRomList', #for web
    '/publish/rom/(.*?)/(.*?)','PublishRom', #for web
    '/publish/userreport','UserReport', #for web
    '/publish/quit','Quit', #for web
    '/publish/changepwd', 'ChangePwd', #for web
    # Make url ending with or without '/' going to the same class
    '/(.*)/', 'redirect', 
)
web.config.debug = False
purl = re.compile('''http://.*?/(.*?.zip)''')

## trans time like 1333316413.0 into '2012-04-02 05:40:13'
def strtime(time_var):
    return time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime(time_var))

## trans time like '2012-04-02 05:40:13' into 1333316413.0
def inttime(time_str):
    t = time.mktime(time.strptime('2012-04-02 05:40:13',"%Y-%m-%d %H:%M:%S"))
    return t

def abs2rev(absurl):
    #print absurl
    r = purl.findall(absurl)
    for x in r:
       #print 'find next: ',x
       return "/"+x

### Templates
t_globals = {
    'datestr': web.datestr,
    'strdate':strtime,
    'urlquote':urllib2.quote,
    'abs2rev':abs2rev
}

app = web.application(urls, globals())
sessionstore = model.MemStore()  
session = web.session.Session(app, sessionstore,initializer={'login': 0,'ulogin':0})
web.config.session_parameters['timeout'] = 86400*2  #24 * 60 * 60, # 24 hours   in seconds 2days
web.config.session_parameters['ignore_expiry'] = False
render = web.template.render('templates/theme_bootstrap', base='base', globals=t_globals)
renderIndex = web.template.render('templates/theme_bootstrap', base='base_index', globals=t_globals)
renderDefault = web.template.render('templates/theme_bootstrap')

def logged():
    if session.login==1:
        return True
    else:
        return False
        
def createRender():
    return render
    
def notfound(errno=404):
    r_index= "Windows IIS 5.0: "+str(errno)
    return r_index

def countPrivilege():
    '''根据预置的秘密计算一个时间相关的随机数，每分钟变一次，用来发布ROM的时候做验证。'''
    secret = config.AUTOPUB_SECRET
    salt = time.strftime("%Y-%m-%d %H:%M",time.localtime(time.time()))
    ptoken = hashlib.sha256(secret+salt).hexdigest()
    print("hasPrivilege: ptoken is:",ptoken)
    return ptoken
    
def hasPrivilege(ptoken):
    token = countPrivilege()
    print "hasPrivilege: token is:",token ," ptoken is:",ptoken
    return token == ptoken

class Index:
    def GET(self):
        """ Show page """
        #session.kill()
        models = model.get_devices()
        prefs = model.get_preferences()
        devices =[]
        for post in models:
            devi={}
            devi['mod_id']= post['mod_id']
            devi['m_device'] = post['m_device']
            devi['m_modname'] = post['m_modname']
            devi['m_time'] = post['m_time']
            devi['m_detail']=model.get_top5_roms_by_modelid(devi['mod_id'])
            devices.append(devi)
        r_index =renderIndex.index(devices,prefs)
        return r_index

class Allroms:
     def GET(self,mdevice):
        """ Show single page """
        #session.kill()
        self.mod_id =-1
        tmd = model.find_modid_bydevice(mdevice)
        for ff in tmd:
            self.mod_id= int(ff['mod_id'])
            self.modname = ff['m_modname']
            self.mtime = ff['m_time']
        if(self.mod_id ==-1):
            return notfound('该设备不支持。')
        models = model.get_devices()
        devi={}
        devi['mod_id']= self.mod_id
        devi['m_device'] = mdevice
        devi['m_modname'] = self.modname
        devi['m_time'] = self.mtime
        devi['m_detail']=model.get_all_roms_by_modelid(self.mod_id)
        r_index =renderIndex.index_allroms(models,devi)
        return r_index
        
class API:
    '''#用于手机客户端的api接口实现'''
    def GET(self):
        session.kill()
        return ''

    def POST(self):
        session.kill()
        x=web.ctx.env['wsgi.input']
        rawjson = x.readline()
        api={}
        body=[]
        if(rawjson !=None):
            mod_id =0
            req = json.loads(rawjson)
            #print req
            method = req['method']
            device = req['params']['device']
            channels = req['params']['channels']
            source_incremental = req['params']['source_incremental']
            if (method == 'get_all_builds' and device != '' and len[channels]>0 and source_incremental != ''):
                print 'recieve a valid Client request :',method,device,channels,source_incremental
                mods =model.get_devices_byname(device)
                for x in mods: 
                    mod_id = x['mod_id']
                if(channels[0]==u"nightly"):
                    channels="nightly"
                else: channels="snapshot"
                availableRoms = model.get_available_roms_by_modelid(mod_id,channels)
                if (availableRoms!=None): 
                    for x in availableRoms:
                        temp={}
                        temp['incremental']=x['incremental']
                        temp["api_level"]= x['api_level']
                        temp["filename"] = x['filename'] 
                        temp["url"] = x['url']
                        temp["timestamp"] =x['m_time']
                        temp["time"] =x['issuetime']
                        temp["md5sum"] =x['md5sum']
                        temp["changes"] = 'http://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+'/api/changelog/'+device+'/changelog'+str(x['id'])+'.txt'
                        temp["channel"] = x['channels']
                        body.append(temp)
            else:
                print 'recieve a INVALID Client request,pass:',method,device,channels,source_incremental
        api['id']=None
        api['result']=body
        api['error']=None
        print api
        result = json.dumps(api)
        return result
        
class API_DELTA:
    '''给手机客户端返回增量升级的信息'''
    def POST(self):
        session.kill()
        x=web.ctx.env['wsgi.input']
        rawjson = x.readline()
        api={}
        if(rawjson !=None):
            print "receive delta upgrade:" ,rawjson
            mod_id =0
            req = json.loads(rawjson)
            device = req['device']
            source_inc = req['source_incremental']
            target_inc = req['target_incremental']
            mods =model.get_devices_byname(device)
            for x in mods:
                mod_id = x['mod_id']
            print 'mod_id',mod_id
            ava_delta = model.get_available_delta_rom(mod_id,source_inc,target_inc)
            for x in ava_delta:
                api["date_created_unix"]=0
                api["filename"]=x["filename"]
                api["download_url"] = x['url']
                api["md5sum"] = x["md5sum"]
                api["incremental"] = x["target_incremental"]
        print api
        result = json.dumps(api)
        return result
        
class API_CHANGELOG:
    '''#客户端变化日志请求'''
    def GET(self,mdevice,romid):
        session.kill()
        changelog = model.get_changelog_bydevice(mdevice,romid)
        result =''
        for x in changelog:
            result = x['changelog']
            break
        #Do not return result, we use the render to solve the default Charset into utf-8
        _render = renderDefault
        return _render.plaintext(result)
        
class API_USER_REPORT:
    '''#客户端提交反馈意见'''
    def GET(self):
        session.kill()
        return notfound(200)
        
    def POST(self):
        session.kill()
        x= web.input(fprint="",fcontent = "")
        fprint =x['fprint']
        fcontent = x['fcontent']
        now = int(time.time())
        if (fcontent!='' and fprint !='' and (len(fcontent)<1000) and (len(fprint)<1000) ):
            model.post_user_report(fprint,fcontent,now)
        return "thank you for report!"
        
class PublishIndex:
    '''#生成后台管理的报表并且显示'''
    def GET(self):
        if logged():
            render = createRender()
            models = model.get_devices()
            prefs = model.get_preferences()
            usrrpt = model.get_user_report_counts()
            r_index =render.publish_index(models,prefs,config.netpref,usrrpt)
            return r_index
        else:
            return notfound(' operation not authorized.')

class ChangePwd:
    '''#更换管理员密码'''
    def POST(self):
        if logged():
            render = createRender()
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
        
class PublishDevice:
    '''#发布新的机型支持'''
    def GET(self):
        if logged():
            x= web.input(a="",mdevice="",mmod="")
            if (x['a']=='del'):
                did =x['did']
                mdevice =x['mdevice']
                model.del_device(did,mdevice)
                web.seeother("/publish")
                return
            render = createRender()
            return render.publish_device()
        else:
            return notfound(" operation not authorized.")
            
    def POST(self):
        if logged():
            x= web.input(a="",mdevice="",mmod="")
            if (x['a']=='add'):
                mdevice =x['mdevice']
                mmod = x['mmod']
                mtime = int(time.time())
                model.save_device(mdevice, mmod ,mtime)
            web.seeother("/publish")
        else:
            return notfound(" operation not authrized.")

class PublishRom:
    '''发布新的rom'''
    def GET(self,modid,modname):
        if logged():
            pdelta =None 
            pupgrade =None 
            x=web.input(a="",t="")
            if (x['a']=='edit' and x['t']=='delta'):
                wid = x['wid']
                pdelta = model.get_romdelta_by_wid(wid)
            if (x['a']=='edit' and x['t']=='full'):
                wid = x['wid']
                pupgrade = model.get_rom_by_wid(wid)
            render = createRender()
            return render.publish_rom(pdelta,pupgrade)
        else:
            return notfound(" operation not authorized.")
    
    def POST(self,modid,modname):
        x=web.input(a='',t='',api_level=23,channels="RC", ptoken="")
        ptoken = x['ptoken']
        privileged = hasPrivilege(ptoken)
        #计算特权的token，只有持有预置secret的自动发布程序才有特权。
        if logged() or privileged:
            if (x['a']=='add' and x['t']=='full'):
                wid = x['wid']
                mod_id=int(modid)
                if mod_id==999999:
                    tmd = model.find_modid_bydevice(modname)[0]['mod_id']
                    mod_id=int(tmd)
                incremental = x['incremental']
                changelog=x['changelog']
                #filename =x['filename']
                url = x['url']
                filename = x['url'].split('/')[-1]
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
            if(privileged):
                return "Post rom ok!."
            else:
                web.seeother("/publish")
        else:
            return notfound(" operation not authrized.")
       
class PublishRomList:
    '''#查看已经发布的rom列表'''
    def GET(self,modid,modname):
        if logged():
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
            render = createRender()
            romlists = model.get_all_roms_by_modelid(modid)
            deltaromlists =model.get_romdelta_bymodid(modid)
            return render.publish_romlist(model.netpref, modname,romlists,deltaromlists,"已经发布的rom列表")
        else:
            return notfound(" operation not authorized.")
            
class UserReport:
    '''#查看后台用户反馈'''
    def GET(self):
        if logged():
            x =web.input(a="",p=0)
            if (x['a']=="del"):
                pid = x['pid']
                model.del_user_report(pid)
                web.seeother('')
            render = createRender()
            pg = int(x['p'])
            pgcon = 50
            pages = 1+ model.get_user_report_counts()/pgcon
            result = model.get_user_report(pg ,pgcon)
            return render.publish_ureport(result, pages, "后台用户反馈")
        else:
            return notfound(" operation not authorized.")
       
class Login:
    '''#管理员登录后台'''
    form = web.form.Form(
        web.form.Textbox('uname', web.form.notnull, size=30,description="uname:"),
        web.form.Password('pword', web.form.notnull, size=30,description="pword:"),
        web.form.Button('Login'),
    )
    
    def GET(self):
        """ View single post """
        if(logged()):
            raise web.seeother('/publish')
        form = self.form()
        return renderDefault.login(form,config.ADMIN_LOGIN)
        
    def POST(self):
        render = renderDefault
        form = self.form()
        if not form.validates():
            return render.login(form)
        if (model.login_post(form.d.uname,form.d.pword)):
            #return "login success"
            session.login= 1
            raise web.seeother('/publish')
        else:
            session.login= 0
            raise web.seeother(config.ADMIN_LOGIN)
            
class Quit:
    '''#管理员退出登录'''
    def GET(self):
        session.kill()
        raise web.seeother(config.ADMIN_LOGIN)
        
class redirect:
    def GET(self, path):
        web.seeother('/' + path)
        
webcache = model.WebCache()

if __name__ == '__main__':
    app.run()
