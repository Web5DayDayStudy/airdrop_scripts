#########################################################
#将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os
curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################
import base64
import itertools
import json
import logging
import os
import random
import time

import requests
from eth_account.messages import encode_defunct
from web3 import Web3


class CommonUtil():
    @staticmethod
    def exec_tx(_from, contract, input_data, nonce, chain_id, private_key, web3):
        contract_address = Web3.to_checksum_address(contract)
        # 估计gas
        estimated_gas = web3.eth.estimate_gas({
            'from': _from,
            'to': contract_address,
            'data': input_data
        })
        gas_limit = int(estimated_gas * 1.1)
        # gas_limit = estimated_gas
        logging.info(f'estimated gas: {estimated_gas}, with buffer: {gas_limit}')
        # 获取当前的gas价格
        gas_price = web3.eth.gas_price
        # logging.info(f'current gas price: {gas_price}')
        # 构造交易
        tx = {
            'from': _from,
            'to': contract_address,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'data': input_data,
            'chainId': chain_id
        }
        # 签名交易
        signed_tx = web3.eth.account.sign_transaction(tx, private_key)
        # 发送交易
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        receipt = None
        max_polling_attempts = 5
        delay_between_attempts = 3
        for attempt in range(max_polling_attempts):
            try:
                # 尝试获取交易收据
                time.sleep(delay_between_attempts)
                receipt = web3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    # 如果收据存在，则打印信息并退出循环
                    logging.info(f"transaction receipt found in attempt {attempt + 1}")
                    break
            except Exception as e:
                # 如果发生异常，则打印错误消息
                logging.info(f"attempt {attempt + 1} failed: {e}")
            # 如果没有找到收据，则等待指定的延迟时间
            logging.error(f"waiting for {delay_between_attempts} seconds before next attempt...")
            time.sleep(delay_between_attempts)
        tx_hash_id = receipt.transactionHash.hex()
        logging.info(f'transaction successful txId: {tx_hash_id}')
        return tx_hash_id

    """ 检查并修复input data """

    @staticmethod
    def check_and_reset_input_data(input_data):
        if not input_data.startswith('0x'):
            return '0x' + input_data
        elif input_data.count('0x') > 1:
            return '0x' + input_data.replace('0x', '')
        else:
            raise Exception("format input_data err")

    """ 解析文件 """

    @staticmethod
    def parse_txt_file(file_path):
        if not os.path.exists(file_path):
            logging.error(f"file '{file_path}' not found.")
            exit(1)
        with open(file_path, 'r') as file:
            datas = file.readlines()

        datas = [data.strip() for data in datas if data.strip()]
        if len(datas) == 0:
            raise Exception("file data not found.")
        return datas

    @staticmethod
    def login(proxy, trak_id: str, private_key: str, chain_url: str):
        logging.info(f'start getToken privateKey in : {private_key}')

        # 获取unique_text
        time_resp = proxy.get(trak_id=trak_id, url="https://worldtimeapi.org/api/timezone/etc/UTC")
        if time_resp.status_code in [200, 201]:
            unique_text = f'{time_resp.json()["unixtime"]}000'
        else:
            raise Exception("get unique_text fail")
        message_text = f"Hello! Please sign this message to confirm your ownership of the address. This action will not cost any gas fee. Here is a unique text: {unique_text}"

        # get signature_hex
        web3 = Web3(Web3.HTTPProvider(chain_url))
        message = encode_defunct(text=message_text)
        account = web3.eth.account
        signed_message = account.sign_message(message, private_key=private_key)

        # signature_hex and address
        signature_hex = signed_message.signature.hex()
        address = account.from_key(private_key).address

        # step2. get accessToken
        base_headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'X-App-Id': 'carv',
            'Origin': 'https://protocol.carv.io',
            'authority': 'interface.carv.io',
            'Referer': 'https://protocol.carv.io/'
        }
        access_token_data = {
            "signature": signature_hex,
            'wallet_addr': address,
            'text': message_text
        }
        auth_response = proxy.post('https://interface.carv.io/protocol/login',
                                   data=json.dumps(access_token_data),
                                   headers=base_headers)
        if auth_response.status_code in [200, 201]:
            auth_response_data = auth_response.json()
            logging.info(f'req login successful, json : {auth_response_data}')
            if auth_response_data['code'] == 0:
                token = auth_response_data['data']['token']
                authorization = base64.b64encode(f"eoa:{token}".encode('utf-8')).decode('utf-8')
                base_headers["Authorization"] = "bearer " + authorization
                return [address, base_headers]
            else:
                raise Exception("login fail")

    @staticmethod
    def login_with_retry(proxy, trak_id: str = None, private_key: str = None,
                         chain_url: str = None, max_retries=3, retry_delay=5):
        retries = 0
        while retries < max_retries:
            try:
                # 尝试执行 login 方法
                return CommonUtil().login(proxy, trak_id, private_key, chain_url)
            except Exception as e:
                retries += 1
                logging.error(f"Login attempt {retries} failed with error: {e}")
                if retries < max_retries:
                    # 在重试之前等待一段时间
                    time.sleep(retry_delay)
                else:
                    # 所有重试尝试都失败，抛出最后一个异常
                    raise


