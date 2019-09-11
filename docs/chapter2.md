### Класс Connection

Класс `Connection` - "рабочая лошадка". Он осуществляет связь с сервером и всю необходимую перепаковку данных из клиентского представления в сетевое.

Экземпляр клиента создается конструктором:

```python
import irbis.core as bars

client = bars.Connection()
```

При создании клиента можно указать (некоторые) настройки:

```python
import irbis.core as bars

client = bars.Connection(host='irbis.rsl.ru', port=5555, username='ninja')
```

Можно задать те же настройки с помощью полей `host`, `port` и т. д.:

```python
client.host = 'irbis.rsl.ru'
client.port = 5555
```

Поле        | Тип | Назначение                  | Значение по умолчанию
------------|-----|-----------------------------|----------------------
host        | str | Адрес сервера               | '127.0.0.1'
port        | int | Порт                        | 6666
username    | str | Имя (логин) пользователя    | None
password    | str | Пароль пользователя         | None
database    | str | Имя базы данных             | 'IBIS'
workstation | str | Тип АРМа (см. таблицу ниже) | 'C'

Типы АРМов

Обозначение | Тип                 | Константа
------------|---------------------|----------
'R'         | Читатель            | READER
'C'         | Каталогизатор       | CATALOGER
'M'         | Комплектатор        | ACQUISITIONS
'B'         | Книговыдача         | CIRCULATION
'K'         | Книгообеспеченность | PROVISION
'A'         | Администратор       | ADMINISTRATOR

Обратите внимание, что адрес сервера задается строкой, так что может принимать как значения вроде `192.168.1.1`, так и `irbis.yourlib.com`.

Тип рабочей станции лучше задавать константой:

```python
import irbis.core as bars

client = bars.Connection()
client.host = '8.8.8.8'
client.workstation = bars.ADMINISTRATOR
```

Если какой-либо из вышеперечисленных параметров не задан явно, используется значение по умолчанию.

Имейте в виду, что логин и пароль пользователя не имеют значения по умолчанию, поэтому должны быть заданы явно.

#### Подключение к серверу и отключение от него

Только что созданный клиент еще не подключен к серверу. Подключаться необходимо явно с помощью метода `connect`, при этом можно указать параметры подключения:

```python
import irbis.core as bars

client = bars.Connection()
client.connect('192.168.1.2', 6666, 'librarian', 'secret')
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

Повторная попытка подключения с помощью того же экземпляра `Connection` игнорируется. При необходимости можно создать другой экземпляр и подключиться с его помощью (если позволяют клиентские лицензии). Аналогично игнорируются повторные попытки отключения от сервера.

Проверить статус "клиент подключен или нет" можно с помощью преобразования подключения к типу `bool`:

```python
if not client:
    # В настоящий момент мы не подключены
    return
```

Вместо индивидуального задания каждого из полей `host`, `port`, `username`, `password` и `database` предпочтительнее использовать метод `parse_connection_string`:

```python
import irbis.core as bars

client = bars.Connection()
client.parse_connection_string('host=192.168.1.4;port=5555;username=itsme;password=secret;db=RDR;')
client.connect()
# выполняем какие-нибудь действия
client.disconnect()
``` 

Подключенный клиент может сформировать строку подключения (с помощью метода `to_connection_string`), которую можно использовать для другого подключения:

```python
import irbis.core as bars

client1 = bars.Connection()
client1.connect('host', 6666, 'librarian', 'secret')
# выполняем какие-нибудь действия
connection_string = client1.to_connection_string()
client1.disconnect()
client2 = bars.Connection()
client2.parse_connection_string(connection_string)
client2.connect()
# выполняем какие-нибудь действия
client2.disconnect()
```

#### Многопоточность

Клиент написан в наивном однопоточном стиле, поэтому не поддерживает одновременный вызов методов из разных потоков.

Для одновременной отсылки на сервер нескольких команд необходимо создать соответствующее количество экземпляров подключений (если подобное позволяет лицензия сервера).

#### Подтверждение подключения

`irbis` самостоятельно не посылает на сервер подтверждений того, что клиент все еще подключен. Этим должно заниматься приложение, например, по таймеру. 

Подтверждение посылается серверу методом `nop`:
 
```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
client.nop()
client.disconnect()
```

#### Чтение записей с сервера

Для индивидуального чтения записи с сервера применяется метод `read_record`.

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
mfn = 123
record = client.read_record(mfn)
print(record.status)
client.disconnect()
```

Для группового чтения записей с сервера применяется метод `read_records`.

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
mfns = [12, 34, 56]
records = client.read_records(mfns)
for record in records:
    print(record.status)
client.disconnect()
```

Методы для работы записями в клиентском представлении (доступ к полям/подполям, добавление/удаление полей и т. д.) см. [в следующей главе](chapter3.md).

#### Сохранение записи на сервере

Вновь созданную либо модифицированную запись можно сохранить на сервере с помощью метода `write_record`. Сначала покажем, как выполняется модификация записи:

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
mfn = 123
record = client.read_record(mfn)
# Добавляем в запись поле 300 (общее примечание)
record.add(300, 'Примечание к записи')
# Сохраняем запись обратно на сервер
client.write_record(record)
client.disconnect()
```

