### Прочие (вспомогательные) классы и функции

#### FoundLine

Строка найденной записи, может содержать результат расформатирования найденной записи. Содержит два поля:

Поле        | Тип  | Значение
------------|------|---------
mfn         | int  | MFN найденной записи
description | str  | Результат расформатирования записи (опционально)

Пример применения см. `SearchParameters`.

#### MenuFile и MenuLine

Файл меню (справочника) `MenuFile` определён в `irbis.ext`. Состоит из пар строк `MenuLine`.

`MenuLine` содержит следующие поля:

Поле    | Тип | Значение
--------|-----|---------
code    | str | Условный код
comment | str | Комментарий к коду (может быть пустым)

`MenuFile` содержит единственное поле `entries` - список элементов типа `MenuLine`. Определены следующие методы:

* `def get_entry(self, code: str) -> Optional[MenuEntry]` -- получение элемента по коду. Внимание! Если в меню присуствует несколько элементов с одинаковым кодом, возвращается первый найденный.
* `def get_value(self, code: str, default_value: Optional[str] = None) -> Optional[str]:` -- получение комментария по коду (задаётся также значение по умолчанию, которое возвращается, когда соответствующий элемент не найден).
* `def parse(self, lines: List[str]) -> None:` -- разбор тексового представления меню (справочника).
* `def save(self, filename: str) -> None:` -- сохранение меню в локальный текстовый файл.

Загрузить меню (справочник) из локального текстового файла можно с помощью функции `load_menu`:

```python
import irbis.ext as bars

menu = bars.load_menu(r'C:\path\file.mnu')
print(menu.get_value('a', '???'))
```

Загрузить меню (справочник) с сервера ИРБИС64 можно с помощью функции `read_menu`:

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
menu = bars.read_menu(client, '3.IBIS.ii.mnu')
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
client.disconnect()
```

Также можно прочитать произвольный INI-файл с сервера ИРБИС64 с помощью функции `read_ini_file`:

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

Параметры для запроса постингов с сервера. Класс определён в `irbis.ext`. Содержит следующие поля:

Поле     | Тип  | Значение
---------|------|---------
database | str  | Имя базы данных
first    | int  | Номер первого постинга (нумерация с 1)
fmt      | str  | Опциональный формат
number   | int  | Количество затребуемых постингов
terms    | list | Список терминов, для которых требуются постинги

Получить список постингов с сервера можно с помощью функции `read_postings`. Класс `PostingParameters` предоставляет возможность тонко настроить эту функцию:

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
params = bars.PostingParameters()
params.database = 'IBIS' # Имя базы данных
params.first = 1 # Постинги, начиная с первого
params.number = 10 # Требуем до 10 постингов
params.terms = ['K=БЕТОН'] # Термины
postings = bars.read_postings(client, params)
for posting in postings:
    print(f"MFN={posting.mfn}, TAG={posting.tag}, OCC={posting.occurrence}")
client.disconnect()
```

#### TermParameters

Параметры для запроса терминов с сервера. Класс определён в `irbis.ext`. Содержит следующие поля:

Поле     | Тип  | Значение
---------|------|---------
database | str  | Имя базы данных
number   | int  | Количество затребуемых терминов
reverse  | bool | Выдавать термины в обратном порядке?
start    | str  | Стартовый термин
format   | str  | Опциональный формат

Получить список терминов с сервера можно с помощью функции `read_terms`. Класс `TermParameters` предоставляет возможность тонко настроить эту функцию:

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
params = bars.TermParameters()
params.database = 'IBIS' # Имя базы данных
params.number = 10 # Требуем выдать до 10 терминов
params.reverse = True # В обратном порядке
params.start = 'K=БЕТОН'
terms = bars.read_terms(client, params)
for term in terms:
    print(f"{term.text} => {term.count}")
