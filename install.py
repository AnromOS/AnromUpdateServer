#!/usr/bin/env python
#coding=utf-8
## 安装和初始化网站的数据库

import sys,model

def main():
    print '''useage: \n ----"install.py install" to initiate the databases \r\n ----"install.py upgrade" to upgrade the databases \r\nAfter that, run "python server.py 18080" to start web server \r\n 
        '''
    if len(sys.argv)>1:
        if (sys.argv[1] == "install"):
            model.installmain()
            exit()
        elif (sys.argv[1] == "upgrade"):
            model.upgradeDB()
            exit()

if __name__ =='__main__':
    main()
