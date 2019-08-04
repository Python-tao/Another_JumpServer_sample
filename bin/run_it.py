import os,sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

if __name__ == '__main__':
    from modules.actions import excute_from_command_line
    #处理输入的命令行命令的函数
    #sys.argv,是一个列表，里面的元素，是命令行输入的程序名称和位置参数。
    excute_from_command_line(sys.argv)

