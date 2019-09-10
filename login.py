"""
此模块实现用pyppeteer登录csdn并退出，注意登录需要单独操作
"""

import asyncio
from pyppeteer import launch
from exe_js import *
from config import *
import pymysql

login_url="https://passport.csdn.net/login"
timeout=30000
#多个账号一起登录
conn=pymysql.connect(host=database["host"], user=database["user"], port=database["port"], password=database["password"],
                                   charset=database["charset"],database=database['database'])
cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
#从数据库中选择账号登录
sql="select * from account"
res=cursor.execute(sql)
accounts=cursor.fetchall()
conn.close()

async def login(account:dict)->bool:
    # 浏览器对象，对浏览器的配置在这里完成
    print("正在登录账号："+account["username"])
    browser = await launch(options={
        "headless": False,
        "userDataDir": account["user_data_dir"],
        "autoClose":False,
        "args": ["--disable-notifications","--disable-infobars"],
        "executablePath":brower_path,
    })

    # 打开一个新的窗口/标签页
    page = await browser.newPage()
    #设置超时时间
    page.setDefaultNavigationTimeout(timeout)
    await page.goto(login_url)
    if page.url.find(login_url)==-1:
        #已登录
        print("账号"+account['username']+"已登录！")
        await browser.close()
        return True

    await page.evaluate(js1)
    #while not await page.querySelector("li:nth-child(2) a"):
     #   pass
    #await page.click("li:nth-child(2) a")
    #time.sleep(1)
    #await page.type(selector="#all",text=account)
    #await page.type(selector="[name=pwd]",text=password)
    # await page.click(".btn")
    #手动登录中
    hand_login=input("手动登录中,登录成功按1:")
    if hand_login=="1":
        # 登录成功
        print("账号："+account['username']+"登录成功！")
        await browser.close()
        return True
    else:
        print("手动登录失败！")
        await browser.close()
        return False
print("您的数据库中有以下账号：")
print("序号"+" "*3+"账号id"+" "*3+"账号名"+" "*5+"账号类型")
t=0
for a in accounts:
    print(str(t)+" "*5+str(a["id"])+" "*3+a["username"]+" "*5+a['type'])
    t+=1
select=input("请输入您要登录的序号：")
select=int(select)
if select in range(0,len(accounts)):
    asyncio.get_event_loop().run_until_complete(login(accounts[select]))
else:
    print("输入错误！")


