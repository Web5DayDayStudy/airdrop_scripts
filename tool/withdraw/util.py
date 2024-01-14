from configparser import ConfigParser, NoSectionError


def get_api_key():
    config = ConfigParser()
    config_file_path = 'config.ini'
    config.read(config_file_path, encoding='utf-8')

    # 检查 'profile' 部分和 'enable' 键是否存在
    if 'profile' not in config or 'enable' not in config['profile']:
        raise Exception("Missing 'enable' in 'profile' section in config.ini")

    enable_profile = config['profile']['enable']

    # 检查激活的配置是否存在
    if enable_profile not in config:
        raise NoSectionError(f"The profile '{enable_profile}' is not defined in config.ini")

    # 检查必要的键是否存在于选定的配置
    if "api_key" not in config[enable_profile] or "api_secret" not in config[enable_profile]:
        raise Exception(f"Missing 'api_key' or 'api_secret' in '{enable_profile}' profile in config.ini")

    return config[enable_profile]["api_key"], config[enable_profile]["api_secret"]


def get_withdrawal():
    config = ConfigParser()
    config_file_path = 'config.ini'
    config.read(config_file_path, encoding='utf-8')
    return config["withdraw"]["coin"], config["withdraw"]["network"], config["withdraw"]["amount"], config["withdraw"][
        "interval_time"]


if __name__ == '__main__':
    print(f"Api keys: {get_api_key()}")
    print(f"Withdrawal : {get_withdrawal()}")
