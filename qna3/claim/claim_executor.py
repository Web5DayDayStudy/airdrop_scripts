import logging
import uuid
#########################################################
#将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os
curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################
from qna3.claim import claim_point
from qna3.common import qna3_util
from qna3.common.proxy_manager import ProxyPoolManager

logging.basicConfig(level=logging.DEBUG)


file_path = os.path.join(curPath, 'qna3', 'resources', 'claim_private_keys.txt')
abs_file_path = os.path.abspath(file_path)
private_keys = qna3_util.parse_txt_file(abs_file_path)

proxy_manager = ProxyPoolManager()
for private_key in private_keys:
    trak_id = uuid.uuid4()
    logging.info(f"executing claim in private key: '{private_key}'")
    (address, tx_hash_id, new_private_key) = claim_point.claim_point(proxy_manager, str(trak_id), private_key)
    logging.info("==================================== CLAIM IN SUCCESS ===============================================")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info(f'CLAIM SUCCESSFUL, ADDRESS: {address}, PRIVATE_KEY: {private_key}, TX_HASH_ID: {tx_hash_id}')
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("==================================== CLAIM IN SUCCESS ===============================================")


logging.info(" ALL EXEC IN SUCCESSFUL !")