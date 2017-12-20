#!/usr/bin/env python
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

import os

### Url mappings
handlers = [
    ##for web view
    (r'/',                action.cms.Index),
    (r'/allroms/([A-Za-z0-9_\-\.]*?)',   action.cms.Allroms), #/allroms/[devicename]
    (r'/api',             action.api.API), #for client API
    (r'/api/v1/build/get_delta',  action.api.API_DELTA), #for delta client API
    (r'/api/report',              action.api.API_USER_REPORT), #for delta client API
    (r'/api/(upgrade)/([A-Za-z0-9_\-\.]*?)/([A-Za-z0-9_\-\.]*?)',action.api.API_APPUP), #获取产品升级信息
    (config.ADMIN_LOGIN,         action.admin.Login), #for web
    (r'/publish',                 action.admin.PublishIndex),# for web 
    (r'/publish/device',          action.admin.PublishNewApp), #for web 发布新的应用
    (r'/publish/romslist/([A-Za-z0-9_\-\.]*?)',    action.admin.PublishRomList), #for web
    (r'/publish/rom/([A-Za-z0-9_\-\.]*?)', action.admin.PublishNewVersion), #for web 发布更新版本
    (r'/publish/userreport',      action.admin.UserReport), #for web 
    (r'/publish/users',      action.admin.UserReport), #for web 
    (r'/publish/quit',            action.admin.Quit), #for web
    (r'/publish/changepwd',       action.admin.ChangePwd), #for web
    (r'/404',                   action.cms.ErrorPage), 
    # Make url ending with or without '/' going to the same class
    (r'/(.*)/',                   action.cms.redirect), 
]
define("port", default=8080, help="run on the given port", type=int)
class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates/theme_bootstrap"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            ui_modules={"Entry": EntryModule},
            xsrf_cookies=True,
            cookie_secret="bc4c516d9ab23c22c65ea2483aae5ba34c907f46f6d8dae11ece24004f486330",
            login_url="/404",#no need to show any login url.
            default_handler_class=action.cms.ErrorPage,
            debug=False,
        )
        super(Application, self).__init__(handlers, **settings)

class EntryModule(tornado.web.UIModule):
    def render(self, entry):
        return self.render_string("modules/entry.html", entry=entry)
       
def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
