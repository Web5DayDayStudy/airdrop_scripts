import json
import os

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger

REPORT_NAME = "asdfund00"


def get_proxyip(proxy_str: str):
    arr = proxy_str.split('|')
    if len(arr) < 4:
        raise Exception("> 代理格式错误, 请检查格式是否为：ip|port|username|pwd")

    ip = arr[0]
    port = arr[1]
    username = arr[2]
    pwd = arr[3]

    proxy = f"socks5://{username}:{pwd}@{ip}:{port}"

    result = {
        "https": proxy,
        "http:": proxy
    }
    return result


def parse_txt_file(file_path):
    if not os.path.exists(file_path):
        logger.error(f"file '{file_path}' not found.")
        exit(1)
    with open(file_path, 'r', encoding='utf-8') as file:
        datas = file.readlines()

    datas = [data.strip() for data in datas if data.strip()]
    if len(datas) == 0:
        raise Exception("file data not found.")
    return datas


def report():
    logger.debug("================================= 开始上报OPI数据 ================================ ")
    names = parse_txt_file("./config.txt")
    for name in names:
        logger.debug(f"> 开始上报 name: {name}")
        do_report(name)
        logger.debug(f"> 上报完成 name: {name}")

    logger.debug("================================= 结束上报OPI数据 ================================ ")


def do_report(name):
    try:
        last_report_data = None
        # 获取区块上报信息
        last_reports_resp = requests.get(url="https://opi.network/api/get_last_reports")
        if last_reports_resp.ok:
            last_reports_json = last_reports_resp.json()
            if last_reports_json["error"] is False:
                last_report_data = last_reports_json.get("data")[0].get("report")

        # 替换name
        last_report_data["name"] = name
        r = requests.post(url="https://api.opi.network/report_block", json=last_report_data)
        if r.status_code == 200:
            logger.debug("> 上报成功！")
            return
        else:
            print("上报发生错误, status code: " + str(r.status_code))
    except Exception as e:
        logger.error(f"> 上报发生错误: {e}， name: {name}")


def scheduler_report():
    logger.debug(
        "================================= 启动上报OPI调度任务，将会在每10分钟执行一次 ================================ ")
    scheduler = BlockingScheduler()
    scheduler.add_job(report, 'cron', minute='*/10')
    scheduler.start()


if __name__ == '__main__':
    scheduler_report()
