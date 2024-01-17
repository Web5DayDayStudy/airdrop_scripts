import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import wraps


def retry(max_attempts=3, delay_between_attempts=1, exceptions=(Exception,)):
    """
    重试装饰器函数。

    参数:
        max_attempts: 最大尝试次数。
        delay_between_attempts: 两次尝试之间的延迟（秒）。
        exceptions: 需要重试的异常类型。
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempts += 1
                    logging.warning(f'Attempt {attempts} failed with error: {e}')
                    if attempts < max_attempts:
                        time.sleep(delay_between_attempts)
                    else:
                        logging.error(f'All {max_attempts} attempts failed. No more retries.')
                        raise

        return wrapper

    return decorator


def capture_error(error_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                current_utc_str = datetime.now().strftime('fail_%Y-%m-%d_') + error_type + '.json'
                # 收集入参作为错误参数
                key = kwargs.get('private_key', 'private_key')
                # 构造要写入的数据
                data = {'private_key': key, "error": str(e)}
                # 读取现有文件内容，如果文件不存在则创建一个空列表
                try:
                    with open(current_utc_str, 'r', encoding='utf-8') as file:
                        errors_list = json.load(file)
                except FileNotFoundError:
                    errors_list = []
                except json.JSONDecodeError:
                    errors_list = []
                # 将新的错误数据追加到列表中
                errors_list.append(data)
                # 将更新后的列表写回文件
                with open(current_utc_str, 'w', encoding='utf-8') as file:
                    json.dump(errors_list, file, ensure_ascii=False, indent=4)
                # 重新抛出异常
                raise

        return wrapper

    return decorator


# 异步任务装饰器
def _async(max_concurrency=3):
    semaphore = asyncio.Semaphore(max_concurrency)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            async with semaphore:
                return await func(*args, **kwargs)

        return wrapper

    return decorator


def to_async(max_workers=2):
    executor = ThreadPoolExecutor(max_workers=max_workers)

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            loop = asyncio.get_running_loop()
            # 使用 functools.partial 来传递额外参数
            from functools import partial
            func_partial = partial(func, *args, **kwargs)
            result = await loop.run_in_executor(executor, func_partial)
            return result

        return async_wrapper

    return decorator
