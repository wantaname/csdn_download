
from aiocqhttp import CQHttp
import config
from main_ddl import main_download
import pymysql
from config import *
import requests
import datetime
import re
import socket
import json


#全局变量,
#下载好后才能下载


is_busy=False

bot=CQHttp(enable_http_post=False)

#数据库连接，返回连接对象
def database_conn():
    conn=pymysql.connect(host=database["host"], user=database["user"], port=database["port"], password=database["password"],
                                   database=database["database"], charset=database["charset"])

    return conn

#搜索csdn资源,返回资源列表
def search_csdn(keyword:str)->dict:

    host = ""
    port = 1245
    s = socket.socket()
    s.connect((host, port))
    keyword=json.dumps(keyword)
    s.send(keyword.encode("utf-8"))
    res = s.recv(4096).decode('utf-8')
    res = json.loads(res)#type:list
    s.close()
    count=1
    reply=''
    for a in res:
        reply+='\n'+str(count)+'.'+a[0]+' '+a[1]
        count+=1
    return {'reply':reply}

#发送邮件
def sendEmail(receivers:list,message:str)->bool:
    host = ""
    port = 1245
    s = socket.socket()
    s.connect((host, port))

    send_msg=[receivers,message]
    send_msg=json.dumps(send_msg)
    s.send(send_msg.encode('utf-8'))
    res=s.recv(4096).decode('utf-8')
    res=json.loads(res)#type:bool
    s.close()
    return res

#充值
async def chongzhi():
    return "需要充值请联系管理员！"

# 帮助
async def help():
    reply="下载格式：下载+资源链接!"
    return reply

#查询，返回查询结果
async def query(user_id):
    conn = database_conn()
    # 配置结果集为字典形式
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)

    sql='select * from USER WHERE qq="%s"'%(user_id,)
    res=cursor.execute(sql)
    # 如果没有查到用户，则添加
    if res == 0:
        # %s要加引号
        sql = 'INSERT into USER (qq,download_count,remain) VALUES ("%s",0,0)' % (user_id)
        cursor.execute(sql)
        conn.commit()
    # 查询用户剩余下载次数
    sql = 'select * from USER WHERE qq="%s"' % (user_id,)
    res = cursor.execute(sql)
    user_info = cursor.fetchone()
    reply="\n已下载："+str(user_info['download_count'])+'次'
    reply+='\n剩余下载：'+str(user_info['remain'])+'次'
    conn.close()
    return reply

#充值，返回充值结果
def super_chongzhi(qq:str,count:int):
    '''
    :param qq: 充值的QQ
    :param count: 充值次数
    :return: 
    不存在用户则创建
    '''

    select_sql = 'select * from USER WHERE qq="%s"' % (qq)
    conn=database_conn()
    # 配置结果集为字典形式
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    res = cursor.execute(select_sql)
    if res==0:
        #创建用户
        create_sql = 'INSERT into USER (qq,download_count,remain) VALUES ("%s",0,0)' % (qq)
        cursor.execute(create_sql)
        conn.commit()
    res=cursor.execute(select_sql)
    current = cursor.fetchone()
    sql = 'update user set remain=%d WHERE qq="%s"' % (count + current['remain'], qq,)
    cursor.execute(sql)
    conn.commit()

    #写入充值记录
    time=datetime.datetime.now()
    sql="insert into chongzhi(qq,count,time) VALUES ('%s',%d,'%s')"%(qq,count,time.strftime("%Y-%m-%d %H:%M:%S"))
    cursor.execute(sql)
    conn.commit()
    user=cursor.fetchone()
    conn.close()

    reply = "充值成功！"
    reply += "\n充值QQ：" + qq
    reply += "\n充值次数：" + str(count)
    reply += '\n剩余次数：' + str(current['remain'] + count)
    return {"reply":reply}

#处理原始消息
def handle_msg(msg:str)->str:
    """
    对原始消息进行处理
    :param msg: 
    :return: 
    """
    #去掉@的部分
    msg=msg.replace("[CQ:at,qq=%d]"%(qqbot),'').strip()
    #去掉命令前的-
    if msg[0]=="-":
        msg=msg.replace("-",'')
    return msg

#提取链接
def handle_url(msg:str)->str:
    # msg=msg.replace(' ','').replace('\n','')
    # #去掉url前面的部分
    # url=msg.split("http")[-1]
    # url="http"+url
    # #去掉url后面的部分,这种方法不好，最好正则
    # url=url.split("?")[0]
    # if url[-1]=='/':
    #     url=url.rstrip("/")
    # if url[-1]==']':
    #     url=url.rstrip(']')

    pattern = '(http|https)://download.csdn.net/download/(\w|_)+/(\d)+'
    pos = re.search(pattern=pattern, string=msg).span()
    url = msg[pos[0]:pos[1]]
    return url

