#!/usr/bin/python
# -*- coding: utf-8 -*-
# 参考文章：
# http://www.python88.com/topic/151957
# http://www.manongjc.com/detail/32-xtynhbbjfwtxoen.html
import requests, json
from colorama import init, Fore, Back, Style
import threading, queue
import imp
import sys
import datetime
import time
imp.reload(sys)
# 解除警告
requests.packages.urllib3.disable_warnings()
# 配置awvs的认证信息
# apikey = '1986ad8c0a5b3df4d7028d5f3c06e936ca2a0d10a2274410d8d637880f1e118ac'
# headers = {"X-Auth": apikey, "Content-type": "application/json;charset=utf8"}




def banner():
    # Initializes Colorama
    init(autoreset=True)
    print(Style.NORMAL + Fore.MAGENTA + f'{35 * "-"}AWVS自动批量添加任务，扫描，生成报告{34 * "-"}')
    print(Style.NORMAL + Fore.MAGENTA + f'{15 * " "}version:0.1 | made by yuanboss | date:2023/09/15{15 * " "}')
    print(Style.NORMAL + Fore.MAGENTA + f'{88 * "*"}')
    print(Style.NORMAL + Fore.MAGENTA + f'{40 * "-"}yuanboss{40 * "-"}')
    print(Style.NORMAL + Fore.MAGENTA + """ 
                                                   .o8                                   
                                                  "888                                   
    oooo    ooo oooo  oooo   .oooo.   ooo. .oo.    888oooo.   .ooooo.   .oooo.o  .oooo.o 
     `88.  .8'  `888  `888  `P  )88b  `888P"Y88b   d88' `88b d88' `88b d88(  "8 d88(  "8 
      `88..8'    888   888   .oP"888   888   888   888   888 888   888 `"Y88b.  `"Y88b.  
       `888'     888   888  d8(  888   888   888   888   888 888   888 o.  )88b o.  )88b 
        .8'      `V88V"V8P' `Y888""8o o888o o888o  `Y8bod8P' `Y8bod8P' 8""888P' 8""888P' 
    .o..P'                                                                               
    `Y8P'                                                                                                                                                                    
        """)
    print(Style.NORMAL + Fore.MAGENTA + f'{88 * "*"}')
    print(Style.NORMAL + Fore.MAGENTA + f'{40 * "-"}yuanboss{40 * "-"}')


# 提示
def tip():
    print(Style.NORMAL + Fore.YELLOW + """
    该工具是用于提升使用AWVS效率的，如果直接使用的话，需要手动在网站中一条条添加，
    该工具可以自动化添加任务，并且启动扫描，等扫描完成之后将会直接生成扫描报告并打印扫描报告地址
    使用帮助：
    python auto_awvs.py
    请输入AWVS的路径:https://localhost:3443/
    请输入apikey:1986ad8c0a5b3df4d7028d5f3c06e936ca2a0d10a2274410d8d637880f1e118ac
    请输入要扫描的地址，以英文逗号分隔:http://testphp.vulnweb.com/,http://www.testfire.net/
    """)


# 添加目标url，返回任务ID
def addTarget(targetUrl):
    api_url = url + '/api/v1/targets'
    try:
        data = {"address": targetUrl, "description": "awvs测试", "criticality": "10"}
        data_json = json.dumps(data)
        resp = requests.post(url=api_url, headers=headers, data=data_json, verify=False)
        target_id = resp.json().get("target_id")
        print(Style.NORMAL + Fore.BLUE + f'【已创建目标任务ID】:{target_id}')
    except Exception as e:
        print(str(e))
    return target_id


# 传入任务ID，开启扫描，返回扫描ID
def startScan(target_id):
    api_url = url + '/api/v1/scans'
    data = {
        "target_id": target_id,
        "profile_id": "11111111-1111-1111-1111-111111111115",
        "schedule":
            {
                "disable": False,
                "start_date": None,
                "time_sensitive": False
            }
    }

    data_json = json.dumps(data)
    try:
        resp = requests.post(url=api_url, headers=headers, data=data_json, verify=False)
        scan_id = resp.json()['scan_id']
        print(Style.NORMAL + Fore.BLUE + f'【已创建扫描任务ID】:{scan_id}')
        return scan_id
    except Exception as e:
        print(str(e))
        return


# 通过扫描ID，获取单个扫描状态
def getScanStatus(scanId):
    api_url = url + '/api/v1/scans/' + scanId
    try:
        resp = requests.get(api_url, headers=headers, verify=False)
        status = resp.json()['current_session']['status']
        return status
    except Exception as e:
        print(Style.NORMAL + Fore.RED + str(e))


