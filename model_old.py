#!/usr/bin/env python
#coding=utf-8
import web,time,datetime,sqlite3,hashlib
import config,utils
import model

#dbmain: 网站的数据和设置信息
#dba 发布的rom保存的位置
DB_PATH_MAIN='databases/dbmain.db'
DB_PATH_PUBLISH='databases/db_publish.db'
dbmain = web.database(dbn='sqlite', db=DB_PATH_MAIN)
dba = web.database(dbn='sqlite', db=DB_PATH_PUBLISH)

#### for Client API
def get_devices_byname(device):
    '''获取所有的应用'''
    return dba.query('SELECT * FROM t_model where m_device = $device;', vars=locals())

def get_devices_counts_byname(mod_id):
    '''已经发布了多少个版本'''
    return dba.query("select count(*) FROM t_anrom where mod_id = $mod_id", vars=locals())[0]['count(*)']
    
def get_available_roms_by_modelid(modelid,channels):
    '''返回可用的升级'''
    chann = '%%'+channels+'%%'
    result= dba.select('t_anrom',where ='mod_id = $modelid AND channels like $chann ',limit = 1, order='issuetime desc', vars=locals())
    return result
    
def get_changelog_bydevice(mdevice,romid):
    '''返回机型的changelog'''
    result = dba.query('select changelog FROM t_anrom ,t_model where t_anrom.id = $romid AND t_anrom.mod_id = t_model.mod_id AND t_model.m_device = $mdevice;', vars=locals())
    return result
    
def get_available_delta_rom(dev_id,source_inc,target_inc):
    '''查找可用的增量升级包 target_inc 暂时没用'''
    source_inc = '%%'+source_inc.split('.')[-1]+'%%'
    result= dba.query('select * from t_anrom where mod_id = $dev_id AND source_incremental like $source_inc AND status = 2  order by m_time desc limit 1', vars=locals())
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
    if (dba.update("t_model", where="m_device=$mdevice", vars=locals(),m_device=mdevice,m_modname=mmod, m_modpicture=mpic, m_moddescription=mdescpt)):
        pass
    else:
        dba.insert("t_model",m_device=mdevice,m_modname=mmod, m_modpicture=mpic, m_moddescription=mdescpt, m_time=mtime)

def del_device(deviceid,mdevice):
    '''删除某个机型'''
    dba.delete("t_model", where="m_device=$mdevice",vars=locals()) 
    dba.delete("t_anrom", where="mod_id = $deviceid",vars=locals())#删除升级包

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
    except IndexError:
        return None

### database scheme.
DB_VERSION=1
def installmain():
    '''安装网站所需要的主数据库'''
    conn = sqlite3.connect(DB_PATH_MAIN)
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
        insert into pref (key,value) values("db_version","%d");
        insert into oplog (mlevel,mcontent) values("INFO", "创建管理员");
        insert into ureport (fingerprint,mcontent,mtime) values("test_finger_print","测试的用户提交数据","1015891406");
        """%(ADMIN_USERNAME,ADMIN_HASHPWD,DB_VERSION)
        c.executescript(installsql)
    finally:
        c.close()
        print 'install ',DB_PATH_MAIN,'  ok'

def installdics():
    '''安装发布版本的数据库'''
    conn = sqlite3.connect(DB_PATH_PUBLISH)
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
          source_incremental TEXT NOT NULL default '0',
          target_incremental TEXT NOT NULL default '0',
          extra TEXT NOT NULL default '',
          api_level TEXT NOT NULL default '0',
          issue_uname TEXT NOT NULL default '',
          issuetime INTEGER NOT NULL default 0,
          m_time INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS index_anrom ON t_anrom(id, mod_id);

        DROP TABLE IF EXISTS t_model;
        CREATE TABLE IF NOT EXISTS t_model (
          mod_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
          m_device TEXT NOT NULL,
          m_modname TEXT NOT NULL,
          m_modpicture TEXT NOT NULL,
          m_moddescription TEXT,
          issue_uname TEXT NOT NULL default '',
          m_time INTEGER NOT NULL DEFAULT 0
        );
        CREATE INDEX IF NOT EXISTS index_model ON t_model(mod_id,m_device);

        """
        
        c.executescript(installsql)
    finally:
        c.close()
        print 'install ', DB_PATH_PUBLISH,' ok'

def upgradeDB():
    #1 migrate t_model
    devices = get_devices()
    for devi in devices:
        mod_id=devi['mod_id']
        mdevice=devi['m_device']
        mmod=devi['m_modname']
        mpic=devi['m_modpicture']
        mdescpt=devi['m_moddescription']
        mtime=devi['m_time']
        model.save_device(mdevice, mmod ,mpic, mdescpt ,mtime, config.ADMIN_USERNAME)
        #2 migrate t_anrom
        products=get_all_roms_by_modelid(mod_id)
        for pd in products:
            wid= 10000+pd['id']
            version=pd['version']
            versioncode=pd['versioncode']
            changelog=pd['changelog']
            filename=pd['filename']
            url=pd['url']
            md5sum=pd['md5sum']
            size=pd['size']
            status=pd['status']
            channels=pd['channels']
            source_incremental=pd['source_incremental']
            target_incremental=pd['target_incremental']
            extra=pd['extra']
            api_level=pd['api_level']
            issuetime=pd['issuetime']
            m_time=pd['m_time']
            model.save_rom_new(wid, mdevice, version,versioncode, changelog, filename, url, size, md5sum, status, channels, source_incremental, target_incremental, extra, api_level, config.ADMIN_USERNAME, issuetime, m_time)
    
    print DB_PATH_PUBLISH,' db upgrade ok'
