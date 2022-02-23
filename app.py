# -*- coding: UTF-8 -*-
import datetime
import os
import time
import sqlite3
import requests
from flask import Flask, request, render_template, session, redirect, url_for
from hashlib import md5

app = Flask(__name__)
app.config['SECRET_KEY'] = 'zichen123123%^&*(^*&&^*'

ver = 1.4

config = {
    "AddDirBinding": "/site?action=AddDirBinding",
    "CloseHasPwd": "/site?action=CloseHasPwd",
    "CloseLimitNet": "/site?action=CloseLimitNet",
    "CloseSSLConf": "/site?action=CloseSSLConf",
    "CloseToHttps": "/site?action=CloseToHttps",
    "CreateProxy": "/site?action=CreateProxy",
    "DelDirBinding": "/site?action=DelDirBinding",
    "Get301Status": "/site?action=Get301Status",
    "GetDirBinding": "/site?action=GetDirBinding",
    "GetDirRewrite": "/site?action=GetDirRewrite",
    "GetDirUserINI": "/site?action=GetDirUserINI",
    "GetDiskInfo": "/system?action=GetDiskInfo",
    "GetFileBody": "/files?action=GetFileBody",
    "GetLimitNet": "/site?action=GetLimitNet",
    "GetNetWork": "/system?action=GetNetWork",
    "GetPHPVersion": "/site?action=GetPHPVersion",
    "GetProxyList": "/site?action=GetProxyList",
    "GetRewriteList": "/site?action=GetRewriteList",
    "GetSSL": "/site?action=GetSSL",
    "GetSecurity": "/site?action=GetSecurity",
    "GetSiteLogs": "/site?action=GetSiteLogs",
    "GetSitePHPVersion": "/site?action=GetSitePHPVersion",
    "GetSystemTotal": "/system?action=GetSystemTotal",
    "GetTaskCount": "/ajax?action=GetTaskCount",
    "HttpToHttps": "/site?action=HttpToHttps",
    "ModifyProxy": "/site?action=ModifyProxy",
    "ResDatabasePass": "/database?action=ResDatabasePassword",
    "SQLDelBackup": "/database?action=DelBackup",
    "SQLToBackup": "/database?action=ToBackup",
    "SaveFileBody": "/files?action=SaveFileBody",
    "Set301Status": "/site?action=Set301Status",
    "SetHasPwd": "/site?action=SetHasPwd",
    "SetLimitNet": "/site?action=SetLimitNet",
    "SetPHPVersion": "/site?action=SetPHPVersion",
    "SetSSL": "/site?action=SetSSL",
    "SetSecurity": "/site?action=SetSecurity",
    "SetStatus": "/ftp?action=SetStatus",
    "SetUserPassword": "/ftp?action=SetUserPassword",
    "SetupPackage": "/plugin?action=a&name=deployment&s=SetupPackage",
    "UpdatePanel": "/ajax?action=UpdatePanel",
    "WebAddDomain": "/site?action=AddDomain",
    "WebAddSite": "/site?action=AddSite",
    "WebBackupList": "/data?action=getData&table=backup",
    "WebDelBackup": "/site?action=DelBackup",
    "WebDelDomain": "/site?action=DelDomain",
    "WebDeleteSite": "/site?action=DeleteSite",
    "WebDoaminList": "/data?action=getData&table=domain",
    "WebFtpList": "/data?action=getData&table=ftps",
    "WebGetIndex": "/site?action=GetIndex",
    "WebSetEdate": "/site?action=SetEdate",
    "WebSetIndex": "/site?action=SetIndex",
    "WebSetPs": "/data?action=setPs&table=sites",
    "WebSiteStart": "/site?action=SiteStart",
    "WebSiteStop": "/site?action=SiteStop",
    "WebSqlList": "/data?action=getData&table=databases",
    "WebToBackup": "/site?action=ToBackup",
    "Websites": "/data?action=getData&table=sites",
    "Webtypes": "/site?action=get_site_types",
    "deployment": "/plugin?action=a&name=deployment&s=GetList&type=0",
    "download": "/download?filename="
}


def GetMd5(s):  # 参考了Demo.py
    m = md5()
    m.update(s.encode("utf-8"))
    return m.hexdigest()


def GetKeyData(apikey):  # 签名算法
    now_time = time.time()
    p_data = {
        "request_token": GetMd5(str(now_time) + "" + GetMd5(apikey)),
        "request_time": now_time
    }
    return p_data


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', title="No Found", error="404 No Found", shuoming="请求的目录没有找到", ver=ver), 404


