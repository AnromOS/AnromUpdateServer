#!/usr/bin/env python3
#coding=utf-8
import time,datetime,hashlib,json,re
import redis
import config

#1.本应用所有的key以upserver:开头
#2.
redis_db = redis.StrictRedis(host=config.netpref['REDIS_HOST'], port=config.netpref['REDIS_PORT'], db=config.netpref['REDIS_DB'], password=config.netpref['REDIS_PASSWORD'],decode_responses=True)

chanPatten= re.compile('\[.*?\]')
  
#### 发布机型管理  
def get_devices():
    '''获取所有的机型'''
    result=[]
    pnames = redis_db.lrange("upserver:tmodel_index",0,-1)
    for pn in pnames:
        rd = redis_db.hgetall("upserver:tmodel:%s"%pn)
        result.append(rd)
    return result

def get_devices_counts_byname(mdevice):
    '''查看当前产品下已经发布了多少个版本'''
    return redis_db.llen("upserver:tmodel:%s.items"%mdevice)

def get_devices_byname(mdevice):
    '''获取某个机型相关的信息'''
    hindex="upserver:tmodel:%s"%mdevice
    result = redis_db.hgetall(hindex)
    return result
   
def save_device(mdevice, mmod ,mpic, mdescpt ,mtime, muser, mpubV4=1):
    '''保存某个机型的配置'''
    hindex="upserver:tmodel:%s"%mdevice
    print("saving new product:",mdevice,mmod)
    ## renew index
    redis_db.lrem("upserver:tmodel_index",1,mdevice)
    redis_db.lpush("upserver:tmodel_index",mdevice)
    ## save detail
    mdetail={
    "m_device":mdevice,
    "m_modname":mmod,
    "m_modpicture":mpic,
    "m_moddescription":mdescpt,
    "m_issue_uname":muser,
    "m_time":mtime,
    "m_pub_ipv4":mpubV4
    }
    redis_db.hmset(hindex,mdetail)
    ##DB changed, so we purge the global cache. 
    purge_Cache()
    return mdevice

def del_device(mdevice):
    '''删除某个机型'''
    hindex="upserver:tmodel:%s"%mdevice
    print("deleting product:",mdevice)
    redis_db.delete(hindex)
    redis_db.lrem("upserver:tmodel_index",1,mdevice)
    ##DB changed, so we purge the global cache. 
    purge_Cache()

### 发布升级条目管理
def get_roms_by_devicesname(mdevice,topcount):
    '''获取某个机型id对应的rom: topcount 为-1 则返回所有的rom'''
    result =[]
    itms = redis_db.lrange("upserver:tmodel:%s.items"%mdevice,0,topcount)
    for itmid in itms:
        anindex="upserver:tanrom:%s"%itmid
        r1 = redis_db.hgetall(anindex)
        result.append(r1)
    return result
    
def get_rom_by_wid(wid):
    '''获取单个升级包的信息'''
    anindex="upserver:tanrom:%s"%wid
    result= redis_db.hgetall(anindex)
    return result

def get_available_roms_by_modelid(mdevice,channels):
    '''返回当前设备下的1个可用的升级'''
    result = []
    lkey = "upserver:tmodel:%s.[%s]"%(mdevice,channels)
    itmid = redis_db.lindex(lkey,0)
    pupgrade = get_rom_by_wid(itmid)
    if(not pupgrade == {}):
        result.append(pupgrade)
    return result
   
def save_rom_new(wid, mdevice, version,versioncode, changelog, filename, url, size, md5sum, status, channels, source_incremental, target_incremental, extra, api_level, issue_uname, issuetime, m_time):
    '''发布新的rom升级包'''  
    itmid=wid
    anindex="upserver:tanrom:%s"%itmid
    if(not redis_db.exists(anindex)):
        itmid=redis_db.incr("upserver:latest:itm")
        anindex="upserver:tanrom:%s"%itmid
    print("saving new update:",mdevice,version, anindex)
    ##put item id into the index first 
    redis_db.lrem("upserver:tmodel:%s.items"%mdevice,1,itmid)
    redis_db.lpush("upserver:tmodel:%s.items"%mdevice,itmid)
    ## put item id in different channels
    chans = chanPatten.findall(config.netpref['CHANNELS'])
    for chan in chans:
        redis_db.lrem("upserver:tmodel:%s.%s"%(mdevice,chan),1,itmid)
    chans = chanPatten.findall(channels)
    for chan in chans:
        redis_db.lpush("upserver:tmodel:%s.%s"%(mdevice,chan),itmid)
    ##save data into redis
    mdetail={
    'id':itmid,
    'mdevice':mdevice,
    'version':version,
    'versioncode':versioncode,
    'changelog':changelog,
    'filename':filename,
    'url':url,
    'md5sum':md5sum,
    'size':size,
    'status':status,
    'channels':channels,
    'source_incremental':source_incremental,
    'target_incremental':target_incremental,
    'extra':extra,
    'api_level':api_level,
    'issue_uname':issue_uname,
    'issuetime':issuetime,
    'm_time':m_time
    }
    redis_db.hmset(anindex,mdetail)
    ##DB changed, so we purge the global cache. 
    purge_Cache()
    return itmid
        
