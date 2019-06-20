# coding: utf-8

# В следующей программе создается и отправляется на сервер 10 записей.
# Показано добавление в запись полей с подполями.

import irbis.core as irbis

SF = irbis.SubField

# Подключаемся к серверу
client = irbis.Connection()
client.parse_connection_string('host=127.0.0.1;port=6666;database=IBIS;user=1;password=1;')
client.connect()

for i in range(10):
    # Создаем запись
    record = irbis.MarcRecord()

    # Наполняем её полями: первый автор
    record.add(700, SF('a', 'Миронов'), SF('b', 'А. В.'),
               SF('g', 'Алексей Владимирович'))

    # заглавие
    record.add(200, SF('a', f'Работа с ИРБИС64: версия {i}.0'),
               SF('e', 'руководство пользователя'))

    # выходные данные
    record.add(210, SF('a', 'Иркутск'), SubField('c', 'ИРНИТУ'),
               SF('d', '2018'))

    # рабочий лист
    record.add(920, 'PAZK')

    # Отсылаем запись на сервер.
    # Обратно приходит запись, обработанная AUTOIN.GBL
    client.write_record(record)
    print(record)  # распечатываем обработанную запись
    print()

# Отключаемся от сервера
client.disconnect()
