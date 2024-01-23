import json
import time

from fabric import Connection, task

from configparser import ConfigParser


@task
def uname(c):
    result = c.run('uname -a')
    print_result(result)


def print_result(result):
    print("服务器 {} 返回结果：\n{}".format(c.host, result.stdout.strip()))


# 安装docker环境
@task
def install_docker(con):
    filename = "docker_install.sh"

    print(f"开始创建 {filename} 文件...")

    file_content = """
        #!/bin/bash
        sudo apt-get update
        sudo apt-get install -y docker.io
        sudo systemctl start docker
        sudo systemctl enable docker
        sudo usermod -aG docker $USER
    """

    crate_file_result = con.run(f'echo "{file_content}" > {filename}')
    print(crate_file_result)

    print(f"文件 {filename} 已经创建...")

    print("开始安装docker...")
    con.run(f'chmod +x {filename}')
    time.sleep(2)
    con.run(f'sh {filename}')
    print("安装docker完毕...")


# 启动bevm docker 容器
@task
def start_bevm_node(con, address):
    # --bootnodes /ip4/18.222.166.234/tcp/10000/ws/p2p/12D3KooWR1DNEVVWMaRJVfAkXTyZAZgnN159hNcPTooCSwMv4zbx
    print("开始启动docker bevm node节点...")
    command = (
        f'sudo docker run -d --name "{address}" -v $HOME/node_bevm_test_storage:/root/.local/share/bevm btclayer2/bevm:v0.1.1 bevm "--chain=testnet" "--name={address}" '
        f'"--pruning=archive" --telemetry-url "wss://telemetry.bevm.io/submit 0" --bootnodes /ip4/18.222.166.234/tcp/10000/ws/p2p/12D3KooWR1DNEVVWMaRJVfAkXTyZAZgnN159hNcPTooCSwMv4zbx')
    print(f"启动命令为：{command}")
    con.run(command)
    print("docker容器已经启动...")


# 查看docker日志
def showlog(con, address):
    command = f"docker logs -f {address}"
    con.run(command)


def getdata():
    with open('./address.json', 'r', encoding='utf-8') as file:
        return json.load(file)


def do_exec():
    data, password, username = get_infos()
    for address, host in data.items():
        con = Connection(host=host,
                         user=username,
                         connect_kwargs={"password": password})
        print(f">> 开始处理地址：{address}")
        install_docker(con)
        start_bevm_node(con, address)
        # showlog(con, address)
        con.close()


def get_infos():
    config = ConfigParser()
    config_file_path = './config.ini'
    config.read(config_file_path, encoding='utf-8')
    username = config['user_config'].get('username')
    password = config['user_config'].get('password')
    data = getdata()
    return data, password, username


def do_start():
    data, password, username = get_infos()
    for address, host in data.items():
        con = Connection(host=host,
                         user=username,
                         connect_kwargs={"password": password})
        start_bevm_node(con, address)


def do_showlog():
    data, password, username = get_infos()
    for address, host in data.items():
        con = Connection(host=host,
                         user=username,
                         connect_kwargs={"password": password})
        showlog(con, address)



if __name__ == '__main__':
    do_exec()
    #do_start()
    #do_showlog()
    pass


