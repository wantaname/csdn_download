"""
此模块实现下载：vip下载函数和积分下载函数，还包括两者的一些公有函数
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from selenium.webdriver.common.action_chains import ActionChains
from config import *
import pymysql
import datetime
import socket
import json

#全局变量

# 用获取积分，返回-1链接无效，返回None则有版权限制
def get_score(url:str)->int:

    host = "45.248.86.152"
    port = 1245
    s = socket.socket()
    s.connect((host, port))
    url=json.dumps(url)
    s.send(url.encode("utf-8"))
    res = s.recv(1024).decode('utf-8')
    res=json.loads(res)
    print(res)
    s.close()
    return res

#数据库连接，返回连接对象
def database_conn():
    conn=pymysql.connect(host=database["host"], user=database["user"], port=database["port"], password=database["password"],database=database['database'],charset=database["charset"])

    return conn

#根据不同的账户返回浏览器对象
def init_chrome(user_data_dir:str,brower_path:str,download_path:str,driver_path:str)->webdriver.Chrome:
    global driver
    # 配置浏览器
    # 个人资料路径
    user_data_dir =r"--user-data-dir="+user_data_dir
    # 加载配置数据
    option = webdriver.ChromeOptions()
    option.add_argument('--log-level=3')
    option.add_argument('--safebrowsing-disable-download-protection')
    option.add_argument("--safebrowsing-disable-extension-blacklist")
    #option.add_argument('--headless')
    option.binary_location=brower_path
    prefs={
        'download.default_directory':download_path,
        'safebrowsing.enabled': True,
    }
    option.add_experimental_option("prefs",prefs)
    option.add_argument(user_data_dir)
    option.add_argument('--disable-infobars')
    option.add_argument("--disable-notifications")
    # 浏览器驱动对象
    driver = webdriver.Chrome(chrome_options=option, executable_path=driver_path)
    return driver

#登录检测，同时获取当前积分、下载次数
def login_check(driver,account_dict):
    driver.get("https://download.csdn.net/my/downloads")
    current=0
    if driver.current_url=="https://download.csdn.net/my/downloads":
        print("已登录")

        if account_dict["type"]=="jifen":
            try:
                # 等待加载剩余积分
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div[1]/div[1]/ul/li[1]/span"))
                )
                current = driver.find_element_by_xpath("/html/body/div[5]/div/div[1]/div[1]/ul/li[1]/span").text
            except:
                print("获取账户积分超时！")
                return None
        if account_dict["type"]=="vip":
            try:
                # 等待加载剩余次数
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[5]/div/div[1]/div[2]/ul/li[1]/span"))
                )
                current = driver.find_element_by_xpath("/html/body/div[5]/div/div[1]/div[2]/ul/li[1]/span").text
            except:
                print("获取账户剩余下载超时！")
                return None
        return int(current)

    else:
        print(" 未登录!")
        return False

#文件处理：等待文件下载完成，压缩文件，删除文件
def file_handle(url:str)->str:
    """
    :param file: 文件全路径
    :return: 处理后的文件路径
    
    """
    url=url.rstrip("/")
    global download_path,file_path
    import zipfile
    if download_path[-1]!='/':
        download_path=download_path+"/"
    if file_path[-1]!="/":
        file_path=file_path+"/"

    while True:
        file_list=os.listdir(download_path)
        if not file_list:
            continue
        if file_list[0].split(".")[-1] == "tmp":
            continue
        if file_list[0].find("crdownload") == -1:
            #文件全路径
            file_abs = download_path + os.listdir(download_path)[0]
            print("下载完成")
            break
    file=file_abs.split("/")[-1]
    file_name=url.split("/")[-1]

    #在文件目录创建压缩文件
    zip_file=zipfile.ZipFile(file_path+file_name+'.zip',"w",zipfile.ZIP_DEFLATED)
    zip_file.write(file_abs,file)
    zip_file.close()
    #删除文件
    os.remove(file_abs)
    # try:
    #     print("正在移动文件")
    #     os.rename(src=file_abs, dst=file_path+file)
    #     print("文件位于："+file_path)
    # except:
    #     print("文件已存在!")

    url_path = "http://"+ip+"/"+dir+"/"+file_name+".zip"
    return url_path

#选择满足条件的账户：随机选择vip号和jifen号,有则返回账号字典，没有则返回None
def choose_account(score:int,**params):
    import random
    global limit_score
    conn = database_conn()
    remove_id=params.get('remove')
    if not remove_id:
        remove_id=-1
    # 配置结果集为字典形式
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    #更新当日下载次数
    sql = "select * from account WHERE today>=%d" % (20,)
    cursor.execute(sql)
    res = cursor.fetchall()
    # 获取当前日期
    now = datetime.datetime.now()
    for a in res:
        date = a['update_time'].date()
        if now.date()!=date:
            #重置次数
            sql='update account set today=0 WHERE id=%d'%(a['id'])
            cursor.execute(sql)
            conn.commit()
    # if now.date() == date:
    # 查积分号，并且今日剩余和积分剩余都要不为0
    if score<=limit_score:
        sql = "select * from account WHERE TYPE='%s' AND today < %d AND remain >= %d AND id!=%d" % ("jifen", 20,score,remove_id)
        cursor.execute(sql)
        info = cursor.fetchall()
        count=len(info)
        print(info)
        if count!=0:
            account=random.randint(0,count-1)
            return info[account]

    sql="select * from account WHERE TYPE='%s' AND today<%d AND remain!=%d AND id!=%d" % ("vip", 20, 0,remove_id)
    cursor.execute(sql)
    info = cursor.fetchall()#type:list
    count = len(info)
    if count==0:
        # 没有可用的vip号
        conn.close()
        return None
    conn.close()
    account=random.randint(0,count-1)#type:int
    return info[account]
#积分号下载模块
def score_download(driver,**params):
    # 等待确认按钮出现
    try:
        element = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[13]/div[4]/a"))
        )
    except:
        # 出现错误
        driver.quit()
        return "load confirm button error!"
    # 点击确认按钮
    # 确定下载按钮，可能达到下载上限
    try:
        vip_btn = driver.find_element_by_xpath("/html/body/div[13]/div[4]/a")  # 这行没问题
        vip_btn.click()
    except:
        print("点击确认按钮失败！")
        driver.quit()
        return "click confirm button error!"
    # 此时可能有验证码,如果没有验证码则已经开始下载了
    try:

        element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, "nc_1_n1z"))
        )
        slideblock = driver.find_element_by_id("nc_1_n1z")
        #
        print("正在验证滑块！")
        # 鼠标点击拖拽块不松开
        ActionChains(driver).click_and_hold(slideblock).perform()
        # 向右移动
        ActionChains(driver).move_by_offset(xoffset=300, yoffset=0).perform()
        time.sleep(0.5)
        # 点确认下载
        detail_submit = driver.find_element_by_id("detail_submit")
        # 点击
        detail_submit.click()
        return None
    except:
        print("无需验证！")
#vip号下载模块
def vip_download(driver,**params):
    try:
        element = WebDriverWait(driver, 6).until(
            EC.presence_of_element_located((By.ID, "vip_btn"))

        )
        vip_btn = driver.find_element_by_id("vip_btn")
        vip_btn.click()
        return None
    except:
        driver.quit()
        print("点击vip确认按钮失败！")
        return "click vip confirm button error!"