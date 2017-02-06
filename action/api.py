#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz

import web
import model,config,utils
import json,time,urllib
from action.base import base as BaseAction

class API(BaseAction):
    '''#用于手机客户端的api接口实现'''
    def GET(self):
        return ''

    def POST(self):
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
            if (method == 'get_all_builds' and device != '' and len(channels)>0 and source_incremental != ''):
                print 'recieve a valid Client request :',method,device,channels,source_incremental
                mods =model.get_devices_byname(device)
                for x in mods: 
                    mod_id = x['mod_id']
                if(channels[0]==u"nightly"):
                    channels="nightly"
                else: channels="release"
                availableRoms = model.get_available_roms_by_modelid(mod_id,channels)
                if (availableRoms!=None): 
                    for x in availableRoms:
                        temp={}
                        temp['version']=x['version']
                        temp['versioncode']=x['versionode']
                        temp["api_level"]= x['api_level']
                        temp["filename"] = x['filename'] 
                        temp["url"] = x['url']
                        temp['size']=x['size']
                        temp['status']=x['status']
                        temp["timestamp"] =x['m_time']
                        temp["time"] =x['issuetime']
                        temp["md5sum"] =x['md5sum']
                        temp["changes"] = config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+'/api/changelog/'+device+'/changelog'+str(x['id'])+'.txt'
                        temp["changelog"] = x['changelog']
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
        
class API_DELTA(BaseAction):
    '''给手机客户端返回增量升级的信息'''
    def POST(self):
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
                api["version"] = x["target_incremental"]
        print api
        result = json.dumps(api)
        return result
        
class API_CHANGELOG(BaseAction):
    '''#客户端变化日志请求'''
    def GET(self,mdevice,romid):
        #web.ctx.session.kill()
        changelog = model.get_changelog_bydevice(mdevice,romid)
        result =''
        for x in changelog:
            result = x['changelog']
            break
        #Do not return result, we use the render to solve the default Charset into utf-8
        _render = self.renderDefault
        return _render.plaintext(result)
        
class API_USER_REPORT(BaseAction):
    '''#客户端提交反馈意见'''
    def GET(self):
        #web.ctx.session.kill()
        return self.renderDefault.plaintext(200)
        
    def POST(self):
        #web.ctx.session.kill()
        x= web.input(fprint="",fcontent = "")
        fprint =x['fprint']
        fcontent = x['fcontent']
        now = int(time.time())
        if (fcontent!='' and fprint !='' and (len(fcontent)<1000) and (len(fprint)<1000) ):
            model.post_user_report(fprint,fcontent,now)
        return "thank you for report!"

class API_APPUP(BaseAction):
    '''#各个产品线的升级api接口实现'''
    def GET(self,method,device,channels):
        #web.ctx.session.kill()
        api={}
        body=[]
        mod_id =0
        webinput= web.input(source_version="")
        source_version = webinput['source_version']
        if (method == 'upgrade' and device != '' and channels!='' and source_version != ''):
            print 'recieve a valid Client request :',method,device,channels,source_version
            mods =model.get_devices_byname(device)
            for x in mods: 
                mod_id = x['mod_id']
            if(channels.find(u"nightly")>-1):
                channels="nightly"
            else: channels="release"
            availableRoms = model.get_available_roms_by_modelid(mod_id,channels)
            if (availableRoms!=None): 
                for x in availableRoms:
                    temp={}
                    temp['version']=x['version']
                    temp['versioncode']=x['versioncode']
                    temp["api_level"]= x['api_level']
                    temp["filename"] = x['filename']
                    temp["url"] = x['url']
                    temp["size"] = x['size']
                    temp['status']=x['status']
                    temp["timestamp"] =x['m_time']
                    temp["time"] =x['issuetime']
                    temp["md5sum"] =x['md5sum']
                    temp["changes"] = config.netpref['SCHEME']+'://'+config.netpref['SERVER_HOST']+':'+config.netpref['SERVER_PORT']+'/api/changelog/'+device+'/changelog'+str(x['id'])+'.txt'
                    temp["changelog"] = x['changelog']
                    temp["channel"] = x['channels']
                    body.append(temp)
        else:
            print 'recieve a INVALID Client request,pass:',method,device,channels,source_version
        api['id']=device
        api['result']=body
        api['error']=None
        print api
        result = json.dumps(api,ensure_ascii=False)
        return result.encode('utf-8')
