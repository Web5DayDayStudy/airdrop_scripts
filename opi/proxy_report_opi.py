import json

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger



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


def report():
    logger.debug("================================= 开始上报OPI数据 ================================ ")
    with open('./config.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.debug(f"> 等待上报数据数量: {len(data)}")
    for name, proxyip in data.items():
        proxy = get_proxyip(proxyip)
        logger.debug(f"> 开始上报 name: {name}, 代理: {proxy}")
        do_report(name, proxy)
        logger.debug(f"> 上报完成 name: {name}, IP: {proxy}")

    logger.debug("================================= 结束上报OPI数据 ================================ ")


def do_report(name, proxies):
    try:
        last_report_data = None
        # 获取区块上报信息
        last_reports_resp = requests.get(url="https://opi.network/api/get_last_reports", proxies=proxies)
        if last_reports_resp.ok:
            last_reports_json = last_reports_resp.json()
            if last_reports_json["error"] is False:
                last_report_data = last_reports_json.get("data")[0].get("report")

        # 替换name
        last_report_data["name"] = name
        r = requests.post(url="https://api.opi.network/report_block", json=last_report_data, proxies=proxies)
        if r.status_code == 200:
            logger.debug("> 上报成功！")
            return
        else:
            print("上报发生错误, status code: " + str(r.status_code))
    except Exception as e:
        logger.error(f"> 上报发生错误: {e}， name: {name}, IP: {proxies}")


def scheduler_report():
    logger.debug(
        "================================= 启动上报OPI调度任务，将会在每10分钟执行一次 ================================ ")
    scheduler = BlockingScheduler()
    scheduler.add_job(report, 'cron', minute='*/10')
    scheduler.start()


if __name__ == '__main__':
    scheduler_report()
