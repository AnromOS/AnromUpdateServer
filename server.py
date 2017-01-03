#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz

import web
import model,config
import action

### Url mappings
urls = (
    ##for web view
    '/',                'action.cms.Index',
    '/allroms/(.*?)',   'action.cms.Allroms', #/allroms/[devicename]
    '/api',             'action.api.API', #for client API
    '/api/v1/build/get_delta',  'action.api.API_DELTA', #for delta client API
    '/api/changelog/(.*?)/changelog(.*?).txt',      'action.api.API_CHANGELOG', #show changelogs 
    '/api/report',              'action.api.API_USER_REPORT', #for delta client API
    config.ADMIN_LOGIN,         'action.admin.Login', #for web
    '/publish',                 'action.admin.PublishIndex',# for web 
    '/publish/device',          'action.admin.PublishNewApp', #for web 发布新的应用
    '/publish/romslist/(.*?)/(.*?)',    'action.admin.PublishRomList', #for web
    '/publish/rom/(.*?)/(.*?)', 'action.admin.PublishNewVersion', #for web 发布更新版本
    '/publish/userreport',      'action.admin.UserReport', #for web 
    '/publish/quit',            'action.admin.Quit', #for web
    '/publish/changepwd',       'action.admin.ChangePwd', #for web
    # Make url ending with or without '/' going to the same class
    '/(.*)/',                   'action.cms.redirect', 
)

def notfound(errno=404):
    r_index= "Windows IIS 5.0: "+str(errno)
    return  web.notfound(r_index)

if __name__ == '__main__':
    web.config.debug = False
    app = web.application(urls, globals())
    app.notfound = notfound
    sessionstore = model.MemStore()  
    session = web.session.Session(app, sessionstore,initializer={'login': 0,'ulogin':0})
    def session_hook():
        web.ctx.session = session
    app.add_processor(web.loadhook(session_hook))
    web.config.session_parameters['timeout'] = 86400*2  #24 * 60 * 60, # 24 hours   in seconds 2days
    web.config.session_parameters['ignore_expiry'] = False
    app.run()
