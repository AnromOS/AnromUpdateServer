#!/usr/bin/env python
#coding=utf-8
import web,time,datetime,sqlite3,hashlib
import config

#dbmain: 网站的数据和设置信息
#dba 发布的rom保存的位置
dbmain = web.database(dbn='sqlite', db=config.DB_PATH_MAIN)
dba = web.database(dbn='sqlite', db=config.DB_PATH_PUBLISH)

#### for Client API
def get_devices_byname(device):
    '''获取所有的应用'''
    return dba.query('SELECT * FROM t_model where m_device = $device;', vars=locals())

def get_available_roms_by_modelid(modelid,channels):
    '''返回可用的升级'''
    result= dba.select('t_anrom',where ='mod_id = $modelid AND channels = $channels ',limit = 1, order='issuetime desc', vars=locals())
    return result
    
def get_changelog_bydevice(mdevice,romid):
    '''返回机型的changelog'''
    result = dba.query('select changelog FROM t_anrom ,t_model where t_anrom.id = $romid AND t_anrom.mod_id = t_model.mod_id AND t_model.m_device = $mdevice;', vars=locals())
    return result
    
def get_available_delta_rom(dev_id,source_inc,target_inc):
    '''查找可用的增量升级包 target_inc 暂时没用'''
    source_inc = '%%'+source_inc.split('.')[-1]+'%%'
    result= dba.query('select * from t_rom_delta where mod_id = $dev_id AND source_incremental like $source_inc AND status = 2  order by m_time desc limit 1', vars=locals())
    return result

def post_user_report(fprint, fcontent,ftime):
    '''提交用户反馈'''
    result = dbmain.insert("ureport",fingerprint= fprint, mcontent=fcontent, mtime = ftime)
    return result
    
## for web admin
def get_preferences():
    '''获取网站的所有配置字段'''
    return dbmain.select('pref', order='id DESC')
    
def login_post(username,password):
    '''验证网站管理员登录'''
    usr = get_pref("user")
    pwd = get_pref("password")
    print username
    print hashlib.sha256(password).hexdigest()
    return (username == usr)and (pwd ==  hashlib.sha256(password).hexdigest())

def post_changeuser(username,password):
    '''更改管理员密码'''
    save_pref("user",username)
    save_pref("password",hashlib.sha256(password).hexdigest())
  
#### 发布机型管理  
def get_devices():
    '''获取所有的机型'''
    return dba.select('t_model', vars=locals())
    
def save_device(mdevice, mmod ,mpic, mdescpt ,mtime):
    '''保存某个机型的配置'''
    if (dba.update("t_model", where="m_device=$mdevice", vars=locals(),m_device=mdevice,m_modname=mmod, m_modpicture=mpic, m_moddescription=mdescpt, m_time=mtime)):
        pass
    else:
        dba.insert("t_model",m_device=mdevice,m_modname=mmod, m_modpicture=mpic, m_moddescription=mdescpt, m_time=mtime)

def del_device(deviceid,mdevice):
    '''删除某个机型'''
    dba.delete("t_model", where="m_device=$mdevice",vars=locals()) 
    dba.delete("t_anrom", where="mod_id = $deviceid",vars=locals())#删除升级包
    dba.delete("t_rom_delta", where="mod_id = $deviceid",vars=locals())#删除增量升级包

### 发布升级包
def get_all_roms_by_modelid(modelid):
    '''获取某个机型id对应的rom'''
    result= dba.select('t_anrom',where ='mod_id = $modelid', order='issuetime desc', vars=locals())
    return result
    
def get_top5_roms_by_modelid(modelid):
    '''获取某个机型id对应的rom,只显示前5个'''
    result= dba.select('t_anrom',where ='mod_id = $modelid', order='issuetime desc', limit='5', vars=locals())
    return result
    
def get_rom_by_wid(wid):
    '''获取单个升级包的信息'''
    result= dba.select('t_anrom',where ='id = $wid', limit= 1, vars=locals())[0]
    return result
    
def save_rom_new(wid, mod_id, version,versioncode, changelog, filename, url, size, md5sum, status, channels, api_level, issuetime, m_time):
    '''发布新的rom升级包'''
    res = dba.update("t_anrom",where="id = $wid",vars=locals(), mod_id = mod_id, version = version,  versioncode= versioncode, changelog = changelog, filename=filename, url=url,size = size, md5sum = md5sum, status = status, channels = channels, api_level = api_level,m_time=m_time)
    if(res):return
    else:
        dba.insert("t_anrom",mod_id = mod_id, version =version ,versioncode=versioncode, changelog = changelog, filename=filename, url=url,size = size, md5sum = md5sum, status = status, channels = channels, api_level = api_level,issuetime=issuetime,m_time=m_time)
        
def delete_rom_by_id(wid):
    '''删除某个rom升级包'''
    return dba.delete("t_anrom", where="id = $wid",vars=locals()) 

def find_modid_bydevice(mdevice):
    '''根据设备名称查找设备ID'''
    return dba.select('t_model', where="m_device=$mdevice" ,limit='1' ,vars=locals())
    
#### 增量升级包
def get_romdelta_bymodid(modid):
    '''显示某个rom的增量升级包'''
    return dba.select("t_rom_delta",where="mod_id=$modid",order='target_incremental desc',vars=locals())

def get_romdelta_by_wid(wid):
    '''获取单个升级包的信息'''
    result= dba.select('t_rom_delta',where ='id = $wid', limit= 1, vars=locals())[0]
    return result
    
