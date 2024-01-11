import time

from web3 import Web3
from eth_account.messages import encode_defunct
import requests
import json
import logging
import base64

# ronin，opbnb，zkSync，linea
chain_ids = [
    2020,
    204,
    324,
    59144
]

logging.basicConfig(level=logging.INFO)

private_key = ""


def get_token(private_key):
    logging.info(f'======================= start getToken privateKey in : {private_key} ============================')

    # 获取unique_text
    time_resp = requests.get("https://worldtimeapi.org/api/timezone/etc/UTC")
    if time_resp.status_code in [200, 201]:
        unique_text = f'{time_resp.json()["unixtime"]}000'
    else:
        raise Exception("get unique_text fail")
    message_text = f"Hello! Please sign this message to confirm your ownership of the address. This action will not cost any gas fee. Here is a unique text: {unique_text}"

    # get signature_hex
    web3 = Web3()
    message = encode_defunct(text=message_text)
    account = web3.eth.account
    signed_message = account.sign_message(message, private_key=private_key)

    # signature_hex and address
    signature_hex = signed_message.signature.hex()
    address = account.from_key(private_key).address

    # step2. get accessToken
    base_headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'X-App-Id': 'carv',
        'Origin': 'https://protocol.carv.io',
        'authority': 'interface.carv.io',
        'Referer': 'https://protocol.carv.io/'
    }
    access_token_data = {
        "signature": signature_hex,
        'wallet_addr': address,
        'text': message_text
    }
    auth_response = requests.post('https://interface.carv.io/protocol/login',
                                  data=json.dumps(access_token_data),
                                  headers=base_headers)
    if auth_response.status_code in [200, 201]:
        auth_response_data = auth_response.json()
        logging.info(f'req login successful, json : {auth_response_data}')
        if auth_response_data['code'] == 0:
            token = access_token = auth_response_data['data']['token']
            logging.info(f'access_token: {access_token}')
            return [token, base_headers]
        else:
            raise Exception("login fail")


def mint_carv_soul(chain_id, private_key):
    (token, base_headers) = get_token(private_key)
    authorization = base64.b64encode(f"eoa:{token}".encode('utf-8')).decode('utf-8')
    base_headers["Authorization"] = "bearer " + authorization
    mint_data = {
        "chain_id": chain_id
    }
    mint_response = requests.post('https://interface.carv.io/airdrop/mint/carv_soul',
                                  data=json.dumps(mint_data),
                                  headers=base_headers)
    mint_result_json = mint_response.json()
    logging.info(f'mint_result_json, json : {mint_result_json}')
    if mint_response.status_code in [200, 201]:
        if mint_result_json["code"] == 0:
            logging.info(f'mint chain_id {chain_id} successful, json : {mint_response.json()}')
        else:
            raise Exception(f"mint chain_id fail : {chain_id}")


# 检查
def check_status():
    url = "https://interface.carv.io/airdrop/check_carv_status?chain_id=2020"
    print('Checking status')


if __name__ == '__main__':
    mint_carv_soul(2020, private_key)
