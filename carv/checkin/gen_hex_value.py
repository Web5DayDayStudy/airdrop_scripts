import json
import os
from datetime import datetime, timedelta

# 获取今天的日期
today = datetime.now().strftime('%Y-%m-%d')

# 文件路径
file_path = 'hex_values.json'

BASE_HEX = '000000000000000000000000000000000000000000000000000000000134d6f1'


def increment_hex(hex_value):
    # 将十六进制字符串转换为十进制整数，增加1，然后转换回十六进制字符串
    return '{:0{}x}'.format(int(hex_value, 16) + 1, len(hex_value))


def get_or_increment_value(date, file_path):
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 读取JSON文件
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        # 文件不存在，创建一个空字典
        data = {}

    # 检查今天的日期是否在数据中
    if date in data:
        # 日期存在，返回对应的值
        return data[date]
    else:
        # 获取昨天的日期
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        # 获取昨天的值，如果昨天的值不存在，则从初始值开始
        previous_value = data.get(yesterday, BASE_HEX)
        # 增加1
        new_value = increment_hex(previous_value)
        # 更新数据字典
        data[date] = new_value
        # 将更新后的数据写回文件
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        return new_value


def gen():
    # 使用函数并打印结果
    value = get_or_increment_value(today, file_path)
    print(f"Gen hex value for {today}: {value}")
    return value

if __name__ == '__main__':
    gen()
