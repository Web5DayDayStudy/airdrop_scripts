import uuid

import check_in
import logging

from qna3.common import qna3_util
from qna3.common.proxy_pool import ProxyPoolManager

logging.basicConfig(level=logging.DEBUG)

private_keys = qna3_util.parse_txt_file("../resources/checkin_private_keys.txt")
proxy_manager = ProxyPoolManager()

for private_key in private_keys:
    trak_id = uuid.uuid4()
    logging.info(f"executing check in private key: '{private_key}'")
    (address, tx_hash_id, new_private_key) = check_in.do_check_in(proxy_manager, str(trak_id), private_key)
    logging.info("==================================== CHECK IN SUCCESS ===============================================")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info(f'CHECK IN SUCCESSFUL, ADDRESS: {address}, PRIVATE_KEY: {private_key}, TX_HASH_ID: {tx_hash_id}')
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("==================================== CHECK IN SUCCESS ===============================================")

logging.info(" ALL EXEC SUCCESSFUL !")


if __name__ == '__main__':
    print(str(uuid.uuid4()))