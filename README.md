# AnromUpdateServer
## Brief:
This project is an implementation of CMupdater,
written with python, need support of webpy framework.

## 如何使用：
1. 在config.py中设置文件下载服务器的域名和端口， 自动发布的API key 管理员用户名、密码
2. 安装服务器:

```
$python install.py
```

3. 启动服务器:

```
$python server.py 10240
```

或者

```
$run.sh
```

4. 确保服务器文件系统的写权限:网站目录的/static/images 和/static/downloads/ 需要有写权限
5. 部署nginx:
修改nginx中的配置文件，填写root dir的路径为程序的绝对路径，然后部署到nginx中即可，详情见下面

## nginx服务器的配置：

1. 服务器配置使用nginx的反向代理功能，把web管理后台和API服务器连接起来。
2. 静态文件直接使用nginx配置文件目录作负载均衡，不用转给webpy搭建的web服务器。这样做是因为webpy性能较弱，并且不支持断点续传，不适合作为文件下载服务器。

以下是 Nginx 的一种可用配置:


```
upstream backend{
	ip_hash;
	server 127.0.0.1:10240;
	server 127.0.0.1:10241;
	server 127.0.0.1:10242;
	server 127.0.0.1:10243;
}
server {
	listen 80 default_server;
	listen [::]:80 default_server ipv6only=on;
	root /path/to/AnromUpdateServer;
	# Make site accessible from http://localhost/
	server_name localhost;
	charset utf-8;
	access_log  /var/log/nginx/anromupdate.access.log;
	location / {
	    proxy_pass http://backend;
	    proxy_set_header Host $host;
	    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	}
	location /static {
	    root /path/to/cmUpdaterServer;
	    autoindex on;
	    autoindex_exact_size off;
	    autoindex_localtime on;
	    charset utf-8;
	    if (-f $request_filename) {
		    rewrite ^/static/(.*)$  /static/$1 break;
	    }
	}
}
```

===================================================================================================
##设置开机自动启动的方法[可选]：
1. 编辑run.sh 以及cmupdater
2. 将cmupdater 拷贝到 /etc/init.d/下
3. 执行 #update-rc.d cmupdater defaults 99

====================================================================================================

##附录I： 为rom作增量升级包
1. 制作差分包，使用android自己带的工具../build/tools/releasetools/ota_from_target_files

* 在执行上述命令时会出现未找到recovery_api_version的错误。原因是在执行上面的脚本时如果使用选项i则会调用WriteIncrementalOTAPackage会从A包和B包中的META目录下搜索misc_info.txt来读取recovery_api_version的值。但是在执行make  otapackage命令时生成的update.zip包中没有这个目录更没有这个文档。
* 此时我们就需要使用执行make otapackage生成的原始的zip包。这个包的位置在out/target/product/xxx/obj/PACKAGING/target_files_intermediates/ 目录下，它是在用命令make otapackage之后的中间生产物，是最原始的升级包。我们将两次编译的生成的包分别重命名为A.zip和B.zip，并拷贝到源码根目录下重复执行上面的命令：
* 例如  $ ./build/tools/releasetools/ota_from_target_files -i A.zip B.zip update-1416912639-1416913926.zip。强烈建议把升级包的文件名写成如下格式 update-{Incremental1}-{Incremental2}.zip 例如 update-1416912639-1416913926.zip
* 编译完成增量升级包后，OTA升级包、原始ZIP包和生成的update包 不要删除，请手动移动到某个文件夹妥善保存。

2. mtk的recovery的命令大致和cm recovery的差不多，recovery开机自动执行的命令格式定义在 /bootable/recovery/recovery.cpp 里面。(验证通过)
3. 用于升级的apk项目叫CMUpdater，该app需要root权限向手机目录下写入数据 (已经解决)
4. MTK自带的升级软件在这个地方 mediatek/packages/apps/AdupsFotaApp 没有源代码(已经去掉)

=====================================================================================================

##附录II： ROM的发布和文件上传

* 不管是OTA升级包还是差分升级包，均上传至服务器的/path/to/AnromUpdateServer/static/download/{device}/ 下面
* 上传完成文件之后，计算升级文件的md5值，然后在web端填写升级信息的表单。
* Incremental 字段其实就是一个时间戳，这个时间戳在编译的时候生成，编译好的升级文件名中已经包含，找到这个值，然后在表单中填写即可。
* Incremental字段是客户端判断是否需要下载增量升级包的关键，所以增量升级包一定要和发布的版本中间衔接好。

