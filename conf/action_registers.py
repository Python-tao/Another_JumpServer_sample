
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from modules import views


#保存当前程序可用的命令。
#使用字典形式保存，
#key为命令名称，values为具体的函数。
actions = {
    'start_session': views.start_session,#堡垒机用户一旦登陆堡垒机，就运行这个。
    # 'stop': views.stop_server,
    'syncdb': views.syncdb,#数据库同步
    'create_users': views.create_users,#创建堡垒机用户
    'create_groups': views.create_groups,#创建主机组
    'create_hosts': views.create_hosts,#创建主机
    'create_bindhosts': views.create_bindhosts,#创建用户绑定主机对应表
    'create_remoteusers': views.create_remoteusers,#创建远程用户
    # 'audit':views.log_audit     #进入审计页面。

}