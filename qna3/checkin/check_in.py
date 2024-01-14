from web3 import Web3
import json
import logging
#########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os

curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################
from qna3.common import qna3_util
from qna3.common.proxy_manager import ProxyPoolManager
from qna3.common.qna3_util import get_base_info

logging.basicConfig(level=logging.INFO)

CONTRACT = "0xb342e7d33b806544609370271a8d074313b7bc30"
INPUT_DATA = "0xe95a644f0000000000000000000000000000000000000000000000000000000000000001"


def retry_check_in(proxy_manager: ProxyPoolManager, trak_id: str, private_key: str):
    return qna3_util.retry_operation_with_logging(
        function=do_check_in,
        proxy_manager=proxy_manager,
        trak_id=trak_id,
        private_key=private_key
    )


# 签到
def do_check_in(proxy_manager: ProxyPoolManager, trak_id: str, private_key: str):
    logging.info(f'======================= start check in privateKey in : {private_key} ============================')

    # step1，构造公共请求头
    web3 = Web3(Web3.WebsocketProvider('wss://opbnb.publicnode.com'))
    address, headers, _ = get_base_info(proxy_manager=proxy_manager, trak_id=trak_id, private_key=private_key)

    # step2. 交互合约签到，返回txId
    chain_id = web3.eth.chain_id
    nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(address))
    tx_hash_id = qna3_util.exec_tx(address, CONTRACT, INPUT_DATA, nonce, chain_id, private_key, web3)

    # step3. 上报得分
    report_point(proxy_manager, trak_id, headers, tx_hash_id)

    return [address, tx_hash_id, private_key]


# 上报得分
def report_point(proxy_manager: ProxyPoolManager, trak_id: str, headers: dict, tx_hash_id):
    check_sign_response = proxy_manager.post('https://api.qna3.ai/api/v2/my/check-in', trak_id, data=json.dumps({
        'hash': tx_hash_id,
        'via': 'opbnb'
    }), headers=headers)
    if check_sign_response.status_code in [200, 201]:
        logging.info(f'req check in successful, json : {check_sign_response.json()}')
    else:
        logging.error(f'req check in fail, response : {check_sign_response.json()}')
