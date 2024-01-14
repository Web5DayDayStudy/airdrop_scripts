#!/usr/bin/env python

#########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os

curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################
import json
import logging
import time
from binance.spot import Spot as Client
from binance.lib.utils import config_logging

from tool.withdraw.util import get_api_key, get_withdrawal

config_logging(logging, logging.INFO)
api_key, api_secret = get_api_key()
coin, network, amount, interval_time = get_withdrawal()
spot_client = Client(api_key, api_secret, show_header=True)


def do_withdraw():
    # read addresses
    with open("withdraw_addresses.json", "r") as fp:
        list_addresses = json.load(fp)
    logging.info(f"Finished reading list of addresses.")

    for address in list_addresses:
        logging.info(f"================== 开始提现 address: {address} ===========================")
        logging.info(" ")
        logging.info(" ")
        logging.info(" ")
        resp = spot_client.withdraw(coin=coin, amount=amount, network=network,
                                    address=address)
        data = resp.get("data")
        logging.info(f"resp: {data}")
        logging.info(" ")
        logging.info(" ")
        logging.info(" ")
        logging.info(f"================== 提现成功 address: {address} ===========================")
        time.sleep(int(interval_time))

    logging.info(f" 所有地址提现成功！ ")


if __name__ == '__main__':
    do_withdraw()
