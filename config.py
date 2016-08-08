#!/usr/bin/env python
#coding=utf-8
import hashlib

netpref ={}
#web 服务端API 和管理入口的地址 
netpref['SERVER_HOST']='127.0.0.1'
netpref['SERVER_PORT']='80'

#登陆后台设置
ADMIN_LOGIN="/yourloginhere"
ADMIN_USERNAME="youradminname"
ADMIN_PWD="youradminpwd"
ADMIN_HASHPWD=hashlib.sha256(ADMIN_PWD).hexdigest()

#自动发布设置
#put your secret here.
AUTOPUB_SECRET="a9da4e7e26722c6bfb1c3742c18aabe679ce24aa67e7bcdea38fff5ebf6df0b2"

#SQLITE数据库文件名设置
DB_PATH_MAIN='databases/dbmain.db'
DB_PATH_PUBLISH='databases/db_publish.db'
