import itertools
import random
#########################################################
#将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os
curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################

import requests
import logging

from qna3.common import qna3_util

logging.basicConfig(level=logging.INFO)

""" 请求代理池 """


class ProxyPoolManager:
    def __init__(self):
        """

        :rtype: object
        """
        proxy_list = []
        file_path = os.path.join(curPath, 'qna3', 'resources', 'socks5_proxys.txt')
        abs_file_path = os.path.abspath(file_path)
        tmp_proxies = qna3_util.parse_txt_file(abs_file_path)
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
    proxy_manager = ProxyPoolManager()
    for _ in range(3):
        response = proxy_manager.get(trak_id=1, url='https://www.baidu.com')
        if response:
            print(response.status_code)
        else:
            print("请求失败")
