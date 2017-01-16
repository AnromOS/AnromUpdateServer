#!/bin/bash
#这是一个使用自动发布接口的例子
basepath=$(cd `dirname $0`; pwd)
cd $basepath
REMOTEHOST="192.168.2.*"
REMOTEPORT=8080
PEMOTESCHEME="http"
REMOTEDIR=/path/to/upload/dir
POSTCMD=./autoPub.py

publish(){
    #publish to web platform
    DEST=$1
    CHANNELS=$2
    VERSION=$3
    VERSIONCODE=$4
    CHANGELOG=$5
    URL=$6
    SIZE=$7
    MD5SUM=$8
    python $POSTCMD "$DEST" "$CHANNELS" "$VERSION" "$VERSIONCODE" "$CHANGELOG" "$URL" "$SIZE" "$MD5SUM"
}

builduserdebug(){
    #$1 : product
    FILENAME=$1
    ROMFILE=$2
    PRODUCTID=$3
    echo "now upload to $REMOTEHOST......"
    #使用scp命令将文件上传到服务器。[可选项]
    #scp $ROMDIR/$ROMFILE $SSHUSER@$REMOTEHOST:$REMOTEDIR/$PRODUCTID/
    echo "upload $ROMFILE to $REMOTEHOST finished."    
    echo "now publish to web...."
    #通过API的标示
    MODID=999999
    DEST=$PEMOTESCHEME://$REMOTEHOST:$REMOTEPORT/publish/rom/$MODID/$PRODUCTID
    URL=$PEMOTESCHEME://$REMOTEHOST:$REMOTEPORT/static/downloads/$PRODUCTID/$FILENAME
    CHANNELS="nightly"
    VERSION="0.0.1"
    VERSIONCODE="444"
    CHANGELOG="[ENG]nightly build for $FILENAME"
    MD5SUM=$(md5sum $ROMFILE)
    SIZE=263433
    publish "$DEST" "$CHANNELS" "$VERSION" "$VERSIONCODE" "$CHANGELOG" "$URL" "$SIZE" $MD5SUM
    echo "publish to web finished."
}

builduserdebug "Anet.png" ~/temp/Anet.png "atomic_win_32"
