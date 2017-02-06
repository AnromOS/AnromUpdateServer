#!/usr/bin/env python
#coding=utf-8
import hashlib,os

netpref ={}
#web 服务端API 和管理入口的地址 
netpref['SERVER_HOST']='127.0.0.1'
netpref['SERVER_PORT']='8080'
netpref['SCHEME']='http'

#登陆后台设置
ADMIN_LOGIN="/yourloginpath"
ADMIN_USERNAME="youradminname"
ADMIN_PWD="youradminpwd"
ADMIN_HASHPWD=hashlib.sha256(ADMIN_PWD).hexdigest()

#自动发布设置
#put your secret here.
AUTOPUB_SECRET="a9da4e7e26722c6bfb1c3742c18aabe679ce24aa67e7bcdea38fff5ebf6df0b2"

#SQLITE数据库文件名设置
DB_PATH_MAIN='databases/dbmain.db'
DB_PATH_PUBLISH='databases/db_publish.db'

ROOT_PATH=os.getcwd()+'/'

netpref['ADMIN_LOGIN']=ADMIN_LOGIN
netpref['AUTOPUB_SECRET']=AUTOPUB_SECRET

sDics={
"nightly":"测试版",
"release":"发布版",
0:"强制升级未开启",
1:"开启强制升级",
2:"其他",
}
def getStatuStr(SKey):
    return sDics[SKey]
