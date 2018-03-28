#!/usr/bin/env python3
#coding=utf-8
#
import subprocess
import os,time,random
import urllib.request, urllib.parse, urllib.error,urllib.request,urllib.error,urllib.parse
import hashlib
import markdown
from markdown.extensions.wikilinks import WikiLinkExtension
import pickle

from math import *

print('importing utils...')

def getpage(url):
    print(url)
    req = urllib.request.Request(url)
    req.add_header("User-Agent","Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0")
    u = urllib.request.urlopen(req).read()
    return u

def savepage(content,filename):
    print('saving content...:%s'%(filename))
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
    if(type(content) is str):
        f.write(content.encode())
    else:
        f.write(content)
    f.flush()
    f.close()

def createDirs(path):
    path= path.strip()
    isExists=os.path.exists(path)
    if not isExists:
        print('%s create success!'%(path))
        # 创建目录操作函数
        os.makedirs(path)
        return True
    else:
        print('%s already exist'%(path))
        return False

def run(command):
    if not command:
        raise Exception("command is invalid")
    else:
        p = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        out, err = p.communicate()
        return out

def createSymbol(path1, path2):
    if os.path.exists(path2):
        os.remove(path2)
    os.symlink(path1, path2)

def sha1(value):
    return hashlib.sha1(value.encode()).hexdigest()

def md5(value):
    return hashlib.md5(value.encode()).hexdigest()

def sha256(value):
    return hashlib.sha256(value.encode()).hexdigest()

def GetFileMd5(filename):
    '''get same value as md5sum'''
    if not os.path.isfile(filename):
        return
    myhash = hashlib.md5()
    f = open(filename,'rb')
    while True:
        b = f.read(8096)
        if not b : break
        myhash.update(b)
    f.close()
    return myhash.hexdigest()

def saveObj(obj,filename):#dump对象到本地
    output = open(filename, 'wb+')
    pickle.dump(obj,output)
    output.close()

def loadObjsIfExist(filename):#启动的时候载入持久化的对象
    result= None
    if os.path.exists(filename):
        pkl_file = open(filename, 'rb')
        result = pickle.load(pkl_file)
        pkl_file.close()
    return result 

def timestamp():
    '''
    The timestamp of integer.
    '''
    return int(time.time())
   
## trans time like 1333316413.0 into '20120402'    
def strtimefold(time_var):
    return time.strftime("%Y-%m-%d",time.localtime(float(time_var)))

## trans time like 1333316413.0 into '2012-04-02 05:40:13'    
def strtime(time_var):
    return time.strftime("%Y-%m-%d %H:%M:%S ",time.localtime(float(time_var)))

## trans time like '2012-04-02 05:40:13' into 1333316413.0
def inttime(time_str):
    t = time.mktime(time.strptime('2012-04-02 05:40:13',"%Y-%m-%d %H:%M:%S"))
    return t

def check_username_valid(username):
    '''
    Checking if the username if valid.

    >>> check_username_valid('/sadf')
    False
    >>> check_username_valid('\s.adf')
    False
    >>> check_username_valid('')
    False
    >>> check_username_valid(' ')
    False
    '''
    if re.match('^[a-zA-Z][a-zA-Z0-9_]{3,19}', username) != None:
        return True
    return False


def check_email_valid(email_str):
    '''
    Checking if the given Email is valid.

    >>> check_email_valid('')
    False
    >>> check_email_valid('s.adf')
    False
    >>> check_email_valid('sadfsdfa@comaldfsdaf.cosdafj')
    False
    '''
    if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
                email_str) != None:
        return True
    return False

def markdown2html(markdown_text):
    '''
    Convert markdown text to HTML. with extensions.
    :param markdown_text:   The markdown text.
    :return:  The HTML text.
    '''
    html = markdown.markdown(
        markdown_text,
        output_format="html5",
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.toc',
            'markdown.extensions.codehilite',
            'markdown.extensions.meta'
        ]
    )
    return html

# input Lat_A 纬度A  
# input Lng_A 经度A  
# input Lat_B 纬度B  
# input Lng_B 经度B  
# output distance 距离(km)  
def getGeoDistance(Lat_A, Lng_A, Lat_B, Lng_B):  
    ra = 6378.140  # 赤道半径 (km)  
    rb = 6356.755  # 极半径 (km)  
    flatten = (ra - rb) / ra  # 地球扁率  
    rad_lat_A = radians(Lat_A)  
    rad_lng_A = radians(Lng_A)  
    rad_lat_B = radians(Lat_B)  
    rad_lng_B = radians(Lng_B)  
    pA = atan(rb / ra * tan(rad_lat_A))  
    pB = atan(rb / ra * tan(rad_lat_B))  
    xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))  
    c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2  
    c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2  
    dr = flatten / 8 * (c1 - c2)  
    distance = ra * (xx + dr)  
    return distance

print('utils import ok!' )
