# coding: utf-8

# Ниже прилагается пример простой программы.
# Сначала находятся и загружаются 10 первых библиографических записей,
# в которых автором является А. С. Пушкин. Показано нахождение
# значения поля с заданным тегом и подполя с заданным кодом.
# Также показано расформатирование записи в формат brief.

import irbis.core as bars

# Подключаемся к серверу
client = bars.Connection()
client.parse_connection_string('host=127.0.0.1;database=IBIS;user=librarian;password=secret;')
client.connect()

# Ищем все книги, автором которых является А. С. Пушкин
# Обратите внимание на двойные кавычки в тексте запроса
found = client.search('"A=ПУШКИН$"')
print(f'Найдено записей: {len(found)}')

# Чтобы не распечатывать все найденные записи, отберем только 10 первых
for mfn in found[:10]:
    # Получаем запись из базы данных
    record = client.read_record(mfn)

    # Извлекаем из записи интересующее нас поле и подполе
    title = record.fm(200, 'a')
    print('Заглавие:', title)

    # Форматируем запись средствами сервера
    description = client.format_record(bars.BRIEF, mfn)
    print('Биб. описание:', description)

    print()  # Добавляем пустую строку

# Отключаемся от сервера
client.disconnect()

