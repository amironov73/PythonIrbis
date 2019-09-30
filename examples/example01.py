# coding: utf-8

"""
Ниже прилагается пример простой программы.

Сначала находятся и загружаются 10 первых библиографических записей,
в которых автором является А. С. Пушкин. Показано нахождение
значения поля с заданным тегом и подполя с заданным кодом.

Также показано расформатирование записи в формат brief.
"""

import irbis

# Подключаемся к серверу
client = irbis.Connection()  # pylint:disable=invalid-name
client.parse_connection_string('host=127.0.0.1;database=IBIS;' +
                               'user=librarian;password=secret;')
client.connect()

if not client.connected:
    print('Невозможно подключиться!')
    exit(1)

# Ищем все книги, автором которых является А. С. Пушкин
# Обратите внимание на двойные кавычки в тексте запроса
found = client.search('"A=ПУШКИН$"')  # pylint:disable=invalid-name
print(f'Найдено записей: {len(found)}')

# Чтобы не распечатывать все найденные записи, отберем только 10 первых
for mfn in found[:10]:
    # Получаем запись из базы данных
    record = client.read_record(mfn)

    # Извлекаем из записи интересующее нас поле и подполе
    title = record.fm(200, 'a')
    print(f'Заглавие: {title}')

    # Форматируем запись средствами сервера
    description = client.format_record(irbis.BRIEF, mfn)
    print(f'Биб. описание: {description}')

    print()  # Добавляем пустую строку

# Отключаемся от сервера
client.disconnect()
