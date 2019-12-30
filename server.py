#!python3
# -*- coding: utf-8 -*-
# @Author: 虚伪
# @Date:   2019-12-29 00:30:53
# @Last Modified by:   虚伪
# @Last Modified time: 2019-12-30 15:41:31

import socket
import base64
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA1
from Crypto.Signature import pkcs1_15


# 1 设置服务器
server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind(("127.0.0.1",9999))
server.listen(5)

# 3 生成RSA公私钥,发送公钥,打印 公私钥,保存密钥
client,addr = server.accept()
client.send("hello,i'm server".encode('utf-8'))

rsa_key   = RSA.generate(1024)

print("public_key: " + '\n'+   str(rsa_key.publickey().export_key()))
print("private_key: " +  '\n'+ str(rsa_key.export_key()))

with open("public_key.pem", "wb") as file_public_key:
	file_public_key.write(rsa_key.publickey().export_key())
with open("private_key.pem","wb") as file_private_key:
	file_private_key.write(rsa_key.export_key())

#实例化RSA私钥解密套件
private_key = RSA.import_key(open("private_key.pem", "rb").read())
cipher_rsa= PKCS1_OAEP.new(private_key)

# 发送公钥文件
with open("public_key.pem", "rb") as file :
	data = file.read(10000)
	client.sendall(data)

# 5 协商aes对称密钥,解密密钥,并打印aes密钥

aes_key = (client.recv(1024)).decode()
print("aes_key: ")
print(aes_key)
aes_key = base64.b64decode(aes_key)
#用私钥解密密钥
aes_key = cipher_rsa.decrypt(aes_key)
print(aes_key)
#实例化aes加密套件
cipher_aes = AES.new(aes_key,AES.MODE_ECB)

# 6 输入信息,加密,发送信息
print("请输入传送信息: ")
data = input()
data = bytes(data,'utf-8')
encrypted_data = cipher_aes.encrypt(pad(data,16))
client.send((base64.b64encode(encrypted_data)))
print("-----------")
#接收信息
encrypted_data = base64.b64decode((client.recv(4096)))
data = unpad(cipher_aes.decrypt(encrypted_data),16)
print(data.decode('utf-8'))

# 8 输入信息,hash,签名,拼接,发送信息和hash.
with open("private_key.pem", "rb") as file :
	private_key = RSA.import_key(file.read())
	print("请输入传送信息: ")
	data = input()
	data = bytes(data,'utf-8')
	digest = SHA1.new(data)
	signature = pkcs1_15.new(private_key).sign(digest)
	print(len(signature))
	data = data + signature 
	encrypted_data = cipher_aes.encrypt(pad(data,16))
	client.send((base64.b64encode(encrypted_data)))

client.close()
server.close()