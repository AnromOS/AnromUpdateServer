#!/usr/bin/env python
#coding=utf-8
import time,datetime,hashlib,sqlite3,json
import redis
import config

#dbmain: 网站的数据和设置信息
#dba 发布的rom保存的位置
redis_db = redis.StrictRedis(host=config.netpref['REDIS_HOST'], port=config.netpref['REDIS_PORT'], db=config.netpref['REDIS_DB'], password=config.netpref['REDIS_PASSWORD'])

#### for Client API
def get_devices_byname(device):
    '''获取所有的应用'''
    return dba.query('SELECT * FROM t_model where m_device = $device;', vars=locals())

def get_devices_counts_byname(mod_id):
    '''已经发布了多少个版本'''
    return redis_db.zcard("upserver:tmodel_index")
    
def get_available_roms_by_modelid(modelid,channels):
    '''返回可用的升级'''
    chann = '%%'+channels+'%%'
    result= dba.select('t_anrom',where ='mod_id = $modelid AND channels like $chann ',limit = 1, order='issuetime desc', vars=locals())
    return result
    
def get_changelog_bydevice(mdevice,romid):
    '''返回机型的changelog'''
    result = dba.query('select changelog FROM t_anrom ,t_model where t_anrom.id = $romid AND t_anrom.mod_id = t_model.mod_id AND t_model.m_device = $mdevice;', vars=locals())
    return result

def post_user_report(fprint, fcontent,ftime):
    '''提交用户反馈'''
    result = redis_db.rpush("upserver:ureport",json.dumps({"fingerprint":fprint,"mcontent":fcontent, "mtime":ftime}))
    return result
    
## for web admin
def get_preferences():
    '''获取网站的所有配置字段'''
    return redis_db.hgetall("upserver:pref")
    
def login_post(username,password):
    '''验证网站管理员登录'''
    usr = get_pref("user")
    pwd = get_pref("password")
    print(username)
    print(hashlib.sha256(password).hexdigest())
    return (username == usr)and (pwd ==  hashlib.sha256(password).hexdigest())

def post_changeuser(username,password):
    '''更改管理员密码'''
    save_pref("user",username)
    save_pref("password",hashlib.sha256(password).hexdigest())
  
#### 发布机型管理  
def get_devices():
    '''获取所有的机型'''
    result=[]
    pnames = redis_db.zrange("upserver:tmodel_index",0,-1)
    for pn in pnames:
        rd = redis_db.hgetall("upserver:tmodel:%s"%pn)
        result.append(rd)
    return result
    
def save_device(mdevice, mmod ,mpic, mdescpt ,mtime, muser):
    '''保存某个机型的配置'''
    redis_db.hset("upserver:tmodel",mdevice,json.dumps({"m_device":mdevice,"m_modname":mmod, "m_modpicture":mpic, "m_moddescription":mdescpt, "m_time":mtime,"m_issue_uname":muser}))

def del_device(deviceid,mdevice):
    '''删除某个机型'''
    redis_db.hdel("upserver:tmodel",mdevice)
    redis_db.hdel("upserver:tanrom",mdevice)
    #dba.delete("t_model", where="m_device=$mdevice",vars=locals()) 
    #dba.delete("t_anrom", where="mod_id = $deviceid",vars=locals())#删除升级包

### 发布升级包
def get_all_roms_by_modelid(modelid):
    '''获取某个机型id对应的rom'''
    result= dba.select('t_anrom',where ='mod_id = $modelid', order='issuetime desc', vars=locals())
    return result
    
def get_top5_roms_by_modelid(modelid):
    '''获取某个机型id对应的rom,只显示前5个'''
    result= redis_db.zrange("upserver:tmodel:testProduct.items",-1,-5)
    return result
    
def get_rom_by_wid(wid):
    '''获取单个升级包的信息'''
    result= dba.select('t_anrom',where ='id = $wid', limit= 1, vars=locals())[0]
    return result
    
def save_rom_new(wid, mod_id, version,versioncode, changelog, filename, url, size, md5sum, status, channels, source_incremental, target_incremental, extra, api_level, issuetime, m_time):
    '''发布新的rom升级包'''
    res = dba.update("t_anrom",where="id = $wid",vars=locals(), mod_id = mod_id, version = version,  versioncode= versioncode, changelog = changelog, filename=filename, url=url,size = size, md5sum = md5sum, status = status, channels = channels,source_incremental = source_incremental, target_incremental = target_incremental, extra= extra, api_level = api_level,m_time=m_time)
    if(res):
        pass
    else:
        dba.insert("t_anrom",mod_id = mod_id, version =version ,versioncode=versioncode, changelog = changelog, filename=filename, url=url,size = size, md5sum = md5sum, status = status, channels = channels, source_incremental = source_incremental, target_incremental = target_incremental, extra= extra, api_level = api_level,issuetime=issuetime,m_time=m_time)
    #升级设备最近更新的时间
    dba.update("t_model", where="mod_id=$mod_id", vars=locals(),m_time=m_time)
        
