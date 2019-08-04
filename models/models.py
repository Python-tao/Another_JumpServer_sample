
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from conf import settings


from sqlalchemy import Table, Column, Enum,Integer,String,DateTime, ForeignKey,UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import ChoiceType

from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker


#此模块用于初始化数据库。

#基类
Base = declarative_base()

#多对多表,用户与绑定表
user_m2m_bindhost = Table('user_m2m_bindhost', Base.metadata,
                        Column('userprofile_id', Integer, ForeignKey('user_profile.id')),
                        Column('bindhost_id', Integer, ForeignKey('bind_host.id')),
                        )
#多对多表，主机组与绑定表
bindhost_m2m_hostgroup = Table('bindhost_m2m_hostgroup', Base.metadata,
                          Column('bindhost_id', Integer, ForeignKey('bind_host.id')),
                          Column('hostgroup_id', Integer, ForeignKey('host_group.id')),
                          )
#多对多表，用户与主机组
user_m2m_hostgroup = Table('userprofile_m2m_hostgroup', Base.metadata,
                               Column('userprofile_id', Integer, ForeignKey('user_profile.id')),
                               Column('hostgroup_id', Integer, ForeignKey('host_group.id')),
                               )

#后端主机表
class Host(Base):
    __tablename__ = 'host'
    id = Column(Integer,primary_key=True)
    hostname = Column(String(64),unique=True,nullable=False)   #主机名
    ip = Column(String(64),unique=True,nullable=False) #主机ip
    port = Column(Integer,default=22,nullable=False)   #主机端口，此处是ssh服务端口。

    def __repr__(self):
        return self.hostname

#主机组表
class HostGroup(Base):
    __tablename__ = 'host_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True,nullable=False)  #组名
    #多对多表，通过组名查找对应的主机
    bind_hosts = relationship("BindHost",secondary="bindhost_m2m_hostgroup",backref="host_groups")

    def __repr__(self):
        return self.name

#远程用户表
class RemoteUser(Base):
    __tablename__ = 'remote_user'
    #联合唯一键
    #意思是auth_type,username,password三个字段联合起来是唯一的，如果有不唯一的值，就会报错。
    #_user_passwd_uc，这个字段用来保存上述三个字段联合起来的哈希值。
    __table_args__ = (UniqueConstraint('auth_type', 'username','password', name='_user_passwd_uc'),)

    id = Column(Integer, primary_key=True)
    AuthTypes = [
        ('ssh-password','SSH/Password'),#密码认证，第一个是存在数据库的，第二个是显示给用户看的。
        ('ssh-key','SSH/KEY'),#key文件认证
    ]
    #认证类型，两种2选1.
    auth_type = Column(ChoiceType(AuthTypes),nullable=False)
    #远程用户名
    username = Column(String(32),nullable=False)
    #远程用户密码
    password = Column(String(128),nullable=True)

    def __repr__(self):
        return self.username
#绑定表
class BindHost(Base):
    '''
    id  host            remote_user
    1   192.168.1.11    web
    2   192.168.1.11    mysql

    '''
    __tablename__ = "bind_host"
    #联合唯一键
    __table_args__ = (UniqueConstraint('host_id','remoteuser_id', name='_host_remoteuser_uc'),)

    id = Column(Integer, primary_key=True)
    #后端主机
    host_id = Column(Integer,ForeignKey('host.id'),nullable=False)
    #group_id = Column(Integer,ForeignKey('group.id'))
    #远程用户
    remoteuser_id = Column(Integer, ForeignKey('remote_user.id'),nullable=False)
    #通过绑定表查找对应的主机。
    host = relationship("Host",backref="bind_hosts")
    #host_group = relationship("HostGroup",backref="bind_hosts")
    #通过绑定表查找对应的远程用户
    remote_user = relationship("RemoteUser",backref="bind_hosts")
    def __repr__(self):
        return "<后端主机ip：%s -- 远程用户名：%s >" %(self.host.ip,
                                   self.remote_user.username
                                  )
#堡垒机用户表
class UserProfile(Base):
    __tablename__ = 'user_profile'

    id = Column(Integer, primary_key=True)
    #堡垒机用户名。
    username = Column(String(32),unique=True,nullable=False)
    # 堡垒机用户密码。
    password = Column(String(128),nullable=False)
    #通过用户查找绑定表。
    bind_hosts = relationship("BindHost", secondary='user_m2m_bindhost',backref="user_profiles")
    #通过用户查找主机组。
    host_groups = relationship("HostGroup",secondary="userprofile_m2m_hostgroup",backref="user_profiles")

    def __repr__(self):
        return self.username

#保存日志信息的表。
class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer,primary_key=True)
    #堡垒机用户id
    user_id = Column(Integer,ForeignKey('user_profile.id'))
    #后端主机与远程用户对应表的id，
    bind_host_id = Column(Integer,ForeignKey('bind_host.id'))
    #日志类型。
    action_choices = [
        (0,'CMD'),
        (1,'Login'),
        (2,'Logout'),
        (3,'GetFile'),
        (4,'SendFile'),
        (5,'Exception'),
    ]
    #另外一种格式的日志类型。
    action_choices2 = [
        (u'cmd',u'CMD'),
        (u'login',u'Login'),
        (u'logout',u'Logout'),
        #(3,'GetFile'),
        #(4,'SendFile'),
        #(5,'Exception'),
    ]
    action_type = Column(ChoiceType(action_choices2))
    #具体是命令
    cmd = Column(String(255))
    #日期时间。
    date = Column(DateTime)

    #relationship字段
    #对应的堡垒机用户
    user_profile = relationship("UserProfile")
    #对应的主机绑定表
    bind_host = relationship("BindHost",backref="audit_logs")









if __name__ == "__main__":
    engine = create_engine(settings.ConnParams,)
    Base.metadata.create_all(engine)  # 创建表结构
    print("数据库初始化成功。")