#########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os

curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################
from web3 import Web3
import json
import logging
from qna3.common import qna3_util
from qna3.common.proxy_manager import ProxyPoolManager
from qna3.common.qna3_util import get_base_info
from qna3.common.re_captcha_parser import ReCaptchaParser

logging.basicConfig(level=logging.INFO)

CONTRACT = "0xb342e7d33b806544609370271a8d074313b7bc30"
INPUT_DATA = "0xe95a644f0000000000000000000000000000000000000000000000000000000000000001"


def retry_check_in(proxy_manager: ProxyPoolManager = None, captcha_parser: ReCaptchaParser = None, trak_id: str = None,
                   private_key: str = None):
    return qna3_util.retry_operation_with_logging(
        function=do_check_in,
        proxy_manager=proxy_manager,
        trak_id=trak_id,
        private_key=private_key,
        captcha_parser=captcha_parser
    )


# 签到
def do_check_in(proxy_manager: ProxyPoolManager, captcha_parser: ReCaptchaParser, trak_id: str, private_key: str):
    logging.info(f'======================= start check in privateKey in : {private_key} ============================')

    # 获取登录的人机验证token
    login_recaptcha = get_captcha_parser(captcha_parser)
    # step1，构造公共请求头
    web3 = Web3(Web3.WebsocketProvider('wss://opbnb.publicnode.com'))
    address, headers, _ = get_base_info(proxy_manager=proxy_manager, trak_id=trak_id,
                                        private_key=private_key, recaptcha=login_recaptcha)

    # step2 检查是否已经签到，如果已经签到就不用再次签到了
    checked = is_checkin(proxy_manager=proxy_manager, trak_id=trak_id, private_key=private_key, headers=headers)
    if checked:
        return address, "", private_key

    # step3. 交互合约签到，返回txId
    chain_id = web3.eth.chain_id
    nonce = web3.eth.get_transaction_count(Web3.to_checksum_address(address))

    # 签到的检查，需要调用validate接口
    checkin_recaptcha = validate_checkin(captcha_parser, headers, proxy_manager)

    tx_hash_id = qna3_util.exec_tx(address, CONTRACT, INPUT_DATA, nonce, chain_id, private_key, web3)
    # step4. 上报得分
    report_point(proxy_manager=proxy_manager, trak_id=trak_id, headers=headers, tx_hash_id=tx_hash_id,
                 private_key=private_key, checkin_recaptcha=checkin_recaptcha)

    return [address, tx_hash_id, private_key]


def get_captcha_parser(captcha_parser):
    login_recaptcha = None
    if captcha_parser.enable:
        login_recaptcha = captcha_parser.get_captcha_token("login")
    return login_recaptcha


def validate_checkin(captcha_parser, headers, proxy_manager):
    checkin_recaptcha = None
    if captcha_parser.enable:
        checkin_recaptcha = captcha_parser.get_captcha_token("checkin")
        checkin_validate_resp = proxy_manager.post(url=f'https://api.qna3.ai/api/v2/my/validate', headers=headers,
                                                   data=json.dumps({
                                                       "action": "checkin",
                                                       "recaptcha": checkin_recaptcha
                                                   }))
        if not checkin_validate_resp.ok:
            raise Exception(f"> 请求检查签到接口失败... resp: {checkin_validate_resp.text}")
        checkin_status_code = checkin_validate_resp.json().get("statusCode")
        if checkin_status_code != 200:
            raise Exception(f"> 验证签到接口失败... resp: {checkin_validate_resp.text}")
    return checkin_recaptcha


def is_checkin(proxy_manager: ProxyPoolManager, trak_id: str, private_key: str, headers: dict) -> bool:
    query_checkin_body = {
        "query": "query loadUserDetail($cursored: CursoredRequestInput!) {\n  userDetail {\n    checkInStatus {\n      checkInDays\n      todayCount\n    }\n    credit\n    creditHistories(cursored: $cursored) {\n      cursorInfo {\n        endCursor\n        hasNextPage\n      }\n      items {\n        claimed\n        extra\n        id\n        score\n        signDay\n        signInId\n        txHash\n        typ\n      }\n      total\n    }\n    invitation {\n      code\n      inviteeCount\n      leftCount\n    }\n    origin {\n      email\n      id\n      internalAddress\n      userWalletAddress\n    }\n    voteHistoryOfCurrentActivity {\n      created_at\n      query\n    }\n    ambassadorProgram {\n      bonus\n      claimed\n      family {\n        checkedInUsers\n        totalUsers\n      }\n    }\n  }\n}",
        "variables": {
            "cursored": {
                "after": "",
                "first": 20
            }
        }
    }
    query_checkin_resp = proxy_manager.post('https://api.qna3.ai/api/v2/graphql',
                                            trak_id,
                                            data=json.dumps(query_checkin_body),
                                            headers=headers)
    if query_checkin_resp.ok:
        today_check_in_count = query_checkin_resp.json().get("data").get("userDetail").get("checkInStatus").get(
            "todayCount")
        if today_check_in_count > 0:
            logging.info(f" >>>>>>>>>>>>>>>> 今日已经签到, 本次签到跳过 , private_key：{private_key} ")
            return True
    else:
        raise Exception(f"查询签到信息失败！private key : {private_key}")
    return False


# 上报得分
def report_point(proxy_manager: ProxyPoolManager, trak_id: str, headers: dict, tx_hash_id, private_key: str,
                 checkin_recaptcha: str):
    body = {
        'hash': tx_hash_id,
        'via': 'opbnb'
    }
    if checkin_recaptcha:
        body['recaptcha']: checkin_recaptcha

    check_sign_response = proxy_manager.post('https://api.qna3.ai/api/v2/my/check-in', trak_id, data=json.dumps(body),
                                             headers=headers)
    if check_sign_response.ok:
        logging.info(f' >>>>>>>>签到成功, json : {check_sign_response.json()}')
    else:

        fail_msg = f' >>>>>>>> 签到失败, trak_id: {trak_id}, private_key:{private_key} response : {check_sign_response.json()}'
        logging.error(fail_msg)
        qna3_util.record_failure_to_json(private_key=private_key, fail_msg=fail_msg)
