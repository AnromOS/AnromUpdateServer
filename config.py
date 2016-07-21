#!/usr/bin/env python
#coding=utf-8
import hashlib

netpref ={}
#web 服务端API 和管理入口的地址 
netpref['SERVER_HOST']='127.0.0.1'
netpref['SERVER_PORT']='80'

ADMIN_LOGIN="/yourloginhere"
ADMIN_USERNAME="youradminname"
ADMIN_PWD="youradminpwd"
ADMIN_HASHPWD=hashlib.sha256(ADMIN_PWD).hexdigest()
