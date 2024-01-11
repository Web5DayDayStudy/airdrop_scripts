import yaml
import threading


class MaterSlaveConfig:
    def __init__(self, real_config):
        self.socks5_proxys = []
        self.user_ids = []
        self.parse(real_config)

    def parse(self, real_config):
        self.user_ids = real_config.get('user_ids', [])
        simple_arrays = real_config.get('socks5_proxys_simple', [])
        tmp_socks5_proxys = []
        if simple_arrays:
            for proxy_str in simple_arrays:
                arr = proxy_str.split('|')
                if len(arr) < 4:
                    continue
                ip = arr[0]
                port = arr[1]
                username = arr[2]
                pwd = arr[3]
                tmp_socks5_proxys.append(f'socks5://{username}:{pwd}@{ip}:{port}')
            self.socks5_proxys = tmp_socks5_proxys
        else:
            self.socks5_proxys = real_config.get('socks5_proxys', [])


class MasterSlaveConfigManager:
    _configs = {}
    _lock = threading.Lock()

    @classmethod
    def get_config(cls, _type):
        with cls._lock:
            if _type not in cls._configs:
                try:
                    with open('master_slave_config.yaml', 'r', encoding='utf-8') as file:
                        config = yaml.safe_load(file)
                        real_config = config.get(_type)
                        if real_config is None:
                            raise ValueError("_type not found")
                        cls._configs[_type] = MaterSlaveConfig(real_config)
                except FileNotFoundError:
                    print("配置文件未找到")
                    raise
                except yaml.YAMLError as exc:
                    print("加载配置文件发生错误：", exc)
                    raise
            return cls._configs[_type]


# 使用示例
if __name__ == '__main__':
    def thread_function(_type):
        try:
            config = MasterSlaveConfigManager.get_config(_type)
            print(f"Config for {_type}: {config}")
        except Exception as e:
            print(f"Error in thread {_type}: {e}")


    thread1 = threading.Thread(target=thread_function, args=('one_to_one',))
    thread2 = threading.Thread(target=thread_function, args=('many_to_many',))
    thread3 = threading.Thread(target=thread_function, args=('many_to_many',))

    thread1.start()
    thread2.start()
    thread3.start()

    thread1.join()
    thread2.join()
    thread3.join()