# 查看Targets扫描队列
def getTargetsScanQueue():
    api_url = url + '/api/v1/targets'
    resp = requests.get(url=api_url, headers=headers, verify=False)
    print(resp.json())  # 返回结果为json格式
    return resp.json()


# 删除扫描任务
def delScan(scanId):
    api_url = url + '/api/v1/scans/' + scanId
    try:
        resp = requests.delete(api_url, headers=headers, verify=False)
        print(f'删除扫描任务成功【{scanId}】')
    except Exception as e:
        print(str(e))


# 获取scan_id和scan_session_id的字典列表
# 返回案例
"""
[
    {'scan_id': '45b700c7-8cf3-45aa-b64f-e27fd09af5d1', 'scan_session_id': '9d4a8fd3-221f-4cf1-8b6e-e80c1dd31d53'},
    {'scan_id': 'e480f3f6-158d-444b-8396-efe5f3b7339a', 'scan_session_id': '275567ff-a7a3-4f7e-908c-6d92e02a8cab'}
]
"""


def get_scanId_scanSessionId():
    api_url = url + '/api/v1/scans'
    # 存放scan_id，scan_session_id的dict对象
    listDict = []
    try:
        r = requests.get(url=api_url, headers=headers, verify=False)
        # print(r.content.decode())
        # 获取扫描任务数量
        count = len(r.json()['scans'])

        for i in range(count):
            subdict = dict()
            scan_id = r.json().get("scans")[i].get("scan_id")
            scan_session_id = r.json().get("scans")[i].get('current_session').get('scan_session_id')
            subdict.update({"scan_id": scan_id})
            subdict.update({"scan_session_id": scan_session_id})
            listDict.append(subdict)
    except Exception as e:
        print(str(e))
        return
    return listDict


# 获取所有扫描报告，返回扫描报告地址对象列表
def getAllScanReports():
    api_url = url + '/api/v1/reports'
    reportsList = []
    try:
        resp = requests.get(api_url, headers=headers, verify=False)
        count = resp.json()['pagination']['count']
        print(f'扫描报告总数:{count}')
        for i in range(count):
            subdict = dict()
            report_id = resp.json()['reports'][i]['report_id']
            html_download = url + resp.json()['reports'][i]['download'][0]
            pdf_download = url + resp.json()['reports'][i]['download'][1]
            subdict.update({'report_id': report_id})
            subdict.update({'html_download': html_download})
            subdict.update({'pdf_download': pdf_download})
            reportsList.append(subdict)
        for j in range(len(reportsList)):
            print(f'report_id:{reportsList[j]["report_id"]}\n'
                  f'html报告下载地址:{reportsList[j]["html_download"]}\n'
                  f'pdf报告下载地址:{reportsList[j]["pdf_download"]}')
        return reportsList
    except Exception as e:
        print(str(e))
        return

# 生成扫描报告
def generateScanReports(scanId):
    api_url = url + '/api/v1/reports'
    data = {"template_id": "11111111-1111-1111-1111-111111111112",
            "source": {
                "list_type": "scans",
                "id_list": [scanId]
            }
            }
    data_json = json.dumps(data)
    try:
        resp = requests.post(api_url, headers=headers, data=data_json, verify=False)
        print(Style.NORMAL + Fore.CYAN + f'正在生成扫描报告id：{resp.json()["report_id"]}')
        return resp.json()['report_id']
    except Exception as e:
        print(Style.NORMAL + Fore.RED + f'发生错误{e}')
        return

def getReportsMsg(report_id):
    api_url = url + '/api/v1/reports/' + report_id
    try:
        resp = requests.get(api_url, headers=headers, verify=False)
        report = resp.json()
        return report
    except Exception as e:
        print(str(e))

# 根据扫描ID获取扫描报告状态，然后生成指定的报告，将其输出到控制台,并返回报告ID列表
def getScanReportsIdList(scanIds):
    reportIdList = []
    scanIdsQueue = queue.Queue()
    for item in scanIds:
        scanIdsQueue.put(item)
    while not scanIdsQueue.empty():
        # 等带一定时间生成扫描报告
        time.sleep(1)
        scanId = scanIdsQueue.get()
        status = getScanStatus(scanId)
        if 'completed' == status:
            # 生成报告
            report_id = generateScanReports(scanId)
            reportIdList.append(report_id)
        else:
            scanIdsQueue.put(scanId)
    return reportIdList

