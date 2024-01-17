import asyncio
import logging
import uuid
#########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os

curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################
from carv.common.common_util import CommonUtil, ProxyPoolManager
from carv.checkin import checkin, gen_hex_value

logging.basicConfig(level=logging.DEBUG)

file_path = os.path.join(curPath, 'carv', 'common', 'resources', 'checkin_private_keys.txt')
abs_file_path = os.path.abspath(file_path)
private_keys = CommonUtil().parse_txt_file(abs_file_path)

proxy_manager = ProxyPoolManager()
# 初始化今天的hexValue
dynamic_hex = gen_hex_value.gen()


async def main():
    tasks = []
    for private_key in private_keys:
        trak_id = str(uuid.uuid4())
        task = checkin.checkin_all(proxy=proxy_manager, trak_id=trak_id, private_key=private_key,
                                   dynamic_hex=dynamic_hex)
        tasks.append(task)

    await asyncio.gather(*tasks)

    logging.info(" ALL EXEC IN SUCCESSFUL !")


if __name__ == '__main__':
    asyncio.run(main())
