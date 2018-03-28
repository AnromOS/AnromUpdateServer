#!/usr/bin/env python3
#coding=utf-8
import hashlib,os

netpref ={}
#web 服务端API 和管理入口的地址 
netpref['SERVER_HOST']='127.0.0.1'
netpref['SERVER_PORT']='8080'
netpref['SCHEME']='http'

#redis
netpref['REDIS_HOST']='127.0.0.1'
netpref['REDIS_PORT']=6379
netpref['REDIS_DB']=0
netpref['REDIS_PASSWORD']=None

#登陆后台设置
ADMIN_LOGIN="/yourloginpath"
ADMIN_USERNAME="youradminname"
ADMIN_PWD="youradminpwd"
ADMIN_HASHPWD=hashlib.sha256(ADMIN_PWD.encode()).hexdigest()

DEFAULT_HEAD="/static/images/default_head.png"
DEFAULT_APPCAPTION="/static/images/appdefault.png"

#自动发布设置
#put your secret here.
AUTOPUB_SECRET="a9da4e7e26722c6bfb1c3742c18aabe679ce24aa67e7bcdea38fff5ebf6df0b2"

##给cookie设置，用于验证加密cookie，发布时必须修改！
COOKIE_SECRET="bc4c516d9ab23c22c65ea2483aae5ba34c907f46f6d8dae11ece24004f486330"
##设置cookie的超时时间，默认半个小时。
COOKIE_EXPIRE=1800

##前台主题设置
DEFAULT_FRONT_THEME="templates/theme_default"

#ROOT path
ROOT_PATH=os.getcwd()+'/'

netpref['ADMIN_LOGIN']=ADMIN_LOGIN
netpref['AUTOPUB_SECRET']=AUTOPUB_SECRET
netpref['CHANNELS']="[nightly][release]"

sDics={
"[nightly]":"测试版",
"[release]":"发布版",
"[nightly][release]":"测试版、发布版",
"nightly":"测试版",
"release":"发布版",
"0":"强制升级未开启",
"1":"开启强制升级",
"2":"其他",
"admin":"管理员",
"developer":"开发者"
}
def getStatuStr(SKey):
    return sDics.get(SKey,SKey)