# 导出
def download_report(reportIdList, typeId):
    reportIdQueue = queue.Queue()
    for item in reportIdList:
        reportIdQueue.put(item)
    while not reportIdQueue.empty():
        dateStr = time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime(time.time()))
        reportId = reportIdQueue.get()
        report = getReportsMsg(reportId)
        status = report['status']
        description = report['source']['description']
        if typeId == 0:
            report_name = dateStr + '.html'
        elif typeId == 1:
            report_name = dateStr + '.pdf'
        if 'completed' == status:
            print(Style.NORMAL + Fore.GREEN + f'{reportId}扫描报告生成完成......')
            # 下载
            print(Style.NORMAL + Fore.CYAN + f'正在下载报告{reportId}')
            report_url = url + report['download'][typeId]
            print(Style.NORMAL + Fore.LIGHTGREEN_EX + f"""
            下载地址为{report_url}
            """)
            resp = requests.get(url=report_url, headers=headers, verify=False)
            with open(report_name, "wb") as f:
                f.write(resp.content)
                f.close()
        else:
            reportIdQueue.put(reportId)



# 通过扫描ID，扫描sessionID，获取单个扫描概况信息
def getScanOverview(scan_id, scan_session_id):
    api_url = url + f'/api/v1/scans/{scan_id}/results/{scan_session_id}/statistics'
    try:
        resp = requests.get(api_url, headers=headers, verify=False)
    except Exception as e:
        print(str(e))
        return

    return resp.json()


# 单个扫描漏洞结果
def getVulnsResult(scan_id, scan_session_id):
    api_url = url + f'/api/v1/scans/{scan_id}/results/{scan_session_id}/vulnerabilities'
    try:
        resp = requests.get(api_url, headers=headers, verify=False)
    except Exception as e:
        print(str(e))
        return
    return resp.json()


# 添加任务列表并且扫描
def createTaskScan(targetUrlList):
    for targetUrl in range(len(targetUrlList)):
        # 创建任务
        target_id = addTarget(targetUrlList[targetUrl])
        # 开始扫描
        scan_id = startScan(target_id)


# 检查扫描状态并生成报告
def checkScanStatus():
    thread_name = threading.current_thread().name
    while not q.empty():
        scanId = q.get()
        status = getScanStatus(scanId)
        print(Style.NORMAL + Fore.YELLOW + f'扫描状态:{status}')
        while status != 'completed':
            print(f'{thread_name} 扫描任务ID：{scanId} 正在扫描......{status}')
            status = getScanStatus(scanId)
        print(Style.NORMAL + Fore.GREEN + f'{scanId} 扫描完成......')

        print(Style.NORMAL + Fore.MAGENTA + f'正在为{scanId} 生成报告......')
        generateScanReports(scanId)
    print(Style.NORMAL + Fore.GREEN + f'报告生成完成..........')





if __name__ == '__main__':
    threads = 2
    banner()
    tip()
    # url = 'https://localhost:3443/'
    # apikey = '1986ad8c0a5b3df4d7028d5f3c06e936ca2a0d10a2274410d8d637880f1e118ac'
    # input = 'http://testphp.vulnweb.com/,http://testphp.vulnweb.com/,http://www.testfire.net/,http://www.testfire.net/'
    url = input('请输入AWVS的路径:')
    apikey = input('请输入AWVS的apikey:')
    input = input('请输入要扫描的地址，以英文逗号分隔:')
    headers = {"X-Auth": apikey, "Content-type": "application/json;charset=utf8"}

    targetUrls = input.split(',')
    q = queue.Queue()
    scanIdList = []
    # 批量创建任务并扫描
    createTaskScan(targetUrls)
    # 获得scanId 与 scanSessionId
    list = get_scanId_scanSessionId()
    for m in range(len(list)):
        scan_id = list[m]['scan_id']
        scanIdList.append(scan_id)
    # 将scanId放入队列
    for n in range(len(scanIdList)):
        q.put(scanIdList[n])
    print(Style.NORMAL + Fore.YELLOW + f'已经创建{q.qsize()}个扫描任务')
    # 开启多线程监听扫描任务并在扫描完成之后生成报告
    for thread in range(threads):
        t = threading.Thread(target=checkScanStatus,name=f'线程{thread}')
        t.start()
        print(Style.NORMAL + Fore.YELLOW + f'线程{thread}开启，正在监听任务的扫描状态并生成扫描报告......')
    # 根据扫描ID监听报告状态，然后获取指定的报告，并将其存入列表中，最后将其输出到控制台
    reportIdList = getScanReportsIdList(scanIdList)
    download_report(reportIdList,0)