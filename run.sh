#!/bin/sh
basepath=$(cd `dirname $0`; pwd)
cd $basepath
command='nohup python '${basepath}'/server.py 10240 >logs 2>&1 &'
echo $command
$command &
#su username -c ${command}
exit 0