@app.errorhandler(500)
def internal_Server_error(e):
    return render_template('error.html', title="Internal Server Error", error="500 Internal Server Error",
                           shuoming="服务器无法处理请求", ver=ver), 500


@app.errorhandler(400)
def bad_requests(e):
    return render_template('error.html', title="Bad Requests", error="400 Bad Requests", shuoming="请求出现错误",
                           ver=ver), 500


@app.errorhandler(405)
def method_not_allowed(e):
    return render_template('error.html', title="Method Not Allowed", error="405 Method Not Allowed", shuoming="不被允许的请求",
                           ver=ver), 500


_ApiKey = "NULL"
_Url = "NULL"

panel_config = {
    'NAME': 'NULL',
    'SOURCE': 'NULL',
    'CPU': 'NULL',
    'OS': 'NULL',
    'IP': 'NULL',
    'SERVICE':'NULL'
}

user_config = {
    'USERNAME': 'NULL',
    'PASSWD': 'NULL',
    'QX': 'NULL',
    'QUESTION': 'NULL',
    'ANSWER': 'NULL'
}


def loadinfo():
    global _ApiKey, _Url
    try:
        conn = sqlite3.connect('panel.db')
        print("数据库打开成功")
        c = conn.cursor()
        cursor = c.execute("SELECT NAME, API, ADDRESS  from PANEL")
        for row in cursor:
            _ApiKey = row[1]
            _Url = row[2]
            panel_config['NAME'] = row[0]
        cursor = c.execute("SELECT SOURCE, IP, CPU, OS , QX  from INFO")
        for row in cursor:
            panel_config['SOURCE'] = row[0]
            panel_config['IP'] = row[1]
            panel_config['CPU'] = row[2]
            panel_config['OS'] = row[3]
            panel_config['SERVICE']=row[4]

        cursor = c.execute("SELECT USERNAME, PASSWD, QUESTION, ANSWER, QX  from USER")
        for row in cursor:
            user_config['USERNAME'] = row[0]
            user_config['PASSWD'] = row[1]
            user_config['QUESTION'] = row[2]
            user_config['ANSWER'] = row[3]
            user_config['QX'] = row[4]
        print("数据库载入成功！")
        conn.close()
    except:
        print('数据库出现错误！！！')


@app.route('/login', methods=['GET', 'POST'])
def login():  # put application's code here
    if request.method == 'GET':
        return render_template('login.html', pwd=0)
    else:
        pwd = request.form['pwd']
        usr = request.form['username']
        if pwd != '' and usr != '':
            if usr == user_config['USERNAME']:
                if pwd == user_config['PASSWD']:
                    session['username'] = usr
                    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    ip = request.remote_addr
                    f = open("log/user.log", "a")
                    f.write(f'{t} USER LOGIN  [{usr}] IP:{ip} \n')
                    f.close()
                    return redirect(url_for('panel'))
                else:
                    return render_template('login.html', pwd=1, info="密码错误")
            else:
                return render_template('login.html', pwd=1, info="用户不存在！")
        else:
            return render_template('login.html', pwd=1, info="用户名密码不能为空！")


@app.route('/reset_user', methods=['POST'])
def register():  # put application's code here
    if 'password' in session or 'reset' in session:
        usr = request.form['username']
        pwd = request.form['password']
        que = request.form['question']
        ans = request.form['answer']
        if usr == '':
            usr = user_config['USERNAME']
        if pwd == '':
            pwd = user_config['PASSWD']
        if que == '':
            que = user_config['QUESTION']
        if ans == '':
            ans = user_config['ANSWER']
        user_config['USERNAME'] = usr
        user_config['PASSWD'] = pwd
        user_config['QUESTION'] = que
        user_config['ANSWER'] = ans
        # print(user_config)
        try:
            conn = sqlite3.connect('panel.db')
            c = conn.cursor()
            c.execute(
                f"UPDATE USER set USERNAME = '{usr}',PASSWD = '{pwd}',QUESTION = '{que}',ANSWER = '{ans}' where ID=1")
            conn.commit()
            conn.close()
            print("数据库刷新成功")
        except:
            print("数据库发生错误！！！")
            session.pop('reset', None)
            session.clear()
            return render_template('error.html', title="服务器错误", error="服务器错误", shuoming="CODE:500", ver=ver)
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ip = request.remote_addr
        f = open("log/user.log", "a")
        f.write(f'{t} USER CHANGE  [{usr}] IP:{ip} \n')
        f.close()
        session.pop('reset', None)
        session.clear()
        return render_template('error.html', title="修改成功！", error="修改成功！", shuoming="请刷新页面 ",
                               ver=ver)
    else:
        return redirect(url_for('login'))


