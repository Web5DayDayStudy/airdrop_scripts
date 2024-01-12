import json
import logging

import requests
from web3 import Web3

from qna3.common import qna3_util
from qna3.common.proxy_manager import ProxyPoolManager

CONTRACT = "0xb342e7d33b806544609370271a8d074313b7bc30"


def claim_point(proxy_manager: ProxyPoolManager, trak_id: str, private_key: str):
    # step1: 查询领取积分方法，查看我能领取多少分
    query_claim_point_url = "https://api.qna3.ai/api/v2/my/claim-all"
    address, headers = qna3_util.get_base_info(proxy_manager, trak_id, private_key)
    query_claim_point_response = proxy_manager.post(url=query_claim_point_url, trak_id=trak_id, headers=headers)
    logging.info(f'query claim point successful, json : {query_claim_point_response.json()}')

    nonce = None
    amount = None
    history_id = None
    signature = None
    if query_claim_point_response.status_code in [200, 201]:
        claim_response_data = query_claim_point_response.json()
        status_code = claim_response_data['statusCode']
        if status_code == 200:
            data = claim_response_data.get("data")
            if data:
                nonce = data['signature']['nonce']
                signature = data['signature']['signature']
                amount = data['amount']
                history_id = data['history_id']
        else:
            raise Exception("claim-all response is null, skip....")
    if nonce is None or amount is None or history_id is None or signature is None:
        logging.error("====== no points available for redemption were found，skip task！=======")
        return

    # step2：调用合约，领取积分
    # 签名数据
    web3 = Web3(Web3.HTTPProvider('https://binance.llamarpc.com'))
    chain_id = web3.eth.chain_id
    input_data = qna3_util.check_and_reset_input_data(build_input_data(amount, nonce, signature))
    tx_nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(address))
    tx_id = qna3_util.exec_tx(address, CONTRACT, input_data, tx_nonce, chain_id, private_key, web3)

    # step3：上报合约领取积分成功
    report_claim_point_url = f"https://api.qna3.ai/api/v2/my/claim/{history_id}"
    body = {
        "hash": tx_id
    }
    report_claim_point_response = proxy_manager.put(url=report_claim_point_url, trak_id=trak_id, data=json.dumps(body),
                                                    headers=headers)
    report_point_json = report_claim_point_response.json()
    logging.info(f'exec claim point successful, json : {report_point_json}')
    if report_claim_point_response.status_code in [200, 201]:
        if report_point_json["statusCode"] == 200:
            logging.info(f'claim point successful')
    else:
        raise Exception("claim point fail")
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
    claim_point("")
