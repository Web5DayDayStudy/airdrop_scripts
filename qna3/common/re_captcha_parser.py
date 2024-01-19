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
from configparser import ConfigParser

import requests

logging.basicConfig(level=logging.INFO)


class ReCaptchaParser:
    def __init__(self):
        config = ConfigParser()
        config_file_path = '../resources/config.ini'
        config.read(config_file_path, encoding='utf-8')

        # 配置信息
        re_captcha_config = config["re_captcha"]
        self.site_key = re_captcha_config["site_key"]
        self.captcha_url = re_captcha_config["captcha_url"]
        self.api_key = re_captcha_config["api_key"]
        self.enable = bool(re_captcha_config.getboolean("enable", fallback=False))

    """
        获取token reCaptcha token
        @param action: 动作类型
    """

    def get_captcha_token(self, action: str):
        if not self.enable:
            return None
        create_task_body = {
            "clientKey": self.api_key,
            "task": {
                "type": "ReCaptchaV3TaskProxyless",
                "websiteURL": self.captcha_url,
                "websiteKey": self.site_key,
                "pageAction": action
            }
        }

        headers = {
            "Content-Type": "application/json"
        }

        logging.info(f"> 开始解析 ReCaptcha, action: [{action}] .....")
        try:
            create_task_resp = requests.post(url="https://api.ez-captcha.com/createTask",
                                             data=json.dumps(create_task_body), headers=headers)
            create_task_resp.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"> 创建ReCaptcha解析任务失败: {e}")

        if not create_task_resp.ok:
            raise Exception(f"> 创建ReCaptcha解析任务失败, 响应: {create_task_resp.text}")

        if create_task_resp.ok:
            print(create_task_resp.json())
            task_id = create_task_resp.json().get("taskId")

            time.sleep(3)

            status = ""
            headers = {'Content-Type': 'application/json'}
            max_retries = 10
            retry_count = 0

            while status != "ready":
                if retry_count >= max_retries:
                    raise Exception("> 解析ReCaptcha失败， 已经达到最大尝试失败次数.....")

                get_task_body = {
                    "clientKey": self.api_key,
                    "taskId": task_id
                }
                get_task_resp = requests.post(url="https://api.ez-captcha.com/getTaskResult",
                                              data=json.dumps(get_task_body),
                                              headers=headers)

                if get_task_resp.ok:
                    get_task_json = get_task_resp.json()
                    error_id = get_task_json.get("errorId")
                    status = get_task_json.get("status")

                    if status == "ready" and error_id == 0:
                        token = get_task_json.get("solution").get("gRecaptchaResponse")
                        logging.info(f"> 解析ReCaptcha成功，token: {token}")
                        return token
                    else:
                        logging.warning(
                            f"> 解析ReCaptcha任务尚未完成，将在1s后重试 Status: {status}, Error ID: {error_id}")

                else:
                    logging.error(f"> 获取ReCaptcha解析任务失败，Status Code: {get_task_resp.status_code}")
                time.sleep(1)
                retry_count += 1
            raise Exception(f"> 创建ReCaptcha解析任务失败, resp: {create_task_resp}")


if __name__ == '__main__':
    parser = ReCaptchaParser()
    token = parser.get_captcha_token("login")
    print(token)