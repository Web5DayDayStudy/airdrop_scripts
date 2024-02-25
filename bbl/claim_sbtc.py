import os
import random
import string
import time

from loguru import logger

import requests

# 代理可以自己实现或者去买现成
def get_proxy(nstproxy_channel="xx", nstproxy_password="xx"):
    session = ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(10))
    return f"http://{nstproxy_channel}-residential-country_ANY-r_5m-s_{session}:{nstproxy_password}@gw-us.nstproxy.com:24125"


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


if __name__ == '__main__':
    address_list = parse_txt_file("./address.txt")
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0",
        "Connection": "keep-alive",
        "X-Requested-With": "XMLHttpRequest",
        "authority": "alt.signetfaucet.com",
        "method": "GET",
        "scheme": "https",
        "Referer": "https://alt.signetfaucet.com/",
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    for address in address_list:
        logger.info(f"加载钱包：{address}  .....")
        try:
            headers["path"] = f"/claim/?address={address}"
            proxy_url = get_proxy()
            proxies = {
                "http": proxy_url,
                "https": proxy_url,
            }
            url = f"https://alt.signetfaucet.com/claim/?address={address}"
            resp = requests.get(url=url, headers=headers, proxies=proxies)
            if resp.ok:
                resp_text = resp.text
                if "sent with txid" in resp_text:
                    tx_id = resp_text.split(" ")[-1]
                    logger.success(
                        f"地址：{address} 领取成功，txId：{tx_id}, 区块链浏览器：https://ex.signet.bublina.eu.org/t/{tx_id}")
                    continue
                logger.error(f"地址：{address} 领取失败，原因：{resp_text}")
            else:
                logger.error(f"地址：{address} 发送领取请求失败，原因: {resp.text}")
        except Exception as e:
            logger.error(f"发生异常：{e}")
