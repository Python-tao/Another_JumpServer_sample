import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from conf import action_registers
from modules import utils

def help_msg():
    '''
    print help msgs
    :return:
    '''
    print("\033[31;1mAvailable commands:\033[0m")
    for key in action_registers.actions:
        print("\t",key)

def excute_from_command_line(argvs):
    #如果位置参数少于2个，就打印帮助。
    if len(argvs) < 2:
        help_msg()
        exit()
        #如果位置参数中代表的命令，不在命令列表中，就报错。
    if argvs[1] not in action_registers.actions:
        utils.print_err("Command [%s] does not exist!" % argvs[1], quit=True)
    action_registers.actions[argvs[1]](argvs[1:])