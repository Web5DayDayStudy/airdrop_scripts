import time

from web3 import Web3
import requests
import json
import logging

from qna3.common import qna3_util
from qna3.common.qna3_util import get_base_info

logging.basicConfig(level=logging.INFO)

CONTRACT = "0xb342e7d33b806544609370271a8d074313b7bc30"
INPUT_DATA = "0xe95a644f0000000000000000000000000000000000000000000000000000000000000001"


# 签到
def do_check_in(private_key):
    logging.info(f'======================= start sign privateKey in : {private_key} ============================')

    # step1，构造公共请求头
    web3 = Web3(Web3.WebsocketProvider('wss://opbnb.publicnode.com'))
    address, headers = get_base_info(private_key)

    # me_req_url = 'https://api.qna3.ai/user/me'
    # me_response = requests.get(me_req_url, headers=headers)
    # if me_response.status_code in [200, 201]:
    #     me_response_data = me_response.json()
    #     logging.info(f'req get me successful, json : {me_response_data}')

    # step2. 交互合约签到，返回txId
    chain_id = web3.eth.chain_id
    nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(address))
    tx_hash_id = qna3_util.exec_tx(address, CONTRACT, INPUT_DATA, nonce, chain_id, private_key, web3)

    # step3. 上报得分
    report_point(headers, tx_hash_id)

    return [address, tx_hash_id, private_key]


# 上报得分
def report_point(headers, tx_hash_id):
    check_sign_response = requests.post('https://api.qna3.ai/api/v2/my/check-in', data=json.dumps({
        'hash': tx_hash_id,
        'via': 'opbnb'
    }), headers=headers)
    if check_sign_response.status_code in [200, 201]:
        logging.info(f'req check signIn successful, json : {check_sign_response.json()}')
    else:
        logging.error(f'sign fail, response : {check_sign_response.json()}')



