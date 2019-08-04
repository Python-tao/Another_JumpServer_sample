import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

import base64
import getpass
import os
import socket
import sys
import traceback
from paramiko.py3compat import input
from  models import models
import datetime

import paramiko
try:
    import interactive
except ImportError:
    from . import interactive


def ssh_login(user_obj,bind_host_obj,mysql_engine,log_recording):
    # now, connect and use paramiko Client to negotiate SSH2 across the connection
    try:
        client = paramiko.SSHClient()
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.WarningPolicy())
        print('*** Connecting...')
        #client.connect(hostname, port, username, password)
        #连接远程机器。
        client.connect(bind_host_obj.host.ip,#远程主机的ip
                       bind_host_obj.host.port, #远程主机的端口
                       bind_host_obj.remote_user.username,#远程主机的远程用户
                       bind_host_obj.remote_user.password,#远程主机的远程用户密码
                       timeout=30)
        #命令缓存队列
        cmd_caches = []
        #创建通道。
        chan = client.invoke_shell()
        print(repr(client.get_transport()))
        #连接上了远程主机
        print('*** Here we go!\n')
        #往命令缓存队列中，记录一条日志。
        cmd_caches.append(models.AuditLog(user_id=user_obj.id,  #堡垒机用户的id
                                          bind_host_id=bind_host_obj.id,    #远程主机
                                          action_type='login',  #动作类型登入，也可以写登出。
                                          cmd=u"登入远程主机。",
                                          date=datetime.datetime.now()  #日期
                                          ))
        #把命令缓存写入数据库。
        #缺点是，如果断开或者重启，命令缓存的数据就丢失了。
        log_recording(user_obj,bind_host_obj,cmd_caches)

        #调用interactive进行处理。
        interactive.interactive_shell(chan,user_obj,bind_host_obj,cmd_caches,log_recording)
        chan.close()
        client.close()

    except Exception as e:
        print('*** Caught exception: %s: %s' % (e.__class__, e))
        traceback.print_exc()
        try:
            client.close()
        except:
            pass
        sys.exit(1)