def delete_rom_by_id(wid):
    '''删除某个rom升级包'''
    anindex="upserver:tanrom:%s"%wid
    itm = get_rom_by_wid(wid)
    mdevice = itm['mdevice']
    channels= itm['channels']
    print("deleting update:",mdevice,itm['version'])
    ##delete from index queue,
    redis_db.lrem("upserver:tmodel:%s.items"%mdevice,1,wid)
    ##delete from channel index
    chans = chanPatten.findall(config.netpref['CHANNELS'])
    for chan in chans:
        redis_db.lrem("upserver:tmodel:%s.%s"%(mdevice,chan),1,wid)
    ##DB changed, so we purge the global cache. 
    purge_Cache()
    ##delete from items
    return redis_db.delete(anindex)

#### 网站用户管理
def get_all_users():
    uinfos = redis_db.hgetall("upserver:users")
    result = {}
    for uname in uinfos.keys():
        result[uname]=json.loads(uinfos[uname])
    return result

def get_user_by_uname(uname):
    uinfo = redis_db.hget("upserver:users",uname)
    if uinfo:
        return json.loads(uinfo)
    else: return None

def add_new_user(uname, upasswd, urole, uavatar, udescription, utime):
    print("saving user:",uname)
    redis_db.hset("upserver:users",uname,json.dumps({"u_name":uname,"u_password":upasswd,"u_role":urole, "u_avatar":uavatar,"u_description":udescription,"u_time":utime}))
    ##DB changed, so we purge the global cache. 
    purge_Cache()

def del_user(uname):
    print("deleting user:",uname)
    redis_db.hdel("upserver:users",uname)
    ##DB changed, so we purge the global cache. 
    purge_Cache()

#### 用户反馈的web管理
def get_user_report_counts():
    '''总共有多少条反馈'''
    return redis_db.llen("upserver:ureport")

def post_user_report(fprint, fcontent,ftime):
    '''提交用户反馈'''
    result = redis_db.lpush("upserver:ureport",json.dumps({"fingerprint":fprint,"mcontent":fcontent, "mtime":ftime}))
    return result

def get_user_report(pg, pagesize):
    '''查看用户反馈'''
    p = pagesize*(pg)
    result = redis_db.lrange("upserver:ureport",p,p+pagesize)
    items=[]
    for itm in result:
        items.append(json.loads(itm))
    return items
    
def del_user_report():
    '''删除用户反馈'''
    ##DB changed, so we purge the global cache. 
    purge_Cache()
    return redis_db.delete("upserver:ureport")

#### 用户操作日志
def get_audit_log_counts():
    return redis_db.llen("upserver:audit")

def post_audit_log(ftag, fcontent,ftime):
    result = redis_db.lpush("upserver:audit",json.dumps({"ftag":ftag,"mcontent":fcontent, "mtime":ftime}))
    return result

def get_audit_log(pg, pagesize):
    p = pagesize*(pg)
    items_r = redis_db.lrange("upserver:audit",p,p+pagesize)
    items=[]
    for itm in items_r:
        items.append(json.loads(itm))
    return items
    
def del_audit_log():
    ##DB changed, so we purge the global cache. 
    purge_Cache()
    return redis_db.delete("upserver:audit")
    
### preference
pref_cache ={}
## for web admin
def get_preferences():
    '''获取网站的所有配置字段'''
    return redis_db.hgetall("upserver:pref")

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

###全局缓存
def get_Cache(cachename, result):
    pname = 'upserver:cache:'
    if(redis_db.hexists(pname,cachename)):
        return redis_db.hget(pname, cachename)
    else: return result

def set_Cache(cachename, cachevalue):
    pname = 'upserver:cache:'
    redis_db.hset(pname, cachename, cachevalue)

def purge_Cache():
    pname = 'upserver:cache:'
    redis_db.delete(pname)

### database scheme.
DB_VERSION=1
def installmain():
    '''安装网站所需要的主数据库'''
    redis_db.hset("upserver:pref","db_version",DB_VERSION)
    for k in config.netpref.keys():
        save_pref(k,config.netpref[k])
    ##添加一个管理员
    add_new_user(config.ADMIN_USERNAME,config.ADMIN_HASHPWD,"admin",config.DEFAULT_HEAD,"超级管理员","1515891406")
    ##测试用户提交数据
    post_user_report("test_finger_print","测试的用户提交数据", 1015891406)
    ##测试添加产品线
    pName = "testProduct"
    save_device(pName, "测试产品" ,config.DEFAULT_APPCAPTION, "这是用来测试的产品数据" ,1115891406, config.ADMIN_USERNAME)
    
    ##测试添加条目
    itmid = save_rom_new(0, pName, '1.0.1','1001', '1,改变了世界 2,拯救了未来3,这是条测试数据，修改或删除随便', 'test.deb', 'http://example.com/test.deb', 1024, '63d475e6b67ebcb959224a1587f28214', 0, '[nightly]', '0', '0', '', '0',config.ADMIN_USERNAME, 0, 0)
    print('save main info into redis ok')

def upgradeDB():
    print(config.DB_PATH_PUBLISH,' db upgrade ok')