#!/usr/bin/python
#coding=utf-8
## 安装和初始化网站的数据库

import sys,model

def main():
    if len(sys.argv)>=1:
        print '''useage: run "install.py install" to initiate the databases \r\n After that, run "python server.py 18080" to start web server \r\n 
        '''
        model.installmain()
        model.installdics()
        exit()

if __name__ =='__main__':
    main()
