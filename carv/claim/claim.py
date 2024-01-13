import json
import logging

from carv.common.common_util import CommonUtil, ProxyPoolManager


def claim_point(proxy: ProxyPoolManager, private_key: str, trak_id: str):
    address, headers = CommonUtil().login_with_retry(proxy, trak_id=trak_id, private_key=private_key,
                                                     chain_url="https://opbnb-mainnet-rpc.bnbchain.org")

    logging.info(
        f"========================================== privateKey: {private_key} 开始领取积分 ======================================== ")
    logging.info(" ")
    logging.info(" ")
    logging.info(" ")
    # 查询奖励列表
    query_url = "https://interface.carv.io/airdrop/data_rewards/list"
    wait_claim_ids = []
    resp = proxy.get(url=query_url, headers=headers)
    if resp.status_code in [200, 201]:
        data = resp.json()
        if data['code'] == 0:
            data_rewards = data.get('data').get('data_rewards')
            if data_rewards:
                for reward in data_rewards:
                    reward_id = reward.get('id')
                    wait_claim_ids.append(reward_id)

    # 领取奖励
    claim_url = "https://interface.carv.io/airdrop/data_rewards/claim"
    if wait_claim_ids:
        for claim_id in wait_claim_ids:
            data = {
                "id": claim_id
            }
            claim_resp = proxy.post(url=claim_url, headers=headers, trak_id=trak_id, data=json.dumps(data))
            if claim_resp.status_code in [200, 201]:
                logging.info(f" claim claim_id : {claim_id} successful")
    logging.info(" ")
    logging.info(" ")
    logging.info(" ")
    logging.info(
        f"========================================== privateKey: {private_key} 完成领取积分 ======================================== ")