class ProxyPoolManager:
    def __init__(self):
        """

        :rtype: object
        """
        proxy_list = []
        file_path = os.path.join(curPath, 'carv', 'common', 'resources', 'socks5_proxys.txt')
        tmp_proxies = CommonUtil().parse_txt_file(file_path)
        # 解析成正确结构
        for proxy_str in tmp_proxies:
            arr = proxy_str.split('|')
            if len(arr) < 4:
                continue
            ip = arr[0]
            port = arr[1]
            username = arr[2]
            pwd = arr[3]
            proxy_list.append(f'socks5://{username}:{pwd}@{ip}:{port}')
        # 先打乱代理列表
        random.shuffle(proxy_list)
        # 然后创建迭代器
        self.proxy_pool = itertools.cycle(proxy_list)
        # 存储会话
        self.sessions = {}

    """ 该方法会使用不同代理来发送请求 """

    def get_proxy(self):
        return next(self.proxy_pool)  # 获取下一个代理

    def exec(self, url, method, data=None, headers=None):
        proxy = self.get_proxy()
        logging.info(f'请求：{url} 使用代理: {proxy}')
        proxies = {'http': proxy, 'https': proxy}
        try:
            if method == "get":
                return requests.get(url, data=data, headers=headers, proxies=proxies)
            if method == "post":
                return requests.post(url, data=data, headers=headers, proxies=proxies)
            if method == "put":
                return requests.put(url, data=data, headers=headers, proxies=proxies)
            if method == "delete":
                return requests.delete(url, data=data, headers=headers, proxies=proxies)
        except requests.exceptions.ProxyError as e:
            logging.info(f'代理错误: {e}')
            return None

    """ 该方法会使用同一个代理来发送请求 """

    def session_exec(self, trak_id, url, method, data=None, headers=None):
        # 获取或创建session
        session = self.get_session(trak_id)
        logging.info(f'任务ID: {trak_id} 请求：{url} 使用代理: {session.proxies["http"]}')
        try:
            if method == "get":
                return session.get(url, data=data, headers=headers)
            if method == "post":
                return session.post(url, data=data, headers=headers)
            if method == "put":
                return session.put(url, data=data, headers=headers)
            if method == "delete":
                return session.delete(url, data=data, headers=headers)
        except requests.exceptions.ProxyError as e:
            logging.info(f'任务ID: {trak_id} 代理错误: {e}')
            return None

    def get_session(self, tark_id):
        if tark_id is None:
            raise Exception("tark_id cannot be None")
        if tark_id not in self.sessions:
            # 如果tark_id不存在，创建一个新的session与之关联
            session = requests.Session()
            proxy = self.get_proxy()
            proxies = {'http': proxy, 'https': proxy}
            logging.debug(f">>> 请求执行代理为: {proxy}")
            session.proxies.update(proxies)
            self.sessions[tark_id] = session
        return self.sessions[tark_id]

    def get(self, url, trak_id=None, data=None, headers=None):
        if trak_id is None:
            return self.exec(url, "get", data, headers)
        return self.session_exec(trak_id, url, "get", data, headers)

    def post(self, url, trak_id=None, data=None, headers=None):
        if trak_id is None:
            return self.exec(url, "post", data, headers)
        return self.session_exec(trak_id, url, "post", data, headers)

    def put(self, url, trak_id=None, data=None, headers=None):
        if trak_id is None:
            return self.exec(url, "put", data, headers)
        return self.session_exec(trak_id, url, "put", data, headers)

    def delete(self, url, trak_id=None, data=None, headers=None):
        if trak_id is None:
            return self.session_exec(trak_id, url, "delete", data, headers)
        return self.exec(url, "delete", data, headers)


if __name__ == '__main__':
    print()
   # ProxyPoolManager()
