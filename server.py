#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz

import web
import model,config
import action.base

### Url mappings
urls = (
    ##for web view
    '/', 'action.base.Index',
    '/allroms/(.*?)', 'action.base.Allroms', #/allroms/[devicename]
    '/api','ac.API', #for client API
    '/api/v1/build/get_delta','action.base.API_DELTA', #for delta client API
    '/api/changelog/(.*?)/changelog(.*?).txt','action.base.API_CHANGELOG', #show changelogs 
    '/api/report','action.base.API_USER_REPORT', #for delta client API
    config.ADMIN_LOGIN, 'action.base.Login', #for web
    '/publish', 'action.base.PublishIndex',# for web 
    '/publish/device','action.base.PublishNewApp', #for web 发布新的应用
    '/publish/romslist/(.*?)/(.*?)','action.base.PublishRomList', #for web
    '/publish/rom/(.*?)/(.*?)','action.base.PublishNewVersion', #for web 发布更新版本
    '/publish/userreport','action.base.UserReport', #for web 
    '/publish/quit','action.base.Quit', #for web
    '/publish/changepwd', 'action.base.ChangePwd', #for web
    # Make url ending with or without '/' going to the same class
    '/(.*)/', 'action.base.redirect', 
)

if __name__ == '__main__':
    web.config.debug = False
    app = web.application(urls, globals())
    sessionstore = model.MemStore()  
    session = web.session.Session(app, sessionstore,initializer={'login': 0,'ulogin':0})
    def session_hook():
        web.ctx.session = session
    app.add_processor(web.loadhook(session_hook))
    web.config.session_parameters['timeout'] = 86400*2  #24 * 60 * 60, # 24 hours   in seconds 2days
    web.config.session_parameters['ignore_expiry'] = False
    app.run()
