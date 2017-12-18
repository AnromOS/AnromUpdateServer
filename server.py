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
    '/allroms/([A-Za-z0-9_\-\.]*?)',   'action.cms.Allroms', #/allroms/[devicename]
    '/api',             'action.api.API', #for client API
    '/api/v1/build/get_delta',  'action.api.API_DELTA', #for delta client API
    '/api/report',              'action.api.API_USER_REPORT', #for delta client API
    '/api/(upgrade)/([A-Za-z0-9_\-\.]*?)/([A-Za-z0-9_\-\.]*?)',              'action.api.API_APPUP', #获取产品升级信息
    config.ADMIN_LOGIN,         'action.admin.Login', #for web
    '/publish',                 'action.admin.PublishIndex',# for web 
    '/publish/device',          'action.admin.PublishNewApp', #for web 发布新的应用
    '/publish/romslist/([A-Za-z0-9_\-\.]*?)',    'action.admin.PublishRomList', #for web
    '/publish/rom/([A-Za-z0-9_\-\.]*?)', 'action.admin.PublishNewVersion', #for web 发布更新版本
    '/publish/userreport',      'action.admin.UserReport', #for web 
    '/publish/users',      'action.admin.UserReport', #for web 
    '/publish/quit',            'action.admin.Quit', #for web
    '/publish/changepwd',       'action.admin.ChangePwd', #for web
    # Make url ending with or without '/' going to the same class
    '/(.*)/',                   'action.cms.redirect', 
)

class MemStore(web.session.Store):
    '''##自定义session store 类，将session信息保存在内存中，提高读写速度'''
    def __init__(self):
        self.shelf = {}

    def __contains__(self, key):
        return key in self.shelf.keys()

    def __getitem__(self, key):
        v = self.shelf[key]
        return self.decode(v)

    def __setitem__(self, key, value):
        self.shelf[key] = self.encode(value)
        
    def __delitem__(self, key):
        try:
            del self.shelf[key]
        except KeyError:
            pass

    def cleanup(self, timeout):
        self.shelf.clear()
        
def notfound(errno=404):
    r_index= "Windows IIS 5.0: "+str(errno)
    return  web.notfound(r_index)

if __name__ == '__main__':
    web.config.debug = False
    app = web.application(urls, globals())
    app.notfound = notfound
    sessionstore = MemStore()  
    session = web.session.Session(app, sessionstore,initializer={'login': 0,'uname':""})
    def session_hook():
        web.ctx.session = session
    app.add_processor(web.loadhook(session_hook))
    web.config.session_parameters['timeout'] = 86400*2  #24 * 60 * 60, # 24 hours   in seconds 2days
    web.config.session_parameters['ignore_expiry'] = False
    app.run()
