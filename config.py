#机器人所在QQ群
group_id=[]

#超级管理员
super_id=[]

#机器人QQ号码,int
qqbot=


#以下可依次添加多个账号...
csdn_account=[
    #资料路径必须配置
    {"username":'',"password":"","user_data_dir":"","type":"vip",'id':1},
    {"username":'',"password":"","user_data_dir":"","type":"vip",'id':2},

]
brower_path="C:/Users/Administrator/AppData/Local/Google/Chrome/Application/chrome.exe"
#chrome驱动路径
driver_path="C:/Users/Administrator/Desktop/csdn_download/resource/chromedriver.exe"
dir="file"
#文件所在域名空间
ip=''
#下载路径,经测试只能用反斜杠！
download_path="C:\\Users\\Administrator\\Desktop\\csdn_download\\file_tmp"
#file
file_path="C:/Users/Administrator/Desktop/csdn_download/file"

#数据库配置
database={
    "host":"",
    "port":3306,
    "user":"",
    "password":"",
    #必须要自己新建，表可以不用
    "database":"",
    "charset":"utf8",
}

#这是限制积分，在此数字内用积分下载
limit_score=2
