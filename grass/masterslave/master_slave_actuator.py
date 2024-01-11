# -*- coding: utf-8 -*-


import asyncio

from connect_to_wss_util import connect_to_wss
from master_slave_config import MasterSlaveConfigManager


def do_exec(config):
    socks5_proxys = config.socks5_proxys
    user_ids = config.user_ids

    # check
    if not socks5_proxys or not user_ids:
        raise ValueError("socks5_proxys or user_ids len is zero")

    tasks = []
    # 确定较大和较小的列表
    larger, smaller = (socks5_proxys, user_ids) if len(socks5_proxys) > len(user_ids) else (user_ids, socks5_proxys)
    multiple = len(larger) // len(smaller)
    remainder = len(larger) % len(smaller)

    def distribute_items(larger_list, smaller_list):
        dict = {}
        start_idx = 0
        for s_item in smaller_list:
            assigned_items = larger_list[start_idx:start_idx + multiple]
            dict[s_item] = assigned_items
            start_idx += multiple
        # 处理余数的情况
        for i in range(remainder):
            dict[smaller_list[i]].append(larger_list[start_idx + i])
        return dict

    mapping = distribute_items(larger, smaller)

    # 创建代理任务
    if len(socks5_proxys) > len(user_ids):
        # 代理数量超过用户ID数量的情况
        for user_id, proxy_list in mapping.items():
            for proxy in proxy_list:
                tasks.append(asyncio.create_task(connect_to_wss(proxy, user_id)))
    else:
        # 用户ID数量超过代理的情况
        for proxy, user_id_list in mapping.items():
            for user_id in user_id_list:
                tasks.append(asyncio.create_task(connect_to_wss(proxy, user_id)))

    return tasks


async def execute_tasks(config):
    tasks = do_exec(config)
    await asyncio.gather(*tasks)


async def main():
    await execute_tasks(MasterSlaveConfigManager.get_config("slave"))


if __name__ == '__main__':
    asyncio.run(main())