#提取邮箱
def hand_mail(msg:str)->str:
    # msg = msg.replace(' ', '').replace('\n', '')
    pattern = "([a-zA-Z0-9]|_|-)+@(\w|\.)+"
    pos = re.search(pattern=pattern, string=msg).span()
    mail = msg[pos[0]:pos[1]]
    return mail

#更新用户下载次数,这里建议使用try，成功返回None,失败终止进程
def update_user(user_id:str):
    try:
        conn = database_conn()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql = 'select * from USER WHERE qq="%s"' % (user_id,)
        res = cursor.execute(sql)
        user_info = cursor.fetchone()
        user_info["download_count"] += 1
        user_info['remain'] -= 1
        sql = 'update user set download_count=%d,remain=%d WHERE qq="%s"' % (
            user_info['download_count'], user_info['remain'], user_id)
        cursor.execute(sql)
        conn.commit()
        conn.close()
    except:
        return "更新用户信息失败！"
    return None

#查询用户剩余下载次数,返回下载次数
def query_remain(user_id:str):
    conn = database_conn()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    # 查询用户
    sql = 'select * from USER WHERE qq="%s"' % (user_id,)
    res = cursor.execute(sql)
    # 如果没有查到用户，则添加
    if res == 0:
        # %s要加引号
        sql = 'INSERT into USER (qq,download_count,remain) VALUES ("%s",0,0)' % (user_id)
        cursor.execute(sql)
        conn.commit()

    # 查询用户剩余下载次数
    sql = 'select * from USER WHERE qq="%s"' % (user_id,)
    res = cursor.execute(sql)
    remain = cursor.fetchone()
    return remain["remain"]

#文件命中,直接返回文件消息，否则返回None
def direct_return(url:str):
    #local文件命中,
    #连接本地数据库
    conn = database_conn()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = 'select * from download WHERE url="%s"' % (url,)
    res = cursor.execute(sql)
    has_url = cursor.fetchone()
    conn.commit()

    # 存在直接返回
    if has_url:
        reply = "\n资源标题:" + has_url['title']
        reply += "\n资源积分:" + str(has_url["score"])
        reply += "\n文件大小:" + has_url["size"]
        reply += "\n下载地址:" + has_url["download_path"]
        sql='insert into direct_return(url,source) VALUES ("%s","%s")'%(url,has_url['download_path'])
        cursor.execute(sql)
        conn.commit()
        conn.close()
        return reply
    conn.close()
    return None

#下载
async def download(url:str,user_id:str):

    global is_busy
    # 文件命中直接返回
    reply = direct_return(url=url)

    if reply:
        # 更新用户信息
        up_us = update_user(user_id=user_id)
        if up_us != None:
            return {"reply": up_us}
        return {"reply": reply}

    is_busy = True

    response = main_download(url=url, user_id=user_id)
    # 下载失败的情况！
    if type(response) == str:
        return {"reply": response}
    # 更新用户信息
    up_us = update_user(user_id=user_id)
    if up_us != None:
        return {"reply": up_us}

    reply = "\n资源标题:" + response['file_title']
    reply += "\n资源积分:" +str(response["file_score"])
    reply += "\n文件大小:" + response["file_size"]
    reply += "\n下载地址:" + response["download_path"]
    return {"reply":reply}

#群消息处理
@bot.on_message("group",)
async def handle_group_msg(context):
    global is_busy

    #获取消息
    user_id = context['user_id']#type:int
    group_id = context['group_id']#type:int
    msg = context['message']  # type:str

    #忽略其他群的消息
    if group_id not in config.group_id:
        return
    # 对原始消息进行处理

    msg = handle_msg(msg)

    #搜索功能
    if msg.find('搜索')==0:
        s=msg.split()
        if len(s)==2:
            return search_csdn(s[1])

    #充值
    if msg.find("充值")==0:

        if user_id in config.super_id:

            buy=msg.replace("充值", '').replace("次", '')

            buy = buy.split()

            if len(buy) == 2:
                return super_chongzhi(qq=buy[0], count=int(buy[1]))
        else:
            #用户充值
            res = await chongzhi()
            return {'reply': res}
    if msg=="查询":
        res = await query(user_id)
        return {"reply": res}
    if msg == "下载":
        res = await help()
        return {'reply': res}

    # 确定有链接
    if msg.find("https://download.csdn.net/download/") !=-1:
        # 提取url进行处理
        url = handle_url(msg=msg)
        if is_busy:
            return {"reply": "系统繁忙,请稍后再试!"}
        if query_remain(user_id=str(user_id)) == 0:
            return {"reply": "下载次数不足，请联系管理员充值！"}
        # 开始下载
        await bot.send_group_msg(group_id=group_id, message="正在下载...")
        user_id = str(user_id)
        reply=await download(url=url,user_id=user_id)#type:dict
        is_busy = False
        # #如果有邮箱
        if msg.find("@")!=-1:
            #提取邮箱
            receiver=hand_mail(msg)
            receivers=[]
            receivers.append(receiver)
            message=reply['reply']+"""
            \n这是机器人自动发的，你可以添加QQ群：{},机器人在线随时自助下载！
            """.format(894761502,)
            print(receivers)
            res=sendEmail(receivers=receivers,message=message)
            if res:
                reply['reply']+="\n邮件发送成功！"
            else:
                reply['reply'] +="\n邮件发送失败！"
    else:
        return

    return reply