@app.route('/forget_passwd', methods=['GET', 'POST'])
def forget_passwd():  # put application's code here
    if request.method == 'GET':
        return render_template('forget.html', pwd=0, QUESTION=user_config['QUESTION'])
    else:
        answer = request.form['answer']
        if answer == user_config['ANSWER']:
            session['reset'] = user_config['ANSWER']
            return render_template('reset_user.html')
        else:
            return render_template('forget.html', pwd=1, QUESTION=user_config['QUESTION'])


@app.route('/cloud/control', methods=['GET', 'POST'])
def cloud_control():  # put application's code here
    status = cloud_status()
    if status == '运行中':
        command = 'systemctl stop cloud'
        info = '停止'
    elif status == '停止':
        command = 'systemctl start cloud'
        info = '打开'
    else:
        info = '错误！ERROR CODE=500"'
        command = 'whoami'
    shell(command)
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    ip = request.remote_addr
    f = open("log/panel.log", "a")
    f.write(f'{t} ALIST CHANGE {info} IP:{ip}  \n')
    f.close()
    return info


def cloud_status():  # put application's code here
    command = 'systemctl is-active cloud'
    status = shell(command)
    if 'in' in status:
        return "停止"
    elif 'active' in status:
        return "运行中"
    else:
        return '错误！ERROR CODE=500"'


def shell(command):
    src = os.popen(command)
    src = src.readlines()
    t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    ip = request.remote_addr
    f = open("log/shell.log", "a")
    f.write(f'{t} SHELL IP:{ip}  command:{command} \n')
    f.close()
    if len(src) == 0:
        return 'error'
    else:
        src = src[0]
        src = str(src)
        return src


@app.route('/', methods=['GET', 'POST'])
def panel(interval=1):  # put application's code here
    if 'username' in session:
        global _Url, _ApiKey
        status = GetSystemTotal(_Url, _ApiKey)
        if len(status) < 4:
            return render_template('error.html', title="ERROR", error="服务器连接失败！", shuoming="请联系管理员",
                                   ver=ver)
        mem = status['mem']
        disk = status['disk']
        disk = disk[0]
        disk = disk['size']
        disku = disk[1]
        diskt = disk[0]
        diskb = disk[3]
        timer = status['time']
        cpu = status['cpu']
        cpuc = cpu[1]
        # print(disk)
        load = status['load']
        load5 = load['five'] * 100
        zj = float(mem['memTotal']) / 1024
        ysy = float(mem['memRealUsed']) / 1024
        memq = '%.1fG/%.1fG' % (ysy, zj)
        memb = int((ysy / zj) * 100)
        hddq = f"{disku}/{diskt}"
        cpuq = str(cpu[0]) + '% ' + str(cpuc) + '核'
        cpub = cpu[0]
        fz = 1
        return render_template('index.html',
                               memq=memq, memb=memb, hddq=hddq,
                               cpuq=cpuq, cpub=cpub, fz=fz,
                               timer=timer, diskb=diskb, load5=load5,
                               ip=panel_config['IP'], CPU=panel_config['CPU'],
                               OS=panel_config['OS'], NAME=panel_config['NAME'],
                               username=user_config['USERNAME'])

    else:
        return redirect(url_for('login'))


@app.route('/program', methods=['GET', 'POST'])
def program():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    status = cloud_status()
    if status == "运行中":
        text = '正在运行...'
        text_color = 'success'
        btn_color = 'danger'
        btn_text = '停止'
    elif status == "停止":
        text = '停止运行'
        text_color = 'danger'
        btn_color = 'primary'
        btn_text = '启动'
    else:
        text = '获取失败ERROR CODE:500'
        text_color = 'warning'
        btn_color = 'warning'
        btn_text = 'ERROR'
    return render_template('program.html',
                           btn_color=btn_color, text=text,
                           text_color=text_color, btn_text=btn_text,
                           ip=panel_config['IP'],
                           username=user_config['USERNAME'])


