#!/bin/sh
cd /path/to/cmUpdaterServer/
su user -c 'nohup python /path/to/cmUpdaterServer/server.py 127.0.0.1:10240 >logs 2>&1 &'
exit 0
