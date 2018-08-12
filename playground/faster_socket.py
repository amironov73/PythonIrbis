# coding: utf-8

import random
import socket

host = '127.0.0.1'
port = 6666
login = '1'
password = '1'
client_id = random.randint(111111, 999999)
command_id = 1
arm = 'C'


def send(command, *other):
    packet = ('1', command, arm, command, str(client_id), str(command_id),
              password, login, '', '', '', *other)
    packet = '\n'.join(packet).encode('cp1251')
    sock = socket.socket()
    sock.connect((host, port))
    sock.send(packet)
    answer = sock.recv(100000)
    result = answer.decode('cp1251')
    return result


ini = send('A', login, password)
print(ini)

command_id += 1
answer = send('B', login)
print(answer)
