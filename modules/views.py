import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from models import models
from conf import settings
from modules.utils import print_err,yaml_parser
from modules.db_conn import engine,session
from modules import ssh_login

#初始化数据库
def syncdb(argvs):
    print("Syncing DB....")
    engine = models.create_engine(settings.ConnParams,
                          echo=True )
    models.Base.metadata.create_all(engine) #创建所有表结构
    print("数据库初始化成功。")


#创建后端主机数据
def create_hosts(argvs):
    '''
    create hosts
    :param argvs:用户输入的原始数据文件名
    :return:
    '''
    if '-f' in argvs:
        hosts_file  = argvs[argvs.index("-f") +1 ]
    else:
        print_err("invalid usage, should be:\ncreate_hosts -f <the new hosts file>",quit=True)
    #使用yaml引擎加载yaml文件，如果有数据，说明加载成功。
    source = yaml_parser(hosts_file)
    if source:
        print(source)
        #遍历字典。
        for key,val in source.items():
            print(key,val)
            obj = models.Host(hostname=key,ip=val.get('ip'), port=val.get('port') or 22)
            session.add(obj)
        session.commit()
        print("数据添加成功。")

#创建远程用户数据
def create_remoteusers(argvs):
    '''
    create remoteusers
    :param argvs:用户输入的yml文件名
    :return:
    '''
    if '-f' in argvs:
        remoteusers_file  = argvs[argvs.index("-f") +1 ]
    else:
        print_err("invalid usage, should be:\ncreate_remoteusers -f <the new remoteusers file>",quit=True)
    source = yaml_parser(remoteusers_file)
    if source:
        for key,val in source.items():
            print(key,val)
            obj = models.RemoteUser(username=val.get('username'),auth_type=val.get('auth_type'),password=val.get('password'))
            session.add(obj)
        session.commit()
        print("数据添加成功。")

#创建堡垒机用户数据。
def create_users(argvs):
    '''
    create little_finger access user
    :param argvs:
    :return:
    '''
    if '-f' in argvs:
        user_file  = argvs[argvs.index("-f") +1 ]
    else:
        print_err("invalid usage, should be:\ncreateusers -f <the new users file>",quit=True)

    source = yaml_parser(user_file)
    if source:
        for key,val in source.items():
            print(key,val)
            obj = models.UserProfile(username=key,password=val.get('password'))
        #     # if val.get('groups'):
        #     #     groups = session.query(models.Group).filter(models.Group.name.in_(val.get('groups'))).all()
        #     #     if not groups:
        #     #         print_err("none of [%s] exist in group table." % val.get('groups'),quit=True)
        #     #     obj.groups = groups
        #     # if val.get('bind_hosts'):
        #     #     bind_hosts = common_filters.bind_hosts_filter(val)
        #     #     obj.bind_hosts = bind_hosts
        #     #print(obj)
            session.add(obj)
        session.commit()
        print("数据添加成功。")


#创建主机组数据。
def create_groups(argvs):
    '''
    create groups
    :param argvs:
    :return:
    '''
    if '-f' in argvs:
        group_file  = argvs[argvs.index("-f") +1 ]
    else:
        print_err("invalid usage, should be:\ncreategroups -f <the new groups file>",quit=True)
    source = yaml_parser(group_file)
    if source:
        for key,val in source.items():
            print(key,val)
            obj = models.HostGroup(name=key)
        #     # if val.get('bind_hosts'):
        #     #     bind_hosts = common_filters.bind_hosts_filter(val)
        #     #     obj.bind_hosts = bind_hosts
        #     #
        #     # if val.get('user_profiles'):
        #     #     user_profiles = common_filters.user_profiles_filter(val)
        #     #     obj.user_profiles = user_profiles
            session.add(obj)
        session.commit()
        print("数据添加成功。")


#创建后端主机绑定远程用户的表的数据。
def create_bindhosts(argvs):
    '''
    create bind hosts
    :param argvs:
    :return:
    '''
    if '-f' in argvs:
        bindhosts_file  = argvs[argvs.index("-f") +1 ]
    else:
        print_err("invalid usage, should be:\ncreate_hosts -f <the new bindhosts file>",quit=True)
    source = yaml_parser(bindhosts_file)

    if source:
        for key,val in source.items():
            #取出后端主机对象。
            host_obj = session.query(models.Host).filter(models.Host.hostname==val.get('hostname')).first()
            assert host_obj

            for item in val['remote_users']:
                # print(item )
                assert item.get('auth_type')
                #判断远程用户的认证方式。
                if item.get('auth_type') == 'ssh-password':
                    #从远程用户表中取出对应的远程用户对象。
                    remoteuser_obj = session.query(models.RemoteUser).filter(
                                                        models.RemoteUser.username==item.get('username'),
                                                        models.RemoteUser.password==item.get('password')
                                                    ).first()

                else:
                    #取出用key认证的远程用户对象。
                    remoteuser_obj = session.query(models.RemoteUser).filter(
                                                        models.RemoteUser.username==item.get('username'),
                                                        models.RemoteUser.auth_type==item.get('auth_type'),
                                                    ).first()
                #如果取不到远程用户对象，就退出。
                if not remoteuser_obj:
                    print_err("RemoteUser obj %s does not exist." % item,quit=True )
                #生成一个Binghost表对象，准备写入数据到BingHost表中。把主机id，和远程用户id写入。
                bindhost_obj = models.BindHost(host_id=host_obj.id,remoteuser_id=remoteuser_obj.id)
                #添加到会话中。
                session.add(bindhost_obj)
                #查找是否有groups字段，如果有就取出该字段在HostGroup表中的对象。

                if source[key].get('groups'):
                    #取出主机组对象
                    group_objs = session.query(models.HostGroup).filter(models.HostGroup.name.in_(source[key].get('groups') )).all()
                    assert group_objs
                    print('groups:', group_objs)
                    #写入数据到多对多表中(bind_host表对host_group表)
                    bindhost_obj.host_groups = group_objs
        #         #查找是否有user_profiles字段。如果有就说明关联了堡垒机用户。
                if source[key].get('user_profiles'):
                    #取出堡垒机用户对象。
                    userprofile_objs = session.query(models.UserProfile).filter(models.UserProfile.username.in_(
                        source[key].get('user_profiles')
                    )).all()
                    assert userprofile_objs
                    print("userprofiles:",userprofile_objs)
                    # 写入数据到多对多表中(bind_host表对user_profiles表)
                    bindhost_obj.user_profiles = userprofile_objs
        #         #print(bindhost_obj)
        session.commit()
        print("数据创建成功。")


