# grassScript

forked from : https://github.com/ymmmmmmmm/getgrass_bot

优化了一下使用流程，增加了多socks5与多uid的支持

## 1:安装依赖
`pip3 install -r requirements.txt`

## 2:修改配置文件

s_config_yaml (智能模式)
config.yaml (指定模式)

## 3:启动
- 主从模式，配置好master_slave_config.yaml文件，run：python master_slave_exec.py

## 邀请链接

https://app.getgrass.io/register/?referralCode=59lUb0S1wUNZwZG

## user_id获取方法

### 方法一：
1.打开链接登录https://app.getgrass.io/dashboard

2.页面按F12打开控制台 输入代码

`console.log(localStorage.getItem('userId'))`

打印的就是当前用户的user_id

![0001](https://github.com/ymmmmmmmm/getgrass_bot/assets/51306299/31d0e16e-df2f-443a-a141-910d16052ed9)

### 方法二
修改login.py中的username，password，运行login.py, 会打印出当前账号uid


## Feature

todo

