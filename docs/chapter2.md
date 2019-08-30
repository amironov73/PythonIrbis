### Класс Connection

Класс `Connection` - "рабочая лошадка". Он осуществляет связь с сервером и всю необходимую перепаковку данных из клиентского представления в сетевое.

Экземпляр клиента создается конструктором:

```python
import irbis.core as irbis

client = irbis.Connection()
```

При создании клиента можно указать (некоторые) настройки:

```python
import irbis.core as irbis

client = irbis.Connection(host='irbis.rsl.ru', port=5555, username='ninja')
```

Можно задать те же настройки с помощью полей `host`, `port` и т. д.:

```python
client.host = 'irbis.rsl.ru'
client.port = 5555
```

Поле|Тип|Назначение|Значение по умолчанию
----|---|----------|---------------------
host        |str | Адрес сервера|'127.0.0.1'
port        |int | Порт|6666
username    |str | Имя (логин) пользователя|None
password    |str | Пароль пользователя|None
database    |str | Имя базы данных|'IBIS'
workstation |str | Тип АРМа (см. таблицу ниже)| 'C'

Типы АРМов

Обозначение|Тип
-----------|---
'R' | Читатель
'C' | Каталогизатор
'M' | Комплектатор
'B' | Книговыдача
'K' | Книгообеспеченность
'A' | Администратор

Обратите внимание, что адрес сервера задается строкой, так что может принимать как значения вроде `192.168.1.1`, так и `irbis.yourlib.com`.

Если какой-либо из вышеперечисленных параметров не задан явно, используется значение по умолчанию.

#### Подключение к серверу и отключение от него

Только что созданный клиент еще не подключен к серверу. Подключаться необходимо явно с помощью метода `connect`, при этом можно указать параметры подключения:

```python
client.connect(host='192.168.1.2')
```

Отключаться от сервера можно двумя способами: во-первых, с помощью метода `disconnect`:

```python
client.disconnect()
```

во-вторых, с помощью контекста, задаваемого блоком `with`:

```python
import irbis.core as bars

with bars.Connection(host='192.168.1.3') as client:
    client.connect(username='itsme', password='secret')
    
    # Выполняем некие действия.
    # По выходу из блока отключение от сервера произойдет автоматически.
```

При подключении клиент получает с сервера INI-файл с настройками, которые могут понадобиться в процессе работы:

```python
ini = client.connect()
format_menu_name = ini.get_value('Main', 'FmtMnu', 'FMT31.MNU')
```

Полученный с сервера INI-файл также хранится в поле `ini_file`.

Повторная попытка подключения с помощью того же экземпляра `IrbisConnection` игнорируется. При необходимости можно создать другой экземпляр и подключиться с его помощью (если позволяют клиентские лицензии). Аналогично игнорируются повторные попытки отключения от сервера.

Проверить статус "клиент подключен или нет" можно с помощью преобразования подключения к типу `bool`:

```python
if not client:
    # В настоящий момент мы не подключены
    return
```

Вместо индивидуального задания каждого из полей `host`, `port`, `username`, `password` и `database`, можно использовать метод `parse_connection_string`:

```python
client.parse_connection_string('host=192.168.1.4;port=5555;username=itsme;password=secret;db=RDR;')
``` 

#### Многопоточность

Клиент написан в наивном однопоточном стиле, поэтому не поддерживает одновременный вызов методов из разных потоков.

Для одновременной отсылки на сервер нескольких команд необходимо создать соответствующее количество экземпляров подключений (если подобное позволяет лицензия сервера).

#### Подтверждение подключения

`irbis` самостоятельно не посылает на сервер подтверждений того, что клиент все еще подключен. Этим должно заниматься приложение, например, по таймеру. 

Подтверждение посылается серверу методом `nop`:
 
```python
client.nop()
```

#### Чтение записей с сервера

```python
record = client.read_record(mfn)
```

#### Сохранение записи на сервере

```python
client.write_record(record)
```

#### Поиск записей

Количество найденных записей по данному запросу:

```python
count = client.search_count('"A=ПУШКИН$"')
```

Выдаёт не более 32 тыс. найденных записей:

```python
found = client.search('"A=ПУШКИН$"')
```

Выдаёт все найденные записи, в т. ч. если их много больше 32 тыс. Осторожно!

```python
found = client.search_all('"A=$"')
```

Поиск с одновременным считыванием записей:

```python
found = client.search_read('"A=ПУШКИН$"', 5)
```

Поиск с одновременным расформатированием записей:

```python
found = client.search_format('"A=ПУШКИН$"', '@brief', 5)
```

#### Поддержка асинхронности

```python
import irbis.core as bars

async def do_async_stuff():
    result = await connection.connect_async()
    if not result:
        print('Failed to connect')
        return

    print('Connected')

    max_mfn = await connection.get_max_mfn_async()
    print(f"Max MFN={max_mfn}")

    text = await connection.format_record_async('@brief', 1)
    print(text)

    await connection.nop_async()
    print('NOP')

    record = await connection.read_record_async(1)
    print(record)

    text = await connection.read_text_file_async('dn.mnu')
    print(text)

    count = await connection.search_count_async('K=бетон')
    print(f'Count={count}')

    found = await connection.search_async('K=бетон')
    print(found)

    await connection.disconnect_async()
    print('Disconnected')

#=============================================

connection = bars.Connection()
connection.host = 'localhost'
connection.username = 'librarian'
connection.password = 'secret'
connection.database = 'IBIS'

bars.init_async()

bars.irbis_event_loop.run_until_complete(do_async_stuff())

bars.close_async()
```

[Предыдущая глава](chapter1.md) [Следующая глава](chapter3.md)
