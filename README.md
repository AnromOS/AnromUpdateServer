# UpServer
## Brief:
This project is an implementation of CMS(Content Management System) for Application upgrade.

## 准备工作：

1. 安装redis： sudo apt install redis-server
2. 安装[tornadoweb](https://github.com/tornadoweb/tornado)框架  pip install tornado
3. 安装python redis驱动: pip install redis

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
$python server.py
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
