from web3 import Web3
import json
import logging

from carv.common.common_util import CommonUtil, ProxyPoolManager
from carv.common.annotation import retry, capture_error, to_async

# ronin，opbnb，zkSync，linea
chain_arr = [
    {
        "id": 2020,
        "url": "",
        "contract": "",
        "name": "Ronin"
    },
    {
        "id": 204,
        "url": "https://opbnb-mainnet-rpc.bnbchain.org",
        "contract": "0xc32338e7f84f4c01864c1d5b2b0c0c7c697c25dc",
        "name": "opBNB"
    },
    # {
    #     "id": 324,
    #     "url": "https://mainnet.era.zksync.io",
    #     "contract": "0x5155704bb41fde152ad3e1ae402e8e8b9ba335d3",
    #     "name": "zkSync Era"
    # },
    # {
    #     "id": 59144,
    #     "url": "https://binance.llamarpc.com",
    #     "contract": "0xc32338e7f84f4c01864c1d5b2b0c0c7c697c25dc",
    #     "name": "Linea"
    # }
]

logging.basicConfig(level=logging.INFO)


# 检查
def check_status(proxy: ProxyPoolManager, trak_id: str, chain_id: str, headers: dict):
    url = f"https://interface.carv.io/airdrop/check_carv_status?chain_id={chain_id}"
    resp = proxy.get(url=url, trak_id=trak_id, headers=headers)
    if resp.status_code in [200, 201]:
        data = resp.json()
        # logging.info(f'req check_status successful, resp : {data}')
        if data['code'] == 0 and data['data']['status'] == 'not_started':
            return True
        logging.error(f'链ID：{chain_id} 已经签到')
        return False


### input_data的参数参考

# 0xa2a9539c - functionName
# 00000000000000000000000004babbd2cb77bc47ff32a78396d70bb33d26dbf3 - 钱包地址
# 0000000000000000000000000000000000000000000000000000000000000032 - 金额
# 000000000000000000000000000000000000000000000000000000000134d6f0 - 动态变化的，目前看来是每天+1
# 0000000000000000000000000000000000000000000000000000000000000080 - 固定
# 0000000000000000000000000000000000000000000000000000000000000041 - 固定
# 550dd7a34150c3d9d4a9948a5001214906eb0854c85dcf2acae85a5debd04bd67f174e358552c47008524b0fba693d1537700b6f1b877acf2a58197d20eb0d0f1c - 签名
# 00000000000000000000000000000000000000000000000000000000000000 - 固定


def build_input_data(amount, address, signature, dynamic_hex):
    # 获取今天的动态部分
    return ("0xa2a9539c"
            f"{address[2:].zfill(64)}"
            f"{f'{hex(amount)[2:].zfill(64)}'}"
            f"{dynamic_hex}"
            f"0000000000000000000000000000000000000000000000000000000000000080"
            f"0000000000000000000000000000000000000000000000000000000000000041"
            f"{signature}"
            f"00000000000000000000000000000000000000000000000000000000000000")


@retry(delay_between_attempts=3)
def checkin_carv_soul(proxy: ProxyPoolManager, trak_id: str, chain_info: dict, private_key: str, dynamic_hex: str,
                      address, headers):
    chain_id = chain_info.get("id")

    # 检查是否能领取
    can_checkin = check_status(proxy=proxy, trak_id=trak_id, chain_id=chain_id, headers=headers)
    if can_checkin is False:
        return address, "", private_key

    carv_soul_url = 'https://interface.carv.io/airdrop/mint/carv_soul'
    body = {
        'chain_id': chain_id
    }

    # 获取签到需要的信息
    resp = proxy.post(url=carv_soul_url, headers=headers, data=json.dumps(body))
    amount = None
    signature = None
    if resp.status_code in [200, 201]:
        json_data = resp.json()
        amount = json_data.get("data").get("permit").get("amount")
        signature = json_data.get("data").get("signature")

    if chain_id == 2020:
        # Ronin不需要和链上交互
        logging.info(f'Ronin skip tx ......')
        return address, "", private_key

    if amount is None or signature is None:
        raise Exception("signature and amount can't be None")

    input_data = CommonUtil().check_and_reset_input_data(build_input_data(amount=amount, signature=signature,
                                                                          address=address, dynamic_hex=dynamic_hex))
    web3 = Web3(Web3.HTTPProvider(chain_info.get("url")))
    temp_address = Web3.to_checksum_address(address)
    nonce = web3.eth.get_transaction_count(temp_address)

    tx_hash_id = CommonUtil().exec_tx(_from=address, contract=chain_info.get("contract"), input_data=input_data,
                                      nonce=nonce,
                                      chain_id=chain_id,
                                      private_key=private_key, web3=web3)
    return address, tx_hash_id, private_key


@to_async(max_workers=2)
@capture_error(error_type="carv-ceckin")
def checkin_all(proxy: ProxyPoolManager, trak_id: str, private_key: str, dynamic_hex: str):
    logging.info(
        f" ========================================= 开始签到： privateKey {private_key} ========================================= ")
    logging.info(f" ")
    logging.info(f" ")
    logging.info(f" ")
    # 登录放到外边，不然循环登录没必要
    address, headers = CommonUtil().login_with_retry(proxy=proxy, trak_id=trak_id, private_key=private_key,
                                                     chain_url="https://opbnb-mainnet-rpc.bnbchain.org")
    logging.info(f">>>>>>>>>>> 完成登录 privateKey: {private_key}， address: {address}")
    for china_info in chain_arr:
        address, tx_hash_id, _private_key = checkin_carv_soul(proxy=proxy, trak_id=trak_id, chain_info=china_info,
                                                              private_key=private_key, dynamic_hex=dynamic_hex,
                                                              address=address, headers=headers)
        logging.info(
            f">>>>>>>>>> address: {address} chinaName: {china_info.get('name')}, tx: {tx_hash_id} checkin successful <<<<<<<<<<<<<")
    logging.info(f" ")
    logging.info(f" ")
    logging.info(f" ")
    logging.info(
        f" ========================================= 完成签到： privateKey {private_key} ========================================= ")


if __name__ == '__main__':
    pass
