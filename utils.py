#!/usr/bin/python
#coding=utf-8
#
import os,cPickle,time
import urllib,urllib2
import hashlib

print 'importing utils...'

def getpage(url):
    print url
    req = urllib2.Request(url)
    req.add_header("User-Agent","Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0")
    req.add_header("If-None-Match","c1858c2845ca9501136ca83d624f8d4d")
    u = urllib2.urlopen(req).read()
    return u

def savepage(content,filename):
    print 'saving content...:',filename
    f = file(filename,"wb+")
    u = content.decode('gb18030')
    ue= u.encode('utf-8')
    f.write(ue)
    f.close()
    return ue

def abs2rev(absurl):
    #print absurl
    purl = re.compile('''http://.*?/(.*?)$''')
    r = purl.findall(absurl)
    for x in r:
       #print 'find next: ',x
       return "/"+x

def saveBin(filename, content):
    f = open(filename,mode="wb+")
    f.write(content)
    f.flush()
    f.close()

def createDirs(path):
    path= path.strip()
    isExists=os.path.exists(path)
    if not isExists:
        print path+' create success!'
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        print path+'already exist'
        return False

def GetFileMd5(filename):
    '''get same value as md5sum'''
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = file(filename,'rb')
    while True:
        b = f.read(8096)
        if not b : break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def saveObj(obj,filename):#dump对象到本地
    output = open(filename, 'wb+')
    cPickle.dump(obj,output)
    output.close()

def loadObjsIfExist(filename):#启动的时候载入持久化的对象
    result= None
    if os.path.exists(filename):
        pkl_file = open(filename, 'rb')
        result = cPickle.load(pkl_file)
        pkl_file.close()
    return result 
    
## trans time like 1333316413.0 into '20120402'    
def strtimefold(time_var):
    return time.strftime("%Y%m%d",time.localtime(time_var))

## trans time like 1333316413.0 into '2012-04-02 05:40:13'    
def strtime(time_var):
    return time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime(time_var))

## trans time like '2012-04-02 05:40:13' into 1333316413.0
def inttime(time_str):
    t = time.mktime(time.strptime('2012-04-02 05:40:13',"%Y-%m-%d %H:%M:%S"))
    return t
print 'utils import ok!'    
