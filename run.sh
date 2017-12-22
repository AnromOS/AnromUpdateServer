#!/bin/sh
basepath=$(cd `dirname $0`; pwd)
cd $basepath
worker1='nohup python '${basepath}'/server.py 127.0.0.1 10240 >logs 2>&1 &'
worker2='nohup python '${basepath}'/server.py 127.0.0.1 10241 >logs 2>&1 &'
worker3='nohup python '${basepath}'/server.py 127.0.0.1 10242 >logs 2>&1 &'
worker4='nohup python '${basepath}'/server.py 127.0.0.1 10243 >logs 2>&1 &'
echo $worker1
echo $worker2
echo $worker3
echo $worker4
$worker1 &
$worker2 &
$worker3 &
$worker4 &
exit 0

