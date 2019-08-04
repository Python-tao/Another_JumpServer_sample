# 主题：堡垒机的演示。
version2
堡垒机的需求：
    基于paramiko的ssh服务所修改的堡垒机试验演示。
    所有人包括运维、开发等任何需要访问业务系统的人员，只能通过堡垒机访问业务系统。
    通过堡垒机访问业务系统的所有操作记录都会记录到日志系统中。
    回收所有对业务系统的访问权限，做到除了堡垒机管理人员，没有人知道业务系统任何机器的登录密码.
    网络上限制所有人员只能通过堡垒机的跳转才能访问业务系统。
    确保除了堡垒机管理员之外，所有其它人对堡垒机本身无任何操作权限，只有一个登录跳转功能。
    确保用户的操作纪录不能被用户自己以任何方式获取到并篡改。
    

#具体实现的堡垒机功能
## syncdb命令(已完成)
```
　　作用：初始化数据库。

```


## create_users命令(已完成)
```
    作用:
        创建堡垒机用户数据。

```

## create_groups命令(已完成)
```
    作用:
        创建主机组数据。

```

## create_hosts命令(已完成)
```
    作用:
        创建后端主机数据。

```
## create_bindhosts命令(已完成)
```
    作用:
        创建bindhosts表数据。

```
## create_remoteusers命令(已完成)
```
    作用:
        创建远程用户表数据。

```
## start_session命令(已完成)
```
    作用:
        堡垒机用户连接远程主机的入口命令。

```





# 使用的模块
```
    sqlalchemy，  与数据库连接的模块。
    paramiko，    进行ssh连接的模块。
    pyyaml，    解析yaml文件。
    
```


# 数据库表结构
```
-基本表
    host，           后端主机表。
    host_group，    主机组表
    remote_user，    远程用户表
    bind_host，      后端主机与远程用户的对应表。
    user_profile，    堡垒机用户表
    audit_log，        日志信息表
-多对多关系表
    user_m2m_bindhost，  堡垒机用户与bind_host表的关系表。
    bindhost_m2m_hostgroup， 主机组与bind_host表的关系表。
    userprofile_m2m_hostgroup，  堡垒机用户ind_host表的关系表。
    
```





# 目录结构
```
- bin 
    -run_it.py          程序启动入口
- conf
    -settinggs.py           全局配置文件，保存了sqlite数据库的连接方式，以及数据文件的路径。
    
-db                         数据库目录
    -database.db            sqlite3数据库文件
-models
    -models.py              使用sqlalchemy创建数据库表格的基础引擎。
-modules                    核心模块
    -actions.py             解析用户输入的命令行内容的模块.
    -db_conn.py             使用sqlalchemy创建数据库交互会话的模块
    -interactive.py         调用paramiko与远程主机进行具体交互的模块
    -ssh_login.py           调用paramiko与远程主机进行ssh连接的模块
    -utils.py               放置各个模块通用的函数。
    -views.py               放置堡垒机的主要功能函数的模块。
-share                      共享目录
    -examples               放置数据库初始化数据的目录
        -new_bindhosts.yml  放置数据库初始化数据的yaml格式的文件。
    
```