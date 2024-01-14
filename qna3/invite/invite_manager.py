import logging
import uuid
import yaml
#########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os

curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################
from qna3.common import qna3_util
from qna3.common.proxy_manager import ProxyPoolManager

logging.basicConfig(level=logging.INFO)

file_path = os.path.join(curPath, 'qna3', 'resources', 'invite_config.yaml')
abs_file_path = os.path.abspath(file_path)


class InviteManager:
    def __init__(self, config_path=abs_file_path):
        self.config_path = config_path
        self.proxy = ProxyPoolManager()

    def get_config_data(self):
        with open(self.config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def invite(self):
        # 邀请信息
        infos = self.get_config_data().get("invite").get("infos")
        if infos is None or len(infos) == 0:
            raise Exception("invite infos can't be empty")

        for info in infos:
            self.process_invitation(info)

    def process_invitation(self, info):
        invite_private_key = info.get("invite_private_key")
        logging.info(f"====================== private key:{invite_private_key} 开始邀请 =======================")
        logging.info(f"=                                                                                     ")
        logging.info(f"=                                                                                     ")
        logging.info(f"=                                                                                     ")

        # 邀请人信息
        invite_address, _, invite_code = qna3_util.get_base_info(
            proxy_manager=self.proxy, trak_id=str(uuid.uuid4()), private_key=invite_private_key
        )
        logging.info(
            f">>>> 邀请人 address: {invite_address}, privateKey: {invite_private_key}, inviteCode: {invite_code}")

        # 接受邀请
        accept_private_keys = info.get("accept_private_keys")
        if accept_private_keys is None or len(accept_private_keys) == 0:
            raise Exception("accept_private_keys can't be empty")

        for accept_private_key in accept_private_keys:
            accept_address, _, _ = qna3_util.get_base_info(
                proxy_manager=self.proxy, trak_id=str(uuid.uuid4()), private_key=accept_private_key,
                invite_code=invite_code
            )
            logging.info(f">>>> 受邀请成功 接受人 address : {accept_address}, privateKey: {accept_private_key}")

        logging.info(f"=                                                                                     ")
        logging.info(f"=                                                                                     ")
        logging.info(f"=                                                                                     ")
        logging.info(f"====================== private key:{invite_private_key} 完成邀请 =======================")


if __name__ == '__main__':
    invite_manager = InviteManager()
    invite_manager.invite()
