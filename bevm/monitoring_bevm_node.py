import websocket
import json
import threading


def on_message(ws, message):
    data = json.loads(message)
    print("Received data:")
    print(data)
    # 在这里添加您的逻辑来处理数据并监控您的节点


def on_error(ws, error):
    print("Error:", error)


def on_close(ws):
    print("### Connection closed ###")


def on_open(ws):
    def run(*args):
        print("Connected to the Websocket service.")
        # 在这里可以发送任何必要的消息来初始化连接或订阅特定的数据
        # 例如: ws.send(json.dumps({"action": "subscribe", "channel": "node_updates"}))

    thread = threading.Thread(target=run)
    thread.start()


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://telemetry.bevm.io/feed",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.on_open = on_open
    ws.run_forever()