def save_romdelta_new(wid, mod_id, api_level, filename, url, md5sum, status, source_incremental, target_incremental,  m_time):
    '''发布新的增量rom升级包'''
    res =dba.update("t_rom_delta",where="id = $wid",vars=locals(),mod_id = mod_id, api_level = api_level, filename=filename, url=url, md5sum = md5sum, status = status, source_incremental = source_incremental, target_incremental = target_incremental,m_time=m_time)
    if (res):return 
    else:
        dba.insert("t_rom_delta",mod_id = mod_id, api_level = api_level, filename=filename, url=url, md5sum = md5sum, status = status, source_incremental = source_incremental, target_incremental = target_incremental, m_time=m_time)

def delete_romdelta_by_id(wid):
    '''删除某个rom增量升级包'''
    return dba.delete("t_rom_delta", where=" id = $wid",vars=locals())
    
#### 用户反馈的web管理
def get_user_report_counts():
    '''总共有多少条反馈'''
    return dbmain.query("select count(*) from ureport")[0]['count(*)']

def get_user_report(pg, pagesize):
    '''查看用户反馈'''
    p = pagesize*(pg)
    return dbmain.select("ureport",vars =locals(), limit = pagesize, offset=p, order="mtime desc")
    
def del_user_report(pid):
    '''查看用户反馈'''
    return dbmain.delete("ureport",where = "id=$pid",vars =locals())
     
### preference
pref_cache ={}
def save_pref(name,content):
    if (dbmain.update("pref", where="key=$name", vars=locals(),value = content)):
        pass
    else:
        dbmain.insert("pref",key= name,value = content)
    pref_cache[name]=content

def get_pref(name):
    try:
        if name in pref_cache.keys():
            return pref_cache[name]
        value = dbmain.select("pref",vars=locals(),where="key=$name")[0].value
        pref_cache[name] = value
        return value
    except KeyError:
        return None

def installmain():
    '''安装网站所需要的主数据库'''
    conn = sqlite3.connect(config.DB_PATH_MAIN)
    c= conn.cursor()
    try:
        installsql=""" 
        DROP TABLE IF EXISTS pref;
        CREATE TABLE pref (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            key TEXT NOT NULL unique,
            value TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS index_pref ON pref(key);
        
        DROP TABLE IF EXISTS ureport;
        CREATE TABLE ureport (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            fingerprint TEXT NOT NULL,
            mcontent TEXT NOT NULL,
            mtime INTEGER NOT NULL);
        CREATE INDEX IF NOT EXISTS index_ureport ON ureport(id, fingerprint);
        
        insert into pref (key,value) values("user","%s");
        insert into pref (key,value) values("password","%s");
        insert into ureport (fingerprint,mcontent,mtime) values("test_finger_print","测试的用户提交数据","1015891406");
        """%(config.ADMIN_USERNAME,config.ADMIN_HASHPWD)
        c.executescript(installsql)
    finally:
        c.close()
        print config.DB_PATH_MAIN,' install db ok'

def installdics():
    '''安装发布版本的数据库'''
    conn = sqlite3.connect(config.DB_PATH_PUBLISH)
    c= conn.cursor()
    try:
        installsql=""" 
        DROP TABLE IF EXISTS t_anrom;
        CREATE TABLE IF NOT EXISTS t_anrom (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          mod_id INTEGER NOT NULL,
          version text NOT NULL,
          versioncode text NOT NULL,
          changelog text NOT NULL,
          filename text NOT NULL,
          url text NOT NULL,
          md5sum text NOT NULL,
          size INTEGER NOT NULL default 0,
          status INTEGER NOT NULL default 0,
          channels TEXT NOT NULL default 'nightly',
          api_level TEXT NOT NULL default '0',
          issuetime INTEGER NOT NULL default 0,
          m_time INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS index_anrom ON t_anrom(id, mod_id);
        
        DROP TABLE IF EXISTS t_rom_delta;
        CREATE TABLE IF NOT EXISTS t_rom_delta (
          id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          mod_id INTEGER NOT NULL,
          api_level text NOT NULL,
          filename text NOT NULL,
          url text NOT NULL,
          md5sum text NOT NULL,
          status INTEGER NOT NULL default 0,
          source_incremental TEXT NOT NULL default '0',
          target_incremental TEXT NOT NULL default '0',
          m_time INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS index_rom_delta ON t_rom_delta(id, mod_id,source_incremental,target_incremental);
        
        DROP TABLE IF EXISTS t_model;
        CREATE TABLE IF NOT EXISTS t_model (
          mod_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          m_device TEXT NOT NULL,
          m_modname TEXT NOT NULL,
          m_modpicture TEXT NOT NULL,
          m_moddescription TEXT,
          m_time INTEGER NOT NULL DEFAULT '0'
        );
        CREATE INDEX IF NOT EXISTS index_model ON t_model(mod_id,m_device);
        """
        
        c.executescript(installsql)
    finally:
        c.close()
        print config.DB_PATH_PUBLISH,' install db ok'
        
        
class MemStore(web.session.Store):
    '''##自定义session store 类，将session信息保存在内存中，提高读写速度'''
    def __init__(self):
        self.shelf = {}

    def __contains__(self, key):
        return key in self.shelf.keys()

    def __getitem__(self, key):
        v = self.shelf[key]
        return self.decode(v)

    def __setitem__(self, key, value):
        self.shelf[key] = self.encode(value)
        
    def __delitem__(self, key):
        try:
            del self.shelf[key]
        except KeyError:
            pass

    def cleanup(self, timeout):
        self.shelf.clear()
        
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