#认证。
def auth():
    '''
    do the user login authentication
    :return:
    '''
    count = 0
    while count <3:
        username = input("\033[32;1mUsername:\033[0m").strip()
        if len(username) ==0:continue
        password = input("\033[32;1mPassword:\033[0m").strip()
        if len(password) ==0:continue
        user_obj = session.query(models.UserProfile).filter(models.UserProfile.username==username,
                                                            models.UserProfile.password==password).first()
        if user_obj:
            return user_obj
        else:
            print("wrong username or password, you have %s more chances." %(3-count-1))
            count +=1
    else:
        print_err("too many attempts.")
#欢迎提示语。
def welcome_msg(user):
    WELCOME_MSG = '''\033[32;1m
    ------------- Welcome [%s] login JumpServer -------------
    \033[0m'''%  user.username
    print(WELCOME_MSG)


#记录日志。
def log_recording(user_obj,bind_host_obj,logs):
    '''
    flush user operations on remote host into DB
    :param user_obj:
    :param bind_host_obj:
    :param logs: list format [logItem1,logItem2,...]
    :return:
    '''
    print("\033[41;1m--logs:\033[0m",logs)
    #接收一个logs 对象，然后写入数据库。
    session.add_all(logs)
    session.commit()



#会话。
def start_session(argvs):
    print('going to start sesssion ')
    #执行认证模块
    user = auth()
    if user:#认证通过。
        #欢迎。
        welcome_msg(user)
        #user.bind_hosts该用户绑定的主机
        #ser.host_groups该用户绑定的主机组。
        # print(user.bind_hosts)
        # print(user.host_groups)
        exit_flag = False#只要不退出，就进入死循环。
        while not exit_flag:
            #如果用户与主机关联了。
            if user.bind_hosts:
                #打印未分组的机器，有多少台。
                print('\033[32;1mz.\tungroupped hosts (%s)\033[0m' %len(user.bind_hosts) )
            for index,group in enumerate(user.host_groups):
                #打印有几个主机组，主机组下的主机列表。
                print('\033[32;1m%s.\t%s (%s)\033[0m' %(index,group.name,  len(group.bind_hosts)) )
            #提示用户输入。
            choice = input("[%s]:" % user.username).strip()
            if len(choice) == 0:continue
            if choice == 'z':#查看主机列表。
                print("------ Group: ungroupped hosts ------" )
                for index,bind_host in enumerate(user.bind_hosts):
                    print("  %s.\t%s@%s(%s)"%(index,    #下标
                                              bind_host.remote_user.username,   #远程用户名称
                                              bind_host.host.hostname,      #主机名称
                                              bind_host.host.ip,              #主机IP
                                              ))
                print("----------- END -----------" )
            elif choice == 'exit':
                exit("Bye!")
            elif choice.isdigit():  #如果输入了数字，说明选择了某个主机组。
                choice = int(choice)
                if choice < len(user.host_groups):
                    #打印选择的主机组下面的主机列表。
                    print("------ Group: %s ------"  % user.host_groups[choice].name )
                    for index,bind_host in enumerate(user.host_groups[choice].bind_hosts):
                        print("  %s.\t%s@%s(%s)"%(index,#下标
                                                  bind_host.remote_user.username,#远程用户名
                                                  bind_host.host.hostname,  #主机名
                                                  bind_host.host.ip,    #主机ip
                                                  ))
                    print("----------- END -----------" )
            #
            #         #进入下一个死循环

                    while not exit_flag:
                        #让用户选择几个主机进入。
                        user_option = input("[(b)back, (q)quit, select host to login]:").strip()
                        if len(user_option)==0:continue
                        if user_option == 'b':break
                        if user_option == 'q':
                            exit_flag=True
                        if user_option.isdigit():
                            user_option = int(user_option)
                            if user_option < len(user.host_groups[choice].bind_hosts) :
                                print('host:',user.host_groups[choice].bind_hosts[user_option])
                                print('audit log:',user.host_groups[choice].bind_hosts[user_option].audit_logs)
                                ssh_login.ssh_login(user,
                                                    user.host_groups[choice].bind_hosts[user_option],#某个主机组下的某个主机。
                                                    session,
                                                    log_recording)#负责把日志写到数据库中的。
                else:
                    print("no this option..")
