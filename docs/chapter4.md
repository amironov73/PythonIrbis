### Прочие (вспомогательные) классы и функции

#### FoundLine

Строка найденной записи, может содержать результат расформатирования найденной записи.

#### MenuFile и MenuLine

Файл меню. Состоит из пар строк.

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
menu = client.read_menu('3.IBIS.ii.mnu')
value = menu.get_value('1')
print(f"Value is {value}")
client.disconnect()
```

#### IniFile, IniSection и IniLine

INI-файл, состоящий из секций, которые в свою очередь состоят из строк вида "ключ=значение".

Клиент получает свой INI-файл при подключении к серверу. Он хранится в свойстве `ini_file`.

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
ini = client.ini_file
dbnnamecat = ini.get_value('Main', 'DBNNAMECAT')
print(f"DBNNAMECAT={dbnnamecat}")
```

Также можно прочитать произвольный INI-файл с сервера:

```python
import irbis.core as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
ini = client.read_ini_file('3.RDR.KO.INI')
number = ini.get_value('SEARCH', 'ItemNumb')
print(f"Число элементов={number}")
client.disconnect()
```

#### TreeFile и TreeLine

TRE-файл -- древовидный справочник.

#### DatabaseInfo

Информация о базе данных ИРБИС.

#### ProcessInfo

Информация о запущенном на ИРБИС-сервере процессе.

#### VersionInfo

Информация о версии ИРБИС-сервера.

#### ClientInfo

Информация о клиенте, подключенном к серверу ИРБИС (не обязательно о текущем).

#### UserInfo

Информация о зарегистрированном пользователе системы (по данным `client_m.mnu`).

#### TableDefinition

Данные для метода printTable.

#### ServerStat

Статистика работы ИРБИС-сервера.

#### PostingParameters

Параметры для запроса постингов с сервера.

#### TermParameters

Параметры для запроса терминов с сервера.

#### TermInfo

Информация о термине поискового словаря. Содержит всего два поля:

Поле  | Тип | Значение
------|-----|---------
count | int | Количество постингов (вхождений) термина в поисковом словаре    
text  | str | Собственно значение термина

Имейте в виду, что термин может входить в одну и ту же запись несколько раз, и все эти вхождения будут отражены в словаре.

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
terms = client.read_terms("K=БЕТОН")
for term in terms:
    print(f"{term.text} => {term.count}")
client.disconnect()
```

#### TermPosting

Постинг (вхождение) термина в поисковом индексе. Содержит следующие поля:

Поле       | Тип | Значение
-----------|-----|---------
mfn        | int | MFN записи
tag        | int | Метка поля
occurrence | int | Повторение поля
count      | int | Позиция в поле
text       | str | Опциональный результат расформатирования

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
postings = client.read_postings('K=БЕТОН')
for posting in postings:
    print(f"MFN={posting.mfn}, TAG={posting.tag}, OCC={posting.occurrence}")
client.disconnect()
```

#### SearchParameters

Параметры для поиска записей (метод `search`). Содержит следующие поля:

Поле       | Тип | Значение по умолчанию | Назначение
-----------|-----|-----------------------|-----------
database   | str | None | Имя базы данных (опционально)
expression | str | None | Выражение для поиска по словарю (быстрый поиск)
first      | int | 1    | Индекс первой из возвращаемых записей
format     | str | None | Опциональный формат для найденных записей
max_mfn    | int | 0    | Максимальный MFN для поиска (опционально)
min_mfn    | int | 0    | Минимальный MFN для поиска (опционально)
number     | int | 0    | Количество возвращаемых записей (0 = все)
sequential | str | None | Выражение для последовательного поиска (медленный поиск)

Если имя базы данных не задано, подразумевается текущая база данных, к которой подключен клиент.

```python
import irbis.core as bars

client = bars.Connection()
...
params = bars.SearchParameters()
params.database = 'IBIS' # По какой базе ищем
params.expression = '"A=ПУШКИН$"' # Поиск по словарю
params.number = 10 # Выдать не больше 10 записей
# Последовательнсый поиск среди отобранных по словарю записей
params.sequential = "if v200^a:'Сказки' then '1' else '0' fi"
found = client.search()
for mfn in found:
    record = client.read_record(mfn)
    print(record.fm(200, 'a'))
```

#### SearchScenario

Сценарий поиска.

#### ParFile

PAR-файл -- содержит пути к файлам базы данных ИРБИС.

#### OptFile и OptLine

OPT-файл -- файл оптимизации рабочих листов и форматов показа.

#### GblStatement и GblSettings

Классы для глобальной корректировки базы данных.

#### ClientQuery

Клиентский запрос. Инфраструктурный класс.

#### ServerResponse

Ответ сервера. Инфраструктурный класс.

[Предыдущая глава](chapter3.md)
