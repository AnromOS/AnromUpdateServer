#!/usr/bin/env python
#coding=utf-8
# web.py In Memery of Aaron Swartz

import web
import model,config,utils
import hashlib,json,time,base64,urllib2
import re
import os

class base:
    def __init__(self):
        auther="tweety"
        self.session = web.ctx.session

    ### Templates
    t_globals = {
        'datestr': web.datestr,
        'strdate':utils.strtime,
        'inttime':utils.inttime,
        'urlquote':utils.urllib2.quote,
        'abs2rev':utils.abs2rev
    }
    renderAdmin = web.template.render('templates/theme_bootstrap', base='base', globals=t_globals)
    renderCMS = web.template.render('templates/theme_bootstrap', base='base_index', globals=t_globals)
    renderDefault = web.template.render('templates/theme_bootstrap')

    def logged(self):
        if web.ctx.session.login==1:
            return True
        else:
            return False

    def countPrivilege(self):
        '''根据预置的秘密计算一个时间相关的随机数，每分钟变一次，用来发布ROM的时候做验证。'''
        secret = config.AUTOPUB_SECRET
        salt = time.strftime("%Y-%m-%d %H:00",time.localtime(time.time()))
        ptoken = hashlib.sha256(secret+salt).hexdigest()
        print("hasPrivilege: ptoken is:",ptoken)
        return ptoken
        
    def hasPrivilege(self,ptoken):
        token = self.countPrivilege()
        print "hasPrivilege: token is:",token ," ptoken is:",ptoken
        return token == ptoken
    
    def seeother(path):
        return web.seeother(config.netpref['SCHEME']+"://"+netpref['SERVER_HOST']+":"+netpref['SERVER_PORT']+path)
