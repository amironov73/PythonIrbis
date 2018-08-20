import random
import asyncio

host = '127.0.0.1'
port = 6666
arm = 'C'
login = '1'
password = '1'
client_id = random.randint(11111111, 99999999)
command_id = 1


async def send(the_loop, packet):
    reader, writer = await asyncio.open_connection(host, port, loop=the_loop)
    writer.write(packet.encode('cp1251'))
    response = bytearray()
    while True:
        buffer = await reader.read(1024)
        if not buffer:
            break
        response.extend(buffer)

    writer.close()
    result = response.decode('cp1251')
    return result


async def connect(the_loop):
    """
    Асинхронно посылаем команду регистрации на сервере
    :param the_loop: Очередь сообщений
    :return: None
    """
    header = ('A', arm, 'A', str(client_id), str(command_id),
              '', '', '', '', '', login, password)
    packet = '\n'.join(header)
    packet = str(len(packet)) + '\n' + packet

    ini_file = await send(the_loop, packet)
    print(ini_file)


async def disconnect(the_loop):
    """
    Асинхронно посылаем команду разрегистрации на сервере
    :param the_loop: Очередь сообщений
    :return: None
    """
    header = ('B', arm, 'B', str(client_id), str(command_id), '', '', '', '', '', '', '')
    packet = '\n'.join(header)
    packet = str(len(packet)) + '\n' + packet

    answer = await send(the_loop, packet)
    print(answer)


loop = asyncio.get_event_loop()
loop.run_until_complete(connect(loop))
command_id += 1
loop.run_until_complete(disconnect(loop))
loop.close()

