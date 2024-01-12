import logging
import uuid

from qna3.claim import claim_point
from qna3.common import qna3_util
from qna3.common.proxy_pool import ProxyPoolManager

logging.basicConfig(level=logging.DEBUG)


private_keys = qna3_util.parse_txt_file("claim_private_keys")

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