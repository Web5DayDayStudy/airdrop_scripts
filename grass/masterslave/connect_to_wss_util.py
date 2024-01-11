# -*- coding: utf-8 -*-

import asyncio
import random
import ssl
import json
import uuid
import time

from loguru import logger
from websockets_proxy import Proxy, proxy_connect


async def send_ping(websocket, device_id, user_id, socks5_proxy):
    while True:
        try:
            send_message = json.dumps({
                "device_id": device_id,
                "uid": user_id,
                "id": str(uuid.uuid4()),
                "version": "1.0.0",
                "action": "PING",
                "data": {}
            })
            logger.info(f"send_ping : {send_message}")
            await websocket.send(send_message)
            await asyncio.sleep(20)
        except asyncio.CancelledError:
            # 如果任务被取消，退出循环
            break
        except Exception as e:
            logger.error(f"send_ping 中发生错误: {e}, 代理：{socks5_proxy}, uid: {user_id}", exc_info=True)
            # 如果WebSocket连接关闭，则退出函数，以便重新连接
            if e.__class__.__name__ == 'ConnectionClosedError':
                logger.error("ConnectionClosedError")
                await websocket.close()
                break
            await asyncio.sleep(3)


async def send_pong(device_id, message, user_id, websocket):
    await websocket.send(json.dumps({"device_id": device_id, "uid": user_id, "id": message["id"],
                                     "origin_action": "PONG"}))


async def connect_to_wss(socks5_proxy, user_id):
    device_id = str(uuid.uuid3(uuid.NAMESPACE_DNS, socks5_proxy + ":" + user_id))
    logger.info(f"Load uid: {user_id}, proxy: {socks5_proxy}, device_id : {device_id}")

    while True:
        try:
            await asyncio.sleep(random.randint(1, 10) / 10)
            custom_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            }
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            uri = "wss://proxy.wynd.network:4650/"
            server_hostname = "proxy.wynd.network"
            proxy = Proxy.from_url(socks5_proxy)
            async with proxy_connect(uri, proxy=proxy, ssl=ssl_context, server_hostname=server_hostname,
                                     extra_headers=custom_headers) as websocket:
                task = asyncio.create_task(send_ping(websocket, device_id, user_id, socks5_proxy))
                while True:
                    response = await websocket.recv()
                    message = json.loads(response)
                    logger.debug(f"接收到服务端消息 -> message: {message}")
                    if message.get("action") == "AUTH":

                        await send_auth(custom_headers, device_id, message, user_id, websocket)

                    elif message.get("action") == "PONG":

                        await send_pong(device_id, message, user_id, websocket)

                await ping_task

        except Exception as e:
            logger.error(f"An error occurred: {e}, proxy: {socks5_proxy}, uid: {user_id}", exc_info=True)
        finally:
            await asyncio.sleep(5)  # 发生异常后5秒重试


async def send_auth(custom_headers, device_id, message, user_id, websocket):
    await websocket.send(json.dumps({
        "id": message["id"],
        "origin_action": "AUTH",
        "result": {
            "browser_id": device_id,
            "user_id": user_id,
            "user_agent": custom_headers['User-Agent'],
            "timestamp": int(time.time()),
            "device_type": "extension",
            "version": "2.5.0"
        }
    }))
