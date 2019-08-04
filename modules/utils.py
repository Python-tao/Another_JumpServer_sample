import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from conf import settings

import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


#自建的错误命令提示语。
def print_err(msg,quit=False):
    output = "\033[31;1mError: %s\033[0m" % msg
    if quit:
        exit(output)
    else:
        print(output)


#yaml配置文件解析引擎。
def yaml_parser(yml_filename):
    '''
    load yaml file and return
    :param yml_filename:
    :return:
    '''
    abs_filename = "%s/%s.yml" % (settings.StateFileBaseDir,yml_filename)
    try:
        yaml_file = open(abs_filename,'r',encoding='utf-8')
        data = yaml.load(yaml_file,Loader=yaml.FullLoader)
        return data
    except Exception as e:
        print_err(e)

#
# filename="%s/%s.yml" % (settings.StateFileBaseDir,'new_hosts')
# yaml_file = open(filename,'r')
# data = yaml.load(yaml_file,Loader=yaml.FullLoader)
# for key,val in data.items():
#     print(key,val)