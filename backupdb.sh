#!/bin/sh
basepath=$(cd `dirname $0`; pwd)
cd $basepath
zip -r ./databases.$(date +%Y%m%d).zip /path/to/UpServer/databases
