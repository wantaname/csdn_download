"""
这是主下载文件
"""
from download import *
import datetime


#主下载逻辑，从一个链接开始;给bot下载的相应结果
def main_download(url,user_id:str):

    #第一步: requests打开链接获取积分
    score=get_score(url)
    if score==-1:
        return "链接无效！"
    if score==-2:
        return "版权限制！请联系管理员"

    #第二步选择合适账号
    account_dict=choose_account(score=score)#type:dict

    if not account_dict:
        return "今日下载次数已达上限，请明日再来！"


    #第四步：执行浏览器初始化等相关操作
    driver=init_chrome(user_data_dir=account_dict["user_data_dir"],
                       brower_path=brower_path,download_path=download_path,driver_path=driver_path)
    #第五步：执行登录检测，顺便返回当前次数或者积分
    current=login_check(driver,account_dict=account_dict)

    #如果未登录则换号
    if current==False:
        driver.close()
        choose_account(score=score,remove=account_dict)

    #以下为登录后的情况
    driver.get(url)
    # 等待加载标题
    try:

        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[@id='download_top']/div[1]/div/dl/dd/h3/span[1]"))
        )
    except:
        driver.quit()
        return "load title error!"
    print("获取文件信息")
    file_score = score
    print("所需积分:" + str(file_score))
    file_size = driver.find_element_by_class_name("dl_b").find_element_by_tag_name("em").text
    print("文件大小:" + file_size)
    file_title = driver.find_element_by_xpath("//*[@id='download_top']/div[1]/div/dl/dd/h3/span[1]").text.strip()
    print("标题:" + file_title)

    try:

        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "direct_download"))
        )
        vip_download_btn = driver.find_element_by_class_name("direct_download")
        vip_download_btn.click()
    except:
        driver.quit()
        print("点击下载按钮失败！")
        return "click download button error!"

    #接下来就不一样了
    #积分号的情况：
    if account_dict["type"]=="jifen":

        res=score_download(driver=driver)
        ##有错误发生
        if res !=None:
            return res
        #更新当前积分
        conn=database_conn()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql="update account set remain=%d WHERE id=%d" % (current-score,account_dict['id'])
        cursor.execute(sql)
        conn.commit()
        conn.close()

    #vip号
    elif account_dict["type"]=="vip":
        res=vip_download(driver=driver)
        if res != None:
            return res
        # 更新当前下载次数
        conn = database_conn()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        sql = "update account set remain=%d WHERE id=%d" % (current - 1, account_dict["id"])
        cursor.execute(sql)
        conn.commit()
        conn.close()
    ##处理文件
    url_path = file_handle(url=url)
    driver.quit()
    #下载完后更新download,account表
    conn = database_conn()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    #获取当前日期
    now = datetime.datetime.now()
    # 将下载记录写入数据库
    conn = database_conn()
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    sql = 'INSERT into download (qq,url,score,size,download_path,title,download_time) VALUES ' \
          '("%s","%s",%d,"%s","%s","%s","%s")' % (
              user_id, url, file_score, file_size, url_path,
              file_title,now.strftime("%Y-%m-%d %H:%M:%S"))
    cursor.execute(sql)
    conn.commit()

    # 更新账号信息
    sql="select * from account WHERE id=%d"%(account_dict['id'])
    cursor.execute(sql)
    res=cursor.fetchone()

    today=res['today']+1
    sql = "update account set today=%d,update_time='%s' WHERE id=%d" % (today,now.strftime("%Y-%m-%d %H:%M:%S"), account_dict['id'])
    cursor.execute(sql)
    conn.commit()
    conn.close()
    download_result = {
        "file_score": file_score,
        "download_path": url_path,
        "file_title": file_title,
        "file_size": file_size,
    }
    return download_result


