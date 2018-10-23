#!/usr/bin/env python3
#coding=utf-8
## 安装和初始化网站的数据库

import sys,model,json,utils

def dumpVersion2Json(modname,  wid):
    _info = model.get_rom_by_wid(wid)
    result ={}
    if(_info):
        _vid = _info['version']
        _dumpfilename = 'static/downloads/'+modname+'/uinfo_'+ _vid +'.json'
        result = json.dumps(_info,ensure_ascii=False)
        utils.saveBin(_dumpfilename,result)
        print('Dumping products..:',wid, _dumpfilename)
    return result  

def upgrade_dump_json_all():
    _alldev = model.get_devices()
    for dev in _alldev:
        _modname = dev['m_device']
        _detail = model.get_roms_by_devicesname(_modname,-1)
        if _detail:
            for post in _detail:
                dumpVersion2Json(_modname, post['id'])

def main():
    print('''useage: \n ----"install.py install" to initiate the databases \r\n ----"install.py upgrade" to upgrade the databases \r\nAfter that, run "python server.py 18080" to start web server \r\n 
        ''')
    if len(sys.argv)>1:
        if (sys.argv[1] == "install"):
            model.installmain()
            exit()
        elif (sys.argv[1] == "upgrade"):
            upgrade_dump_json_all()
            exit()

if __name__ =='__main__':
    main()