def delete_rom_by_id(wid):
    '''删除某个rom升级包'''
    return dba.delete("t_anrom", where="id = $wid",vars=locals()) 

def find_modid_bydevice(mdevice):
    '''根据设备名称查找设备ID'''
    return dba.select('t_model', where="m_device=$mdevice" ,limit='1' ,vars=locals())
   
#### 用户反馈的web管理
def get_user_report_counts():
    '''总共有多少条反馈'''
    return redis_db.llen("upserver:ureport")

def get_user_report(pg, pagesize):
    '''查看用户反馈'''
    p = pagesize*(pg)
    return redis_db.lrange("upserver:ureport",p,p+pagesize)
    
def del_user_report(pid):
    '''查看用户反馈'''
    return redis_db.ltrim("upserver:ureport",0,-1)
     
### preference
pref_cache ={}
def save_pref(name,content):
    redis_db.hset("upserver:pref",name,content)
    pref_cache[name]=content

def get_pref(name):
    try:
        if name in pref_cache.keys():
            return pref_cache[name]
        value = redis_db.hget("upserver:pref",name)
        pref_cache[name] = value
        return value
    except KeyError:
        return None
    except IndexError:
        return None

### database scheme.
DB_VERSION=1
def installmain():
    '''安装网站所需要的主数据库'''
    redis_db.hset("upserver:pref","user",config.ADMIN_USERNAME)
    redis_db.hset("upserver:pref","password",config.ADMIN_HASHPWD)
    redis_db.hset("upserver:pref","db_version",DB_VERSION)
    ##测试用户
    redis_db.hset("upserver:users",config.ADMIN_USERNAME,json.dumps({"u_name":config.ADMIN_USERNAME,"u_password":config.ADMIN_HASHPWD,"u_avatar":config.DEFAULT_HEAD,"u_description":"超级管理员","u_time":"1115891406"}))
    ##测试用户提交数据
    redis_db.rpush("upserver:ureport",{"fingerprint":"test_finger_print","mcontent":"测试的用户提交数据", "mtime":"1015891406"})
    ##测试添加产品线
    pName= "testProduct"
    mod_id=redis_db.incr("upserver:latest:mod_id")
    redis_db.zadd("upserver:tmodel_index",mod_id,pName)
    hindex="upserver:tmodel:%s"%pName
    mdetail={
    "mod_id":mod_id,
    "m_device":pName,
    "m_modname":"测试产品",
    "m_modpicture":"static/images/appdefault.png",
    "m_moddescription":"这是用来测试的产品数据",
    "m_issue_uname":config.ADMIN_USERNAME,
    "m_time":1115891406
    }
    redis_db.hmset(hindex,mdetail)
    ##测试添加条目
    itmid=redis_db.incr("upserver:latest:itm")
    anindex="upserver:tanrom:%s"%itmid
    redis_db.zadd(hindex+".items",itmid,anindex)
    mdetail={
    'id':itmid,
    'mod_id':'testProduct',
    'version':'1.0.1',
    'versioncode':'1001',
    'changelog':'1,改变了世界 2,拯救了未来',
    'filename':'test.deb',
    'url':'http://example.com/test.deb',
    'md5sum':'63d475e6b67ebcb959224a1587f28214',
    'size':1024,
    'status':0,
    'channels':'nightly',
    'source_incremental':'0',
    'target_incremental':'0',
    'extra':'',
    'api_level':'0',
    'issue_uname':config.ADMIN_USERNAME,
    'issuetime':0,
    'm_time':0
    }
    redis_db.hmset(anindex,mdetail)
    print('save main info into redis ok')

def upgradeDB():
    print(config.DB_PATH_PUBLISH,' db upgrade ok')
        

class WebCache:
    '''缓存web页面的类，减少数据库访问，用来提高访问不太经常改变的内容的速度'''
    mcache = {}
    cleartime =int(time.time())
    def get(self,keyword):
        now = int(time.time())
        if ((now - self.cleartime)>(24*3600)):
            self.mcache.clear()#clear the cache every 24 hours
            self.cleartime= int(time.time())
        return self.mcache.get(keyword)
        
    def put(self,keyword,content):
        self.mcache[keyword]=content