#私聊消息处理
@bot.on_message("private",)
async def handle_private_msg(context):
    user_id=context['user_id']#type:int
    msg=context['message']

    global is_busy

    # 对原始消息进行处理
    msg = handle_msg(msg)

    # 搜索功能
    if msg.find('搜索') == 0:
        s = msg.split()
        if len(s) == 2:
            return search_csdn(s[1])
    # 充值
    if msg.find("充值") == 0:
        # 管理员消息: 充值
        if user_id in config.super_id:
            buy = msg.replace("充值", '').replace("次", '')
            buy = buy.split()
            if len(buy) == 2:
                return super_chongzhi(qq=buy[0], count=int(buy[1]))
        else:
            # 用户充值
            res = await chongzhi()
            return {'reply': res}
    if msg == "查询":
        res = await query(user_id)
        return {"reply": res}
    if msg == "下载":
        res = await help()
        return {'reply': res}

    # 确定有链接
    if msg.find("https://download.csdn.net/download/") != -1:
        # 提取url进行处理

        url = handle_url(msg=msg)

        if is_busy:
            return {"reply": "系统繁忙,请稍后再试!"}
        if query_remain(user_id=str(user_id)) == 0:
            return {"reply": "下载次数不足，请联系客服QQ：{}充值！".format(525817640)}

        # 开始下载
        await bot.send_private_msg(user_id=user_id, message="正在下载...")
        user_id = str(user_id)

        reply= await download(url=url, user_id=user_id)  # type:dict
        is_busy = False
        # #如果有邮箱
        if msg.find("@") != -1:
            # 提取邮箱
            receiver = hand_mail(msg)
            receivers = []
            receivers.append(receiver)
            message = reply['reply'] + """
                        \n这是机器人自动发的，你可以添加QQ群：{},机器人在线随时自助下载！
                        """.format(894761502, )
            print(receivers)
            res = sendEmail(receivers=receivers, message=message)
            if res:
                reply['reply'] += "\n邮件发送成功！"
            else:
                reply['reply'] += "\n邮件发送失败！"
    else:
        message = '欢迎新人~你可以发送如下指令：'
        message += "\n{}个人信息：-查询".format("[CQ:emoji,id=128147]")
        message += "\n{}次数充值：-充值".format("[CQ:emoji,id=128147]")
        message += '\n{}csdn下载：-下载'.format("[CQ:emoji,id=128147]")
        reply={"reply":message}
    return reply

#好友请求处理
@bot.on_request("friend")
async def hand_friend_request(context):
    # 将好友加到数据库
    conn = database_conn()
    # 配置结果集为字典形式
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    user_id=str(context['user_id'])
    try:
        sql='insert into new_friend(qq) VALUES ("%s")'%(user_id)
        cursor.execute(sql)
        conn.commit()
        conn.close()
    except:
        print("添加好友到数据库失败！")
    return {'approve':True}

#加群请求处理
@bot.on_request('group')
async def handle_group_request(context):
    return {'approve':True}


# 通知处理
@bot.on_notice('group_increase')
async def handle_group_increase(context):
    message = '欢迎新人~你可以发送如下指令：'
    message += "\n{}个人信息：-查询".format("[CQ:emoji,id=128147]")
    message += "\n{}次数充值：-充值".format("[CQ:emoji,id=128147]")
    message += '\n{}csdn下载：-下载'.format("[CQ:emoji,id=128147]")
    await bot.send(context, message=message, at_sender=True)

if __name__=="__main__":
    bot.run(host="127.0.0.1",port=8080)
