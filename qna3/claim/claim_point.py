import json
import logging

import requests
from web3 import Web3

from qna3.common import qna3_util

CONTRACT = "0xb342e7d33b806544609370271a8d074313b7bc30"

def claim_point(private_key):
    # step1: 查询领取积分方法，查看我能领取多少分
    query_claim_point_url = "https://api.qna3.ai/api/v2/my/claim-all"
    address, headers = qna3_util.get_base_info(private_key)
    query_claim_point_response = requests.post(query_claim_point_url, headers=headers)
    logging.info(f'query claim point successful, json : {query_claim_point_response.json()}')

    nonce = None
    amount = None
    history_id = None
    signature = None
    if query_claim_point_response.status_code in [200, 201]:
        claim_response_data = query_claim_point_response.json()
        status_code = claim_response_data['statusCode']
        if status_code == 200:
            nonce = claim_response_data['data']['signature']['nonce']
            signature = claim_response_data['data']['signature']['signature']
            amount = claim_response_data['data']['amount']
            history_id = claim_response_data['data']['history_id']
        else:
            raise Exception("query claim point info fail")
    if nonce is None or amount is None or history_id is None or signature is None:
        raise Exception(f"query point param fail, params is None. nonce: {nonce}, amount: {amount}, "
                        f"history_id: {history_id}, signature: {signature}")

    # step2：调用合约，领取积分
    # 签名数据
    web3 = Web3(Web3.HTTPProvider('https://binance.llamarpc.com'))
    chain_id = web3.eth.chain_id
    # nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(address))
    input_data = qna3_util.check_and_reset_input_data(build_input_data(amount, nonce, signature))
    tx_id = qna3_util.exec_tx(address, CONTRACT, input_data, nonce, chain_id, private_key, web3)
    # step3：上报合约领取积分成功
    report_claim_point_url = f"https://api.qna3.ai/api/v2/my/claim/{history_id}"
    report_claim_point_response = requests.post(report_claim_point_url, headers=headers)
    report_point_json = report_claim_point_response.json()
    logging.info(f'exec claim point successful, json : {report_point_json}')
    if report_claim_point_response.status_code == 200 or report_claim_point_response.status_code == 201:
        if report_point_json["statusCode"] == 200:
            logging.info(f'report claim point successful')
        else:
            raise Exception("report claim point fail")
    return address, private_key, tx_id


### input_data的参数参考
# 0x624f82f5 - functionName
# 000000000000000000000000000000000000000000000000000000000000000e -金额(64位)
# 00000000000000000000000000000000000000000000000000000000000f5836 - nonce(64位)
# 0000000000000000000000000000000000000000000000000000000000000060 - 固定(64位)
# 0000000000000000000000000000000000000000000000000000000000000041 - 固定(64位)
# 9d7738b50579134ee69d7a578942dcd8bb5bd00f9d2359439bc7034d61c6c37a34f8f9d997303be9271e7b52f0953aa36dfb06c07dd44707a30c0c786f2033641c - 签名(128位)
# 00000000000000000000000000000000000000000000000000000000000000 - 固定
def build_input_data(amount, nonce, signature):
    return (f"0x624f82f5{f'{hex(amount)[2:].zfill(64)}'}"
            f"{f'{hex(nonce)[2:].zfill(64)}'}"
            f"0000000000000000000000000000000000000000000000000000000000000060"
            f"0000000000000000000000000000000000000000000000000000000000000041"
            f"{signature}"
            f"00000000000000000000000000000000000000000000000000000000000000")


if __name__ == '__main__':
    web3 = Web3(Web3.HTTPProvider('https://binance.llamarpc.com'))
    tx = web3.eth.get_transaction("")
    print(json.dumps(tx))
    #claim_point("")
