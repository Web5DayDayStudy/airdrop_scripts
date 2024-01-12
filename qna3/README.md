
# 先决条件

### 签到
需要opbnb链上有bnb，不用太多，一两刀就行
### 领取积分
需要bsc链上有bnb

# 安装依赖
pip3 install -r requirements.txt

# 运行
需要先进行配置： 

1: checkin_private_keys.txt - 签到私钥 

2: claim_private_keys.txt - 领取积分的私钥 

3: socks5_proxys.txt - 代理配置,格式：
```
ip|port|username|password
ip|port|username|password
```
## 签到

python checkin_executor.py

## 领取积分

python claim_executor.py

# 查看结果
去浏览器上看看成功没


# Feature

- [x] 领取积分
- [ ] 邀请注册
- [ ] 点赞回答