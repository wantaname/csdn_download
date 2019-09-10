"""
初始化程序
"""
from config import *
import pymysql
import datetime

#检查配置文件是否正确
def check_config():
    for a in [group_id,super_id,qqbot,csdn_account,brower_path,driver_path,
              file_path,download_path,ip,database,limit_score]:
        if not a:
            print("有未完成的设置！")
            print(a)
            return False
    return True

#初始化数据库
def init_database():
    #连接数据库
    conn = pymysql.connect(host=database["host"], user=database["user"], port=database["port"],
                           password=database["password"],database=database['database'],
                            charset=database["charset"])
    cursor=conn.cursor()

    update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #将账号信息同步到数据库
    for a in csdn_account:
        try:

            sql="insert into account(type,username,password,today,remain,id,update_time,user_data_dir) VALUES ('%s'," \
                "'%s','%s',%d,%d,%d,'%s','%s')"%(a['type'],a['username'],a['password'],0,0,a['id'],update_time,a['user_data_dir'])
            cursor.execute(sql)
            conn.commit()
            print("账号" + str(a['id']) + "插入成功！")
        except:
            print("账号"+str(a['id'])+"已存在！")
    conn.close()


def init():
    if check_config():
        init_database()

init()