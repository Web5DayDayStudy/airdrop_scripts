import json
import os
from datetime import datetime, timezone

# 获取今天的日期
today = datetime.now().strftime('%Y-%m-%d')

# 文件路径
file_path = 'hex_values.json'

BASE_HEX = '000000000000000000000000000000000000000000000000000000000134d6f1'


def get_or_increment_value(date, file_path):
    # 检查文件是否存在
    if os.path.exists(file_path):
        # 读取JSON文件
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        # 文件不存在，创建一个空字典
        data = {}

    # 检查指定日期是否已经在数据中
    if date in data:
        # 日期存在，返回对应的值
        return data[date]
    else:
        # 获取最近的日期的字符串，如果数据为空，则使用当前日期
        if data:
            last_date_str = max(data.keys())
            last_hex = data[last_date_str]
        else:
            # 如果没有数据，那么我们无法比较日期，返回一个错误或默认值
            raise ValueError("No data available to increment from.")

        # 计算日期差异
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        now_date = datetime.strptime(date, '%Y-%m-%d').replace(tzinfo=timezone.utc)
        delta = (now_date - last_date).days

        # 定义一个函数来增加十六进制的值
        def increment_hex(hex_value, increment):
            # 移除前缀"0x"并转换为十进制，然后加上增量，再转换回十六进制
            new_value = hex(int(hex_value, 16) + increment).lstrip("0x")
            # 补充前导0以保持长度一致
            new_value = new_value.zfill(len(hex_value))
            return new_value

        # 在之前的last_hex之上增加日期差值
        new_value = increment_hex(last_hex, delta)
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