client.disconnect()
```

#### TermInfo

Информация о термине поискового словаря. Содержит всего два поля:

Поле  | Тип | Значение
------|-----|---------
count | int | Количество постингов (вхождений) термина в поисковом словаре    
text  | str | Собственно значение термина

Имейте в виду, что термин может входить в одну и ту же запись несколько раз, и все эти вхождения будут отражены в словаре.

Получить список терминов с сервера можно с помощью функции `read_terms`.

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
terms = bars.read_terms(client, ('K=БЕТОН', 10))
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
postings = bars.read_postings(client, 'K=БЕТОН')
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
client.connect('host', 6666, 'librarian', 'secret')
params = bars.SearchParameters()
params.database = 'IBIS' # По какой базе ищем
params.expression = '"A=ПУШКИН$"' # Поиск по словарю
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

#### SearchScenario

Сценарий поиска. Определён в `irbis.ext`. Содержит следующие поля:

Поле            | Тип  | Значение
----------------|------|---------
name            | str  | Наименование поискового атрибута (автор, заглавие и т. п.)
prefix          | str  | Префикс соответствующих терминов в поисковом словаре (может быть пустым)
type            | int  | Тип словаря для соответствующего поиска
menu            | str  | Имя файла справочника (меню)
old             | str  | Имя формата (без расширения)
correction      | str  | Способ корректировки по словарю
truncation      | bool | Исходное положение переключателя "усечение"
hint            | str  | Текст подсказки/предупреждения
mod_by_dic_auto | str  | Параметр пока не задействован
logic           | int  | Применимые логические операторы
advance         | str  | Правила автоматического расширения поиска на основе авторитетного файла или тезауруса
format          | str  | Имя формата показа документов

Нестандартные сценарии поиска можно загрузить с сервера с помощью метода `read_search_scenario`:

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
scenarios = bars.read_search_scenario(client, '2.IBIS.SEARCH.INI')
print(f"Всего сценариев поиска: {len(scenarios)}")
for scenario in scenarios:
    print(f"{scenario.name} => {scenario.prefix}")
client.disconnect()
```

Стандартный сценарий поиска содержится в INI-файле, полученном клиентом с сервера при подключении:

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
scenarios = bars.SearchScenario.parse(client.ini_file) 
print(f"Всего сценариев поиска: {len(scenarios)}")
for scenario in scenarios:
    print(f"{scenario.name} => {scenario.prefix}")
client.disconnect()
```

#### ParFile

PAR-файл -- содержит пути к файлам базы данных ИРБИС. Класс определён в `irbis.ext`. Определены следующие поля:

Поле | Тип | Значение
-----|-----|---------
xrf  | str | Путь к XRF-файлу
mst  | str | Путь к MST-файлу
cnt  | str | Путь к CNT-файлу
n01  | str | Путь к N01-файлу
n02  | str | В ИРБИС64 не используется
l01  | str | Путь к L01-файлу
l02  | str | В ИРБИС64 не используется
ifp  | str | Путь к IFP-файлу
any  | str | В ИРБИС64 не используется
pft  | str | Путь к PFT-файлам
ext  | str | Путь к полнотекстовым файлам

Как правило, все поля, кроме `ext`, имеют одно и то же значение, т. к. вся база данных, кроме полнотекстовых файлов, хранится в одной и той же директории.

Загрузить PAR-файл из локального текстового файла можно с помощью функции `load_par_file`:

```python
import irbis.ext as bars

par = bars.load_par_file(r'C:\IRBIS64\DataI\IBIS.par')
# Полчаем путь к MST-файлу
print(par.mst)
```

Загрузить PAR-файл с сервера ИРБИС64 можно с помощью функции `read_par_file`:

```python
import irbis.ext as bars

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
par = bars.read_par_file(client, '1..IBIS.par')
# Получаем путь к MST-файлу
print(par.mst)
client.disconnect()
```

#### OptFile и OptLine

OPT-файл -- файл оптимизации рабочих листов и форматов показа.

#### GblStatement и GblSettings

Классы для глобальной корректировки базы данных.

#### ClientQuery

Клиентский запрос. Инфраструктурный класс.

#### ServerResponse

Ответ сервера. Инфраструктурный класс.

[Предыдущая глава](chapter3.md)
