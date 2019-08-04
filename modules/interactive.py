# Copyright (C) 2003-2007  Robey Pointer <robeypointer@gmail.com>
#
# This file is part of paramiko.
#
# Paramiko is free software; you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# Paramiko is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Paramiko; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA.


import socket
import sys
from paramiko.py3compat import u
from  models import models
import datetime

# windows does not have termios...
try:
    import termios
    import tty
    has_termios = True
except ImportError:
    has_termios = False


def interactive_shell(chan,user_obj,bind_host_obj,cmd_caches,log_recording):
    if has_termios:
        posix_shell(chan,user_obj,bind_host_obj,cmd_caches,log_recording)
    else:
        windows_shell(chan)

#linux的shell
def posix_shell(chan,user_obj,bind_host_obj,cmd_caches,log_recording):
    '''

    :param chan: 通道
    :param user_obj: 堡垒机用户对象
    :param bind_host_obj: 后端主机对象
    :param cmd_caches:  命令缓存列表
    :param log_recording:   日志记录模块。
    :return:
    '''
    import select
    
    oldtty = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        tty.setcbreak(sys.stdin.fileno())
        chan.settimeout(0.0)
        cmd = ''
        #标记tab键的标识符。
        tab_key = False
        while True:
            r, w, e = select.select([chan, sys.stdin], [], [])
            if chan in r:#socket中有数据进入。
                try:
                    x = u(chan.recv(1024))
                    if tab_key:#用户按下了tab键。
                        if x not in ('\x07' , '\r\n'):
                            #print('tab:',x)
                            cmd += x#把远程主机补全的命令也加到命令字符串中。
                        tab_key = False#把标志位设置位false。
                    if len(x) == 0:#断开了
                        sys.stdout.write('\r\n*** EOF\r\n')
                        break
                    sys.stdout.write(x)
                    sys.stdout.flush()
                except socket.timeout:
                    pass
            if sys.stdin in r:#按下键盘
                x = sys.stdin.read(1)
                if '\r' != x:#如果不是换行键，就加入命令变量中。
                    cmd +=x
                else:#是换行键，说明输入了一条命令。

                    print('cmd->:',cmd)#打印此行命令。
                    #生成数据库对象。
                    log_item = models.AuditLog(user_id=user_obj.id,
                                          bind_host_id=bind_host_obj.id,
                                          action_type='cmd',
                                          cmd=cmd ,
                                          date=datetime.datetime.now()
                                          )
                    #加入到命令缓存列表中。
                    cmd_caches.append(log_item)
                    #把cmd字符串变量清空。
                    cmd = ''

                    if len(cmd_caches)>=10:#每满10个命令，就保存到数据库中。
                        log_recording(user_obj,bind_host_obj,cmd_caches)
                        cmd_caches = []
                if '\t' == x:#用户按下了tab键。
                    tab_key = True#标志设置为true.
                if len(x) == 0:#断开连接了。
                    break
                chan.send(x)#把输入的数据发送到远程主机。

    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, oldtty)

    
# windows的shell，不用。
def windows_shell(chan):
    import threading

    sys.stdout.write("Line-buffered terminal emulation. Press F6 or ^Z to send EOF.\r\n\r\n")
        
    def writeall(sock):
        while True:
            data = sock.recv(256)
            if not data:
                sys.stdout.write('\r\n*** EOF ***\r\n\r\n')
                sys.stdout.flush()
                break
            sys.stdout.write(data.decode())
            sys.stdout.flush()
        
    writer = threading.Thread(target=writeall, args=(chan,))
    writer.start()
        
    try:
        while True:
            d = sys.stdin.read(1)
            if not d:
                break
            chan.send(d)
    except EOFError:
        # user hit ^Z or F6
        pass
