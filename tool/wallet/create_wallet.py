import time

from eth_account import Account
from openpyxl import Workbook


def get_input_wallet_count():
    return input("输入的钱包数量为：")


def generate_wallet_info():
    global mnemonic, address, privateKey
    Account.enable_unaudited_hdwallet_features()
    # 创建账户，助记词
    account, mnemonic = Account.create_with_mnemonic()
    # 钱包地址
    address = account.address
    # 私钥
    privateKey = account.key.hex()

    return address, privateKey, mnemonic


if __name__ == '__main__':

    while True:
        walletCount = int(get_input_wallet_count())
        if walletCount < 1:
            print('>>> 钱包数量不能小于 1')
        else:
            break

    # 创建excel
    wb = Workbook()
    ws = wb.active

    # ws.append(['address', 'privateKey', 'mnemonic'])
    ws.append(['地址', '私钥', '助记词'])

    for i in range(walletCount):
        address, privateKey, mnemonic = generate_wallet_info()
        row = [address, privateKey, mnemonic]
        ws.append(row)

    # 保存文件
    wb.save('evm_wallet.xlsx')

    # 结束程序
    countdown = 3
    print('>>> 生成成功, 即将自动退出')
    while countdown > 0:
        print(f'{countdown} ...')
        time.sleep(1)
        countdown -= 1