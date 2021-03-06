# UpServer
## Brief:
This project is an implementation of CMS(Content Management System) for Application upgrade.

## 准备工作：

__本程序仅支持Linux系统__

__由于全面使用了python3 因此，需要先安装python3的环境__

__如果没有python3 的pip工具，则需要首先安装python3-pip__

1. 安装pip3：sudo apt install python3-pip
2. 安装redis： sudo apt install redis-server
3. 安装[tornadoweb](https://github.com/tornadoweb/tornado)框架 sudo pip3 install tornado
4. 安装python redis驱动: sudo pip3 install redis
5. 安装markdown: sudo pip3 install markdown

## 如何使用：

1. 在config.py中必须设置:
    - 文件下载服务器的域名和端口
    - 自动发布的API key:AUTOPUB_SECRET
    - 默认管理员用户名、密码
    - 数据库的地址端口
    - COOKIE_SECRET
2. 安装服务器:

```
$python install.py install
```

3. 启动服务器:

```
$python server.py 8080
```

或者

```
$run.sh
```

4. 确保服务器文件系统的写权限:网站目录的/static/images 和/static/downloads/ 需要有写权限
5. 部署nginx:
修改nginx中的配置文件，填写root dir的路径为程序的绝对路径，然后部署到nginx中即可，详情见下面

## 旧版本如何升级：

 1. 停止正在运行的服务
 2. 运行:
```
$python install.py upgrade
```
 3. 重新开始服务
```
$run.sh
```

## nginx服务器的配置：

1. 服务器配置使用nginx的反向代理功能，把web管理后台和API服务器连接起来。
2. 静态文件直接使用nginx配置文件目录作负载均衡。这样做是因为将静态文件独立负载，而动态内容通过网站程序运行。

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
