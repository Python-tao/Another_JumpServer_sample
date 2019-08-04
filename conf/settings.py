
import os
import sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)



#sqlite连接方式
ConnParams = "sqlite:///%s/db/database.db"%(BASE_DIR)
#yaml数据文件的路径
StateFileBaseDir= "%s/share/examples"%(BASE_DIR)