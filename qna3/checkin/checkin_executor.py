import asyncio
import uuid
from concurrent.futures import ThreadPoolExecutor

import check_in
import logging
#########################################################
# 将根目录加入sys.path中,解决命令行找不到包的问题
import sys
import os

from qna3.common.re_captcha_parser import ReCaptchaParser

curPath = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(curPath)
#########################################################
from qna3.common import qna3_util
from qna3.common.proxy_manager import ProxyPoolManager

logging.basicConfig(level=logging.DEBUG)

executor = ThreadPoolExecutor()


async def run_blocking_io(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


async def check_in_coroutine(semaphore, proxy_manager, private_key, captcha_parser):
    async with semaphore:
        trak_id = uuid.uuid4()
        logging.info(f"executing check in private key: '{private_key}'")
        # 在线程池中运行同步函数
        address, tx_hash_id, new_private_key = await run_blocking_io(
            check_in.retry_check_in, proxy_manager, captcha_parser, str(trak_id), private_key
        )
        logging.info(
            "==================================== CHECK IN SUCCESS ===============================================")
        logging.info(f'CHECK IN SUCCESSFUL, ADDRESS: {address}, PRIVATE_KEY: {private_key}, TX_HASH_ID: {tx_hash_id}')
        logging.info(
            "==================================== CHECK IN SUCCESS ===============================================")


async def main():
    file_path = os.path.join(curPath, 'qna3', 'resources', 'checkin_private_keys.txt')
    abs_file_path = os.path.abspath(file_path)
    private_keys = qna3_util.parse_txt_file(abs_file_path)
    proxy_manager = ProxyPoolManager()
    captcha_parser = ReCaptchaParser()

    semaphore = asyncio.Semaphore(1)

    # 创建并启动协程列表
    tasks = [check_in_coroutine(semaphore=semaphore, proxy_manager=proxy_manager, private_key=private_key,
                                captcha_parser=captcha_parser) for private_key in private_keys]
    await asyncio.gather(*tasks)

    logging.info(" ALL EXEC SUCCESSFUL !")


asyncio.run(main())
