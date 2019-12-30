#!python3		
# -*- coding: utf-8 -*-
# @Author: 虚伪
# @Date:   2019-12-29 00:29:20
# @Last Modified by:   虚伪
# @Last Modified time: 2019-12-30 15:42:09

import socket
import base64
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA1
from Crypto.Signature import pkcs1_15




# 2 申请访问服务器,获得公钥,打印公钥,导入公钥
client = socket.socket()
client.connect(("127.0.0.1",9999))

print(client.recv(2048).decode('utf-8')) 

with open("server_public_key.pem", 'wb') as file:
	data = client.recv(10000)
	file.write(data)

# 实例化RSA加密
public_key = RSA.import_key(open("server_public_key.pem").read())
print(open("server_public_key.pem").read())
cipher_rsa = PKCS1_OAEP.new(public_key)

# 4 生成aes密钥(ECB),公钥加密协商密钥 

#实例化AES加密套件
aes_key = get_random_bytes(16)
print(aes_key)
cipher_aes = AES.new(aes_key,AES.MODE_ECB)
#加密aes密钥并发送
encrypted_data  = cipher_rsa.encrypt(aes_key)
client.send((base64.b64encode(encrypted_data)))


# 7 接受信息,解密,打印
encrypted_data = base64.b64decode((client.recv(4096)))
data = unpad(cipher_aes.decrypt(encrypted_data),16)
print(data.decode('utf-8'))

# 发送信息
print("请输入传送信息: ")
data = input()
data = bytes(data,'utf-8')
encrypted_data = cipher_aes.encrypt(pad(data,16))
client.send((base64.b64encode(encrypted_data)))

# 9 接受信息,验证签名,打印信息和hash
with open("server_public_key.pem","rb") as file:
	public_key = RSA.import_key(file.read())
	encrypted_data = base64.b64decode((client.recv(4096)))
	data = unpad(cipher_aes.decrypt(encrypted_data),16)
	signature = data[-128:]
	digest = SHA1.new(data[:-128])
	try:
		pkcs1_15.new(public_key).verify(digest,signature)
		print("验证成功")
	except (ValueError, TypeError):
	   print("验证失败")

client.close()

