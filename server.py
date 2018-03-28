#!/usr/bin/env python3
#coding=utf-8
# web.py In Memery of Aaron Swartz
# 2017.12.10: Switched into Tornado

import tornado.escape
from tornado import gen
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

import model,config
import action
import action.cms
import action.admin
import action.api

import os,sys

### Url mappings
handlers = [
    ##for web view
    ('/',                action.cms.Index),
    ('/allroms/([A-Za-z0-9_\-\.]*?)',   action.cms.Allroms), #/allroms/[devicename]
    ('/api',             action.api.API), #for client API
    ('/api/v1/build/get_delta',  action.api.API_DELTA), #for delta client API
    ('/api/report',              action.api.API_USER_REPORT), #for delta client API
    ('/api/(upgrade)/([A-Za-z0-9_\-\.]*?)/([A-Za-z0-9_\-\.]*?)',action.api.API_APPUP), #获取产品升级信息
    (config.ADMIN_LOGIN,         action.admin.Login), #for web
    ('/publish',                 action.admin.PublishIndex),# for web 
    ('/publish/device',          action.admin.PublishNewApp), #for web 发布新的应用
    ('/publish/romslist/([A-Za-z0-9_\-\.]*?)',    action.admin.PublishRomList), #for web
    ('/publish/rom/([A-Za-z0-9_\-\.]*?)', action.admin.PublishNewVersion), #for web 发布更新版本
    ('/publish/settings',      action.admin.Settings),
    ('/publish/userreport',      action.admin.UserReport), #for web 
    ('/publish/users',      action.admin.PublishNewUser), #for web 
    ('/publish/audit',      action.admin.Audit), #for web 
    ('/publish/quit',            action.admin.Quit), #for web
    ('/404',                   action.cms.ErrorPage), 
    # Make url ending with or without '/' going to the same class
    (r'/(.*)/',                   action.cms.redirect), 
]

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            #see: RequestHandler.get_template_path()
            #template_path=os.path.join(os.path.dirname(__file__), config.DEFAULT_FRONT_THEME),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            cookie_secret=config.COOKIE_SECRET,
            login_url="/404",#no need to show any login url.
            default_handler_class=action.cms.ErrorPage,
            debug=False,
            static_hash_cache=False,
        )
        super(Application, self).__init__(handlers, **settings)
       
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    if len(sys.argv)==2:
        http_server.listen(sys.argv[1])
    elif len(sys.argv)>=3:
        http_server.listen(sys.argv[2],address=sys.argv[1])
    else:
        print("To run this server: \npython server.py 8080 \npython server.py 127.0.0.1 8080")
        exit()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