@app.route('/web', methods=['GET', 'POST'])
def web():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        ws = Websites(_Url, _ApiKey)
        web = ws['data'][3]
        php = web['php_version']
        print(web)
        sslda = web['ssl']['notAfter']
        ssla = web['ssl']['issuer']
        ts = int(time.mktime(time.strptime(sslda, "%Y-%m-%d")))
        ns = int(time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")))
        if ns > ts:
            sslc = "warning"
            ssld = '证书品牌：' + ssla + ' 到期时间：' + sslda + " 状态：证书过期! "
        else:
            sslc = "info"
            ssld = '证书品牌：' + ssla + ' 到期时间：' + sslda + " 状态：正常 "
        site = '主页'
        url = web['name']
        if web['status'] == '1':
            site_status = '运行中...'
            site_color = 'success'
        elif web['status'] == '0':
            site_status = '已停止'
            site_color = 'danger'
        else:
            site_status = '获取信息异常'
            site_color = 'warning'

        ssl_color = ''
        siteurl = 'web'
        return render_template('web.html',
                               site=site, site_status=site_status,
                               site_color=site_color, ssld=ssld, url=url, sslc=sslc,
                               ip=panel_config['IP'], siteurl=siteurl, php=php,
                               username=user_config['USERNAME'])

@app.route('/web/on', methods=['GET', 'POST'])
def webon():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        WebSiteStart(_Url, _ApiKey, 'xelon.top')
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ip = request.remote_addr
        f = open("log/panel.log", "a")
        f.write(f'{t} WEB ON IP:{ip}  \n')
        f.close()
        return '成功'
    except:
        return '错误-ERRORCODE:400'



@app.route('/web/off', methods=['GET', 'POST'])
def weboff():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        WebSiteStop(_Url, _ApiKey, 'xelon.top')
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ip = request.remote_addr
        f = open("log/panel.log", "a")
        f.write(f'{t} WEB OFF IP:{ip}  \n')
        f.close()
        return '成功'
    except:
        return '错误-ERRORCODE:400'

@app.route('/blog', methods=['GET', 'POST'])
def blog():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        ws = Websites(_Url, _ApiKey)
        web = ws['data'][1]
        php = web['php_version']
        print(web)
        sslda = web['ssl']['notAfter']
        ssla = web['ssl']['issuer']
        ts = int(time.mktime(time.strptime(sslda, "%Y-%m-%d")))
        ns = int(time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")))
        if ns > ts:
            sslc = "warning"
            ssld = '证书品牌：' + ssla + ' 到期时间：' + sslda + " 状态：证书过期! "
        else:
            sslc = "info"
            ssld = '证书品牌：' + ssla + ' 到期时间：' + sslda + " 状态：正常 "
        site = '博客'
        url = web['name']
        if web['status'] == '1':
            site_status = '运行中...'
            site_color = 'success'
        elif web['status'] == '0':
            site_status = '已停止'
            site_color = 'danger'
        else:
            site_status = '获取信息异常'
            site_color = 'warning'

        ssl_color = ''
        siteurl = 'blog'
        return render_template('web.html',
                               site=site, site_status=site_status,
                               site_color=site_color, ssld=ssld, url=url, sslc=sslc,
                               ip=panel_config['IP'], siteurl=siteurl, php=php,
                               username=user_config['USERNAME'])

@app.route('/blog/on', methods=['GET', 'POST'])
def blogon():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        WebSiteStart(_Url, _ApiKey, 'blog.xelon.top')
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ip = request.remote_addr
        f = open("log/panel.log", "a")
        f.write(f'{t} BLOG ON IP:{ip}  \n')
        f.close()
        return '成功'
    except:
        return '错误-ERRORCODE:400'



@app.route('/blog/off', methods=['GET', 'POST'])
def blogoff():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        WebSiteStop(_Url, _ApiKey, 'blog.xelon.top')
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ip = request.remote_addr
        f = open("log/panel.log", "a")
        f.write(f'{t} BLOG OFF IP:{ip}  \n')
        f.close()
        return '成功'
    except:
        return '错误-ERRORCODE:400'

@app.route('/cloud', methods=['GET', 'POST'])
def cloud():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        ws = Websites(_Url, _ApiKey)
        web = ws['data'][2]
        php = web['php_version']
        print(web)
        sslda = web['ssl']['notAfter']
        ssla = web['ssl']['issuer']
        ts = int(time.mktime(time.strptime(sslda, "%Y-%m-%d")))
        ns = int(time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime()), "%Y-%m-%d")))
        if ns > ts:
            sslc = "warning"
            ssld = '证书品牌：' + ssla + ' 到期时间：' + sslda + " 状态：证书过期! "
        else:
            sslc = "info"
            ssld = '证书品牌：' + ssla + ' 到期时间：' + sslda + " 状态：正常 "
        site = '网盘'
        url = web['name']
        if web['status'] == '1':
            site_status = '运行中...'
            site_color = 'success'
        elif web['status'] == '0':
            site_status = '已停止'
            site_color = 'danger'
        else:
            site_status = '获取信息异常'
            site_color = 'warning'

        ssl_color = ''
        siteurl = 'cloud'
        return render_template('web.html',
                               site=site, site_status=site_status,
                               site_color=site_color, ssld=ssld, url=url, sslc=sslc,
                               ip=panel_config['IP'], siteurl=siteurl, php=php,
                               username=user_config['USERNAME'])

