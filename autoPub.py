#!/usr/bin/python
#coding=utf-8
#auther:tweety 2016-5-23
#自动发布应用信息到web上的接口，此接口在管理员的客户端使用
import os,urllib,urllib2,re
import sched,time,socket
import threading 
import hashlib
import sys

def countPrivilege():
    '''根据预置的秘密计算一个时间相关的随机数，每分钟变一次，用来发布ROM的时候做验证。使用的时候必须修改这里'''
    secret = "a9da4e7e26722c6bfb1c3742c18aabe679ce24aa67e7bcdea38fff5ebf6df0b2"
    salt = time.strftime("%Y-%m-%d %H:00",time.localtime(time.time()))
    ptoken = hashlib.sha256(secret+salt).hexdigest()
    print("hasPrivilege: ptoken is:",ptoken)
    return ptoken
    
def postrom(dest,channels,version, versioncode, changelog, url, size, md5sum):
    print(url)
    data = {
          'a' : 'add',
          't' : 'full',
          'api_level' : 23,
          'channels' : channels, #nightly表示测试版，release表示发布版本
          'ptoken' : '', #计算出来的token，若计算出错则无法发送
          'version' : version, #版本
          'versioncode': versioncode, #版本号整数
          'changelog' : changelog, #变动日志
          'url' : url, #下载地址
          'size': size, #文件大小 单位字节
          'md5sum':md5sum
        }
    data['ptoken']=countPrivilege()
    print(data)
    # setup socket connection timeout
    timeout = 15
    socket.setdefaulttimeout(timeout)
    req = urllib.urlopen(dest, urllib.urlencode(data))
    html = req.read()
    print(html)
   
if __name__ == '__main__': 
    if(len(sys.argv)<=1):
        print "please use full parameter."
        exit()
    dest = sys.argv[1]
    channels = sys.argv[2]
    version = sys.argv[3]
    versioncode = sys.argv[4]
    changelog = sys.argv[5]
    url = sys.argv[6]
    size = sys.argv[7]
    md5sum = sys.argv[8]
    postrom(dest,channels,version, versioncode,changelog,url, size, md5sum)
