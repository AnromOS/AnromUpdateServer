#!/bin/bash
#这是一个使用自动发布接口的例子
basepath=$(cd `dirname $0`; pwd)
cd $basepath
REMOTEHOST=127.0.0.1
REMOTEPORT=80
REMOTEDIR=/path/to/upload/dir
POSTCMD=/path/to/autoPost.py

publish(){
    #publish to web platform
    DEST=$1
    CHANNELS=$2
    CHANGELOG=$3
    URL=$4
    MD5SUM=$5
    python $POSTCMD "$DEST" "$CHANNELS" "$CHANGELOG" "$URL" "$MD5SUM"
}

builduserdebug(){
    #$1 : product
    PRODUCT=$1
    echo "now upload to $REMOTEHOST......"
    scp $ROMDIR/$ROMFILE.zip $SSHUSER@$REMOTEHOST:$REMOTEDIR/$PRODUCT/
    echo "upload $ROMFILE.zip to $REMOTEHOST finished."    
    echo "now publish to web...."
    #通过API的标示
    MODID=999999
    CHANNELS=nightly
    CHANGELOG="[ENG]nightly build for $ROMFILE"
    MD5SUM=$(md5sum $ROMDIR/$ROMFILE.zip)
    publish "http://$REMOTEHOST:$REMOTEPORT/publish/rom/$MODID/$PRODUCT" "$CHANNELS" "$CHANGELOG" "http://$DLHOST:$REMOTEPORT/static/downloads/$PRODUCT/$ROMFILE.zip" $MD5SUM
    echo "publish to web finished."
}