@app.route('/cloud/on', methods=['GET'])
def cloudon():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        WebSiteStart(_Url, _ApiKey, 'cloud.xelon.top')
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ip = request.remote_addr
        f = open("log/panel.log", "a")
        f.write(f'{t} Cloud ON IP:{ip}  \n')
        f.close()
        return '成功'
    except:
        return '错误-ERRORCODE:400'



@app.route('/cloud/off', methods=['GET'])
def cloudoff():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    try:
        WebSiteStop(_Url, _ApiKey, 'cloud.xelon.top')
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        ip = request.remote_addr
        f = open("log/panel.log", "a")
        f.write(f'{t} Cloud OFF IP:{ip}  \n')
        f.close()
        return '成功'
    except:
        return '错误-ERRORCODE:400'

@app.route('/setting', methods=['GET','POST'])
def setting():  # put application's code here
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method=='GET':
        return render_template('setting.html',s=panel_config['SERVICE'],
                           ip=panel_config['IP'],service='RHYZX',
                           username=user_config['USERNAME'])
    else:
        name=request.form['name']
        if name != '':
            panel_config['NAME'] = name
            try:
                conn = sqlite3.connect('panel.db')
                c = conn.cursor()
                c.execute(
                    f"UPDATE PANEL set NAME = '{name}' where ID=1")
                conn.commit()
                conn.close()
                print("数据库刷新成功")
                t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                ip = request.remote_addr
                f = open("log/panel.log", "a")
                f.write(f'{t} SERVERNAME CHANGE {name} IP:{ip}  \n')
                f.close()
            except:
                print("数据库刷新失败！")
            return redirect(url_for('setting'))
        return redirect(url_for('setting'))



@app.route('/clear_login', methods=['GET'])
def clear():  # put application's code here
    session.clear()
    return redirect(url_for('login'))


def GetSystemTotal(btpanel, btkey):  # 获取系统基础统计
    url = btpanel + config["GetNetWork"]
    return requests.post(url, GetKeyData(btkey)).json()


def Websites(btpanel, btkey):  # 获取网站列表
    url = btpanel + config["Websites"]
    return requests.post(url, GetKeyData(btkey)).json()


def WebSiteStop(btpanel, btkey, site):  # 停用网站
    """
    btpanel                面板地址,可用PingBaoTa()拼接
    btkey                  API密匙
    site                   网站名
    """
    url = btpanel + config["WebSiteStop"]
    data = GetKeyData(btkey)
    data["id"] = str(GetSiteID(btpanel, btkey, site))
    data["name"] = site
    return requests.post(url, data).text


def WebSiteStart(btpanel, btkey, site):  # 启用网站
    """
    btpanel                面板地址,可用PingBaoTa()拼接
    btkey                  API密匙
    site                   网站名
    """
    url = btpanel + config["WebSiteStart"]
    data = GetKeyData(btkey)
    data["id"] = GetSiteID(btpanel, btkey, site)
    data["name"] = site
    return requests.post(url, data).json()


def GetSiteID(btpanel, btkey, site):  # 获取指定站点ID 若站点不存在则返回-1
    data = Websites(btpanel, btkey)["data"]
    for i in data:
        if i["name"] == site:
            return i["id"]
    return -1


if __name__ == '__main__':
    verify = requests.get('https://rerizon.cn/server_verify/zichen.html').text
    if verify == 'OK':
        info = '''===============================================
  ____       ____   _    _   _ _____ _     
|  _ \     |  _ \ / \  | \ | | ____| |    
| |_) |____| |_) / _ \ |  \| |  _| | |    
|  _ <_____|  __/ ___ \| |\  | |___| |___ 
|_| \_\    |_| /_/   \_\_| \_|_____|_____|
==============================================='''

        print(info)
        print(f'R-PANEL SERVER PANEL  Author:RHYZX VER:{ver}')
        loadinfo()
        app.run(host='0.0.0.0', port=int("9999"))
    else:
        print('++++++++++++++++++++++++++++++++++++')
        print('   ERROR CODE VERIFY 服务器验证错误！  ')
        print('++++++++++++++++++++++++++++++++++++')
