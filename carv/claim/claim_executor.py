import logging
import time
import uuid

#########################################################
#将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os
curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################

from carv.claim import claim
from carv.common.common_util import CommonUtil, ProxyPoolManager

logging.basicConfig(level=logging.INFO)

file_path = os.path.join(curPath, 'carv', 'common', 'resources', 'checkin_private_keys.txt')
abs_file_path = os.path.abspath(file_path)
private_keys = CommonUtil().parse_txt_file(abs_file_path)

proxy_manager = ProxyPoolManager()
retry_attempts = 3
retry_delay = 5
for private_key in private_keys:
    trak_id = str(uuid.uuid4())
    attempt = 0
    while attempt < retry_attempts:
        try:
            logging.info(" ")
            logging.info(" ")
            logging.info(" ")
            claim.claim_point(proxy=proxy_manager, trak_id=trak_id, private_key=private_key)
            logging.info(" ")
            logging.info(" ")
            logging.info(" ")
            break
        except Exception as e:
            logging.error(f"attempt {attempt + 1} failed with error: {e}")
            attempt += 1
            if attempt < retry_attempts:
                time.sleep(retry_delay)
            else:
                logging.error(f"all attempts to checkin have failed for private_key: {private_key}")
logging.info(" ALL EXEC IN SUCCESSFUL !")



