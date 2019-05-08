飞花令后台
=========


### 部署

部署分为三个阶段：

- 搭建环境
- 导入数据
- 运行应用

#### 搭建环境

搭建飞花令应用需要一台服务器，当然，你用自己电脑也是可以的。

1、搭建环境分为两步

1. 在宿主机上安装 mysql、redis、nginx，不知道如何安装的同学右转 google 搜索 `如何安装ＸＸ`。
2. 使用 docker 建立飞花令app镜像 

２、修改 ` .env.sample` 文件为 `.env ` 然后在其中按要求填写自己的 mysql、redis以及百度语音app的信息。

３、下载简体版本中文诗词，使用 `git clone https://github.com/Provinm/chinese-poetry-simplified.git`

#### 导入数据

环境搭建好之后，启动 docker 镜像，由于 docker 镜像 cmd 是启动 sanic 应用的命令，这一步只是导入数据，所以需要覆盖掉这一条命令

示例如下

```cmd

docker run -d -p 8000:8000 \
			  --name flyingflower \ 
			  -v yourpath/flyingflower_pubilc: /server \
			  -v yourpath/chinese-poetry-simplified: /var/data/poetry \
			  flyingflower:1.0.0 \
			  tail -f /server/requirements.txt 	  
```

需要注意：

1. 替换自己的路径到 `yourpath`
2. `tail -f /server/requirements.txt ` 既覆盖了原有 CMD ，又保证容器运行起来之后不退出

容器运行之后使用 `docker exec -it flyingflower bash`　进入容器中。


1、加载 .env 到环境变量，命令 `source .env`
2、进入 `server/preparation` 文件夹中


1. 运行 `python db_create.py ` 建立数据库表
2. 运行  `python db_import.py` 导入数据

第二步导入数据用时会非常长，因为整个诗词库有30万首诗词左右，然后我们需要逐首逐句逐字的导入到数据库。在我的1H1C服务器上足足跑了一下午才结束。

所以等程序跑起来之后就出门散散心，和朋友聚个会，然后再看个电影什么的，都来得及。

#### 运行应用

导入数据完成之后，结束掉之前导入数据的 container，运行命令

```

docker run -d -p 8000:8000 \
			  --name flyingflower \ 
			  -v yourpath/flyingflower_pubilc: /server \
			  flyingflower:1.0.0 \
```

这时候打开浏览器或者 wget 命令访问 `http://localhost:8000/ebrose/pivot?povit=花` 应该可以看到结果。

接下来为了搭起一个完整的应用，参考飞花令的[小程序代码]()，clone 下来，使用小程序开发工具打开，更改 app.json 中的 host，即可在手机上扫码体验啦。