Теперь попробуем создать запись "с нуля" и сохранить её в базе данных:

```python
import irbis.core as bars

SF = bars.SubField # для краткости

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')

# Создаём запись и наполняем её полями
record = bars.MarcRecord()
record.add(200, SF('a', 'Заглавие'))
record.add(700, SF('a', 'Фамилия автора'))

# Отправляем запись на сервер
# Запись попадёт в текущую базу данных
client.write_record(record)

client.disconnect()
```

#### Удаление записей

Удаление записи заключается в установке её статуса `LOGICALLY_DELETED`. Для этого применяется метод `delete_record`, принимающий MFN записи:

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
mfn = 123 # MFN записи, подлежащей удалению
client.delete_record(mfn)
client.disconnect()
```

После удаления запись становится логически удалённой, т. е. физически она присутствует в файле документов и может быть считана клиентом, однако исключается из поиска. Логически удалённую запись в любой момент можно восстановить с помощью метода `undelete_record`, также принимающего MFN записи.

Администратор может провести на сервере так называемую реорганизацию файла документов, в процессе которой логически удалённые записи будут исключены из мастер-файла (однако, за ними сохранится MFN). Такие записи не могут быть прочитаны и/или восстановлены клиентом.

#### Поиск записей

Поиск записей в ИРБИС осуществляется двумя способами:

1. Так называемый "прямой поиск", выполняемый по автоматически поддерживаемому поисковому индексу (словарю). Используется специальный синтаксис, описанный на странице http://sntnarciss.ru/irbis/spravka/pril01701001000.htm
2. Так называемый "последовательный поиск", заключающийся в последовательном переборе записей. Для него используется другой синтаксис, описанный на странице http://sntnarciss.ru/irbis/spravka/pril01701002000.htm.

##### Прямой поиск

Обратите внимание, что при прямом поиске мы заключаем искомые термины в дополнительные двойные кавычки, это требование сервера ИРБИС64 (ведь термины могут включать в себя пробелы и специальные символы, и без кавычек сервер не сможет определить конец одного термина и начало другого).

Вот как выглядит правильно сформулированное поисковое выражение:

```python
search_expression = '"A=ПУШКИН$" * ("T=СКАЗКИ$" + "T=ПОВЕСТИ$")'
```

Количество найденных записей по данному запросу:

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Находим книги, автором которых является Пушкин
count = client.search_count('"A=ПУШКИН$"')
print(f"Всего книг Пушкина в фонде: {count}")
client.disconnect()
```

**Имейте в виду, что сервер ИРБИС64 возвращает записи в произвольном порядке!** Чаще всего этот порядок совпадает с порядком, в котором записи были введены в базу данных. Поэтому сортировать записи должен сам клиент.

Обычный поиск с помощью метода `search` выдаёт не более 32 тыс. найденных записей (это ограничение сервера ИРБИС64):

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Получаем MFN книг, автором которых является Пушкин
found = client.search('"A=ПУШКИН$"')
# Распечатываем список найденных MFN
print('Найдены MFN:', ', '.join(found)) 
client.disconnect()
```

Метод `search_all` выдаёт все найденные записи, в т. ч. если их много больше 32 тыс. *Осторожно! Этот метод может занять много времени и ресурсов как сервера, так и клиента!*

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Получаем MFN книг, у которых есть хотя бы один автор
found = client.search_all('"A=$"')
# Распечатываем список найденных MFN
print('Найдены MFN:', ', '.join(found)) 
client.disconnect()
```

Можно объединить поиск с одновременным считыванием записей, применив метод `search_read`. *Осторожно! Этот метод может занять много времени и ресурсов как сервера, так и клиента!* Устанавливайте разумное значение параметра `limit` при вызове этого метода.

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Считываем первые 5 найденных записей для книг,
# автором которых является Пушкин 
found = client.search_read('"A=ПУШКИН$"', 5)
# Распечатываем заглавия найденных книг:
for record in found:
    print(record.fm(200, 'a'))
client.disconnect()
```

Поиск с одновременным расформатированием записей осуществляется методм `search_format`:

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Расформатируем первые 5 найденных записей для книг,
# автором которых является Пушкин
found = client.search_format('"A=ПУШКИН$"', '@brief', 5)
# Распечатываем результаты форматирования:
for line in found:
    print(line)
client.disconnect()
```

##### Последовательный поиск

