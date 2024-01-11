import asyncio

from master_slave_actuator import execute_tasks
from master_slave_config import MasterSlaveConfigManager


async def exec_master():
    print("=========== executor master =============")
    await execute_tasks(MasterSlaveConfigManager.get_config("master"))


async def exec_slave():
    print("=========== executor slave =============")
    await execute_tasks(MasterSlaveConfigManager.get_config("slave"))


async def process():
    tasks = [asyncio.ensure_future(exec_master()), asyncio.ensure_future(exec_slave())]
    await asyncio.gather(*tasks)


if __name__ == '__main__':
    asyncio.run(process())