Последовательный поиск можно выполнить при помощи метода `search_ex`, принимающий в себя спецификацию поискового запроса `SearchParameters`. Часто последовательный поиск проводят по результатам предварительного прямого поиска. В терминах `SearchParameters` это означает задание значения поля `sequential` (выражение для последовательного поиска) вместе (согласованно) со значением поля `expression` (выражение для прямого поиска).

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
params = bars.SearchParameters()
params.database = 'IBIS' # По какой базе ищем
params.expression = '"A=ПУШКИН$"' # Прмямой поисй (по словарю)
params.number = 10 # Выдать не больше 10 записей
params.format = '@brief' # Форматирование найденных записей
# Последовательнсый поиск среди отобранных по словарю записей
params.sequential = "if v200^a:'Сказки' then '1' else '0' fi"
found = client.search_ex(params)
for line in found:
    record = client.read_record(line.mfn)
    print(record.fm(200, 'a'))
    # Получаем расформатированную запись
    print(line.description)
```

#### Работа с текстовыми файлами на сервере

Сначала необходимо упомянуть об используемой сервером ИРБИС64 спецификации имён файлов. Эта спецификация выглядит так:

```
Расположение . База . ИмяФайла
```

где `расположение` - число, означающее место, где сервер должен искать файл:

* 0 – общесистемный путь (директория, в которую установлен сервер ИРБИС64), чаще всего `C:\IRBIS64`.
* 1 – путь размещения сведений о базах данных сервера ИРБИС64, чаще всего `C:\IRBIS64\DATAI`.
* 2 – путь на мастер-файл базы данных. Для базы данных IBIS чаще всего выглядит так: `C:\IRBIS64\DATAI\IBIS`. 
* 3 – путь на словарь базы данных. Чаще всего совпадает с предыдущим путём.
* 10 – путь на параметрию базы данных. Чаще всего совпадает с предыдущим путём.

Для расположений `0` и `1` имя базы данных указывать не нужно, т. к. оно не имеет смысла. Такие пути выглядят так: 

* `0..RC.MNU` - меню с римскими цифрами, хранится рядом с сервером ИРБИС64.
* `1..dbnam2.mnu` - меню со списком баз данных, доступных АРМ "Каталогизатор", хранится в папке `DATAI`.

Для остальных расположений между двух точек указывают имя базы данных. Примеры:

* `2.IBIS.brief.pft` - формат краткого библиографического описания для базы данных `IBIS`.  
* `2.RDR.email.pft` - формат электронной почты для базы данных `RDR`.
* `2.CMPL.KP.MNU` - меню с каналами поступления для базы данных `CMPL`.

Для путей, больших или равных 2, сервер сначала ищет файл в директории, заданной в PAR-файле, и, если не находит там, то пытается найти файл с тем же именем в папке `Deposit`.

**Обратите внимание! Сервер ИРБИС64 под Windows игнорирует регистр символов в спецификации имён файлов!** 

Чаще всего клиенты считывают с сервера следующие текстовые файлы:

* форматы (имеют расширение PFT) для формирования каталожных карточек и списков литературы,
* меню (имеют расширение MNU),
* иерархические меню (имеют расширение TRE),
* INI-файлы со сценариями поиска,
* рабочие листы ввода (имеют расширения WS и WSS).

Однако, ничего не мешает клиентам получать с сервера и любые другие текстовые и двоичные файлы, необходимые им для работы.

Текстовый файл можно получить с сервера с помощью метода `read_text_file`:

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Считываем формат краткого библиографического 
# описания для базы IBIS
brief = client.read_text_file('2.IBIS.brief.pft')
print('BRIEF:', brief)
client.disconnect()
```

**Обратите внимание! Если сервер не может найти указанный файл, либо не может получить доступ к этому файлу (недостаточно прав), он возвращает строку нулевой длины!**

Для считывания с сервера меню, иерархических справочников и других специфических текстовых файлов имеются соответствующие методы, описанные [в главе 4](chapter4.md).

Сохранить текстовый файл на сервере можно с помощью метода `write_text_file`. Имейте в виду, что текстовые файлы на сервере хранятся, как правило, в кодировке CP1251, так что все символы, не имеющие представления в данной кодировке, будут утеряны при сохранении.

Для получения с сервера двоичных файлов (например, изображений) используется метод `read_binary_file`:

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Считываем GIF-файл с бегущим ирбисом, 
# хранящийся рядом с сервером ИРБИС64
running = client.read_binary_file('0..irbis.gif')
# Сохраняем в локальный файл
with open('bars.gif', 'wb') as f:
    f.write(running)
client.disconnect()
```

Получить список файлов на сервере можно с помощью метода `list_files`. В него передаётся перечень (может состоять из одного файла) спецификаций файлов, которые нас интересуют. Разрешается использовать метасимволы '?' и '*', имеющие тот же смысл, что и в командной строке Windows. Метод возвращает массив имён (не спецификаций!) найденных файлов.

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Получаем список форматных файлов для базы IBIS
formats = client.list_files('2.IBIS.')
# Распечатываем полученный список файлов:
print(formats)
client.disconnect()
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

[Предыдущая глава](chapter1.md) | [Следующая глава](chapter3.md)
