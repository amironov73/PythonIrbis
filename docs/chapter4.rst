=========================================
Прочие (вспомогательные) классы и функции
=========================================

FoundLine
=========

Строка найденной записи, может содержать результат расформатирования найденной записи. Содержит два поля:

============ ====== =================================================
Поле          Тип    Значение
============ ====== =================================================
mfn           int    MFN найденной записи
description   str    Результат расформатирования записи (опционально)
============ ====== =================================================

Пример применения см. раздел `SearchParameters` в данной главе.

MenuFile и MenuLine
===================

Файл меню (справочника) `MenuFile` состоит из пар строк `MenuLine`.

`MenuLine` содержит следующие поля:

======== ===== =======================================
Поле      Тип   Значение
======== ===== =======================================
code      str   Условный код (должен быть непустым)
comment   str   Комментарий к коду (может быть пустым)
======== ===== =======================================

`MenuFile` содержит единственное поле `entries` - список элементов типа `MenuLine`. Определены следующие методы:

* `def get_entry(self, code: str) -> Optional[MenuEntry]` -- получение элемента по коду. Внимание! Если в меню присуствует несколько элементов с одинаковым кодом, возвращается первый найденный.
* `def get_value(self, code: str, default_value: Optional[str] = None) -> Optional[str]:` -- получение комментария по коду (задаётся также значение по умолчанию, которое возвращается, когда соответствующий элемент не найден).
* `def parse(self, lines: List[str]) -> None:` -- разбор тексового представления меню (справочника).
* `def save(self, filename: str) -> None:` -- сохранение меню в локальный текстовый файл.

Загрузить меню (справочник) из локального текстового файла можно с помощью функции `load_menu`:

.. code-block:: python

  import irbis

  menu = irbis.load_menu(r'C:\path\file.mnu')
  print(menu.get_value('a', '???'))

Загрузить меню (справочник) с сервера ИРБИС64 можно с помощью функции `read_menu`:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  menu = client.read_menu('3.IBIS.ii.mnu')
  value = menu.get_value('1')
  print(f"Value is {value}")
  client.disconnect()

IniFile, IniSection и IniLine
=============================

INI-файл, состоящий из секций, которые в свою очередь состоят из строк вида "ключ=значение".

Клиент получает свой INI-файл при подключении к серверу. Он хранится в свойстве `ini_file` класса `Connection`.

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  ini = client.ini_file
  dbnnamecat = ini.get_value('Main', 'DBNNAMECAT')
  print(f"DBNNAMECAT={dbnnamecat}")
  client.disconnect()

Также можно прочитать произвольный INI-файл с сервера ИРБИС64 с помощью метода `read_ini_file`:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  ini = client.read_ini_file('3.RDR.KO.INI')
  number = ini.get_value('SEARCH', 'ItemNumb')
  print(f"Число элементов={number}")
  client.disconnect()

TreeFile и TreeNode
===================

TRE-файл -- древовидный текстовый справочник. Состоит из узлов, каждый из которых может быть либо узлом самого верхнего уровня, либо дочерним по отношению к узлу более высокого уровня. Уровень узла определяется величиной отступа, с которым соответствующая строка записана в файле справочника.

Класс `TreeNode` соответствует узлу дерева. Содержит следующие поля:

========= ====== ================================================
Поле      Тип    Назначение
========= ====== ================================================
children  list   Список дочерних узлов (может быть пустым).
value     str    Текстовое значение узла (не может быть пустым).
level     int    Уровень узла (0 = узел самого верхнего уровня).
========= ====== ================================================

Класс `TreeFile` описывает TRE-файл в целом. Содержит следующие поля:

========= ====== ================================================
Поле       Тип    Назначение
========= ====== ================================================
roots      list   Список узлов самого верхнего уровня (корневых).
========= ====== ================================================

Прочитать древовидный справочник из текстового файла можно с помощью функции `load_tree_file`:

.. code-block:: python

  import irbis
  
  tree = irbis.load_tree_file(r'C:\IRBIS64\Datai\IBIS\ii.tre')
  print(tree.roots[0].value)

Загрузить TRE-файл с сервера ИРБИС64 можно с помощью функции `read_tree_file`:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  tree = client.read_tree_file('2.IBIS.II.tre')
  print(tree.roots[0].value)
  client.disconnect()

DatabaseInfo
============

Информация о базе данных ИРБИС. Класс содержит следующие поля:

=================== ====== ==============================================================
Поле                 Тип    Назначение
=================== ====== ==============================================================
name                 str    Имя базы данных (непустое).
description          str    Описание в произвольной форме (может быть пустым).
max_mfn              int    Максимальный MFN.
logically_deleted    list   Перечень MFN логически удалённых записей (может быть пустым).
physically_deleted   list   Перечень MFN физически удалённых записей (может быть пустым).
nonactualized        list   Перечень MFN неактуализированных записей (может быть пустым).
database_locked      bool   Флаг: база заблокирована на ввод.
read_only            bool   Флаг: база доступна только для чтения.
=================== ====== ==============================================================

Получение информации о конкретной базе данных (заполняются только поля `max_mfn`, `logically_deleted`, `physically_deleted`, `nonactualized`, `database_locked`):

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  info = client.get_database_info('IBIS')
  print(f"Удалённых записей: {len(info.logically_deleted)}")
  client.disconnect()

Получить список баз данных, доступных для данного АРМ, можно с помощью метода `list_databases` (заполняются только поля `name`, `description`, `read_only`).

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  databases = client.list_databases('1..dbnam2.mnu')
  for db in databases:
      print(f"{db.name} => {db.description}")
  client.disconnect()

ProcessInfo
===========

Информация о запущенном на ИРБИС-сервере процессе.

VersionInfo
===========

Информация о версии ИРБИС-сервера.

ClientInfo
==========

Информация о клиенте, подключенном к серверу ИРБИС (не обязательно о текущем).

UserInfo
========

Информация о зарегистрированном пользователе системы (по данным `client_m.mnu`).  Определены следующие поля:

============== ===== =======================================
Поле            Тип   Назначение
============== ===== =======================================
number          str   Номер по порядку в списке.
name            str   Логин пользователя.
password        str   Пароль.
cataloger       str   Доступность АРМ "Каталогизатор".
reader          str   Доступность АРМ "Читатель".
circulation     str   Доступность АРМ "Книговыдача".
acquisitions    str   Доступность АРМ "Комплектатор".
provision       str   Доступность АРМ "Книгообеспеченность".
administrator   str   Доступность АРМ "Администратор".
============== ===== =======================================

Если строка доступа к АРМ пустая, то доступ пользователя к соответствующему АРМ запрещен.

Получить список зарегистрированных в системе пользователей можно с помощью метода `list_users`:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  users = client.list_users()
  for user in users:
      print(f"{user.name} => {user.password}")
  client.disconnect()

Обновить список зарегистрированных пользователей можно с помощью метода `update_user_list`:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  users = client.list_users()
  checkhov = irbis.UserInfo()
  checkhov.number = str(len(users))
  checkhov.name = 'Чехов'
  checkhov.password = 'Каштанка'
  checkhov.cataloger = 'irbisc_chekhov.ini'
  users.append(checkhov)
  client.update_user_list(users)
  client.disconnect()

TableDefinition
===============

Данные для метода `print_table`.

ServerStat
==========

Статистика работы ИРБИС-сервера.

PostingParameters
=================

Параметры для запроса постингов с сервера. Содержит следующие поля:

========= ====== ================================================
Поле       Тип    Значение
========= ====== ================================================
database   str    Имя базы данных
first      int    Номер первого постинга (нумерация с 1)
fmt        str    Опциональный формат
number     int    Количество затребуемых постингов
terms      list   Список терминов, для которых требуются постинги
========= ====== ================================================

Получить список постингов с сервера можно с помощью функции `read_postings`. Класс `PostingParameters` предоставляет возможность тонко настроить эту функцию:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  params = irbis.PostingParameters()
  params.database = 'IBIS'  # Имя базы данных
  params.first = 1  # Постинги, начиная с первого
  params.number = 10  # Требуем до 10 постингов
  params.terms = ['K=БЕТОН']  # Термины
  postings = client.read_postings(params)
  for posting in postings:
      print(f"MFN={posting.mfn}, TAG={posting.tag}, OCC={posting.occurrence}")
  client.disconnect()

TermParameters
==============

Параметры для запроса терминов с сервера. Содержит следующие поля:

========= ====== =====================================
Поле       Тип    Значение
========= ====== =====================================
database   str    Имя базы данных
number     int    Количество затребуемых терминов
reverse    bool   Выдавать термины в обратном порядке?
start      str    Стартовый термин
format     str    Опциональный формат
========= ====== =====================================

Получить список терминов с сервера можно с помощью функции `read_terms`. Класс `TermParameters` предоставляет возможность тонко настроить эту функцию:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  params = irbis.TermParameters()
  params.database = 'IBIS'  # Имя базы данных
  params.number = 10  # Требуем выдать до 10 терминов
  params.reverse = True  # В обратном порядке
  params.start = 'K=БЕТОН'
  terms = client.read_terms(params)
  for term in terms:
      print(f"{term.text} => {term.count}")
  client.disconnect()

TermInfo
========

Информация о термине поискового словаря. Содержит всего два поля:

====== ===== =============================================================
Поле    Тип   Значение
====== ===== =============================================================
count   int   Количество постингов (вхождений) термина в поисковом словаре
text    str   Собственно значение термина
====== ===== =============================================================

Имейте в виду, что термин может входить в одну и ту же запись несколько раз, и все эти вхождения будут отражены в словаре.

Получить список терминов с сервера можно с помощью функции `read_terms`.

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  terms = client.read_terms(('K=БЕТОН', 10))
  for term in terms:
      print(f"{term.text} => {term.count}")
  client.disconnect()

TermPosting
===========

Постинг (вхождение) термина в поисковом индексе. Содержит следующие поля:

=========== ===== =========================================
Поле         Тип   Значение
=========== ===== =========================================
mfn          int   MFN записи
tag          int   Метка поля
occurrence   int   Повторение поля
count        int   Позиция в поле
text         str   Опциональный результат расформатирования
=========== ===== =========================================

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  postings = client.read_postings('K=БЕТОН')
  for posting in postings:
      print(f"MFN={posting.mfn}, TAG={posting.tag}, OCC={posting.occurrence}")
  client.disconnect()

SearchParameters
================

Параметры для поиска записей (методы `search` и `search_ex`). Содержит следующие поля:

Поле       | Тип | Значение по умолчанию | Назначение
---------== ==-== ==-------------------== ==---------
database   | str | None | Имя базы данных (опционально)
expression | str | None | Выражение для поиска по словарю (быстрый поиск)
first      | int | 1    | Индекс первой из возвращаемых записей
format     | str | None | Опциональный формат для найденных записей
max_mfn    | int | 0    | Максимальный MFN для поиска (опционально)
min_mfn    | int | 0    | Минимальный MFN для поиска (опционально)
number     | int | 0    | Количество возвращаемых записей (0 = все)
sequential | str | None | Выражение для последовательного поиска (медленный поиск)

Если имя базы данных не задано, подразумевается текущая база данных, к которой подключен клиент.

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  params = irbis.SearchParameters()
  params.database = 'IBIS'  # По какой базе ищем
  params.expression = '"A=ПУШКИН$"'  # Поиск по словарю
  params.number = 10  # Выдать не больше 10 записей
  params.format = '@brief'  # Форматирование найденных записей
  # Последовательнсый поиск среди отобранных по словарю записей
  params.sequential = "if v200^a:'Сказки' then '1' else '0' fi"
  found = client.search_ex(params)
  for line in found:
      record = client.read_record(line.mfn)
      print(record.fm(200, 'a'))
      # Получаем расформатированную запись
      print(line.description)

SearchScenario
==============

Сценарий поиска. Содержит следующие поля:

Поле            | Тип  | Значение
--------------== ==--== ==-------
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

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  scenarios = client.read_search_scenario('2.IBIS.SEARCH.INI')
  print(f"Всего сценариев поиска: {len(scenarios)}")
  for scenario in scenarios:
      print(f"{scenario.name} => {scenario.prefix}")
  client.disconnect()

Стандартный сценарий поиска содержится в INI-файле, полученном клиентом с сервера при подключении:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  scenarios = irbis.SearchScenario.parse(client.ini_file) 
  print(f"Всего сценариев поиска: {len(scenarios)}")
  for scenario in scenarios:
      print(f"{scenario.name} => {scenario.prefix}")
  client.disconnect()

ParFile
=======

PAR-файл -- содержит пути к файлам базы данных ИРБИС. Определены следующие поля:

Поле | Тип | Значение
---== ==-== ==---------------
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

.. code-block:: python

  import irbis
  
  par = irbis.load_par_file(r'C:\IRBIS64\DataI\IBIS.par')
  # Полчаем путь к MST-файлу
  print(par.mst)

Загрузить PAR-файл с сервера ИРБИС64 можно с помощью функции `read_par_file`:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  par = client.read_par_file('1..IBIS.par')
  # Получаем путь к MST-файлу
  print(par.mst)
  client.disconnect()

OptFile и OptLine
=================

OPT-файл -- файл оптимизации рабочих листов и форматов показа.

Типичный OPT-файл выглядит так:

::

  920
  5
  PAZK  PAZK42
  PVK   PVK42
  SPEC  SPEC42
  J     !RPJ51
  NJ    !NJ31
  NJP   !NJ31
  NJK   !NJ31
  AUNTD AUNTD42
  ASP   ASP42
  MUSP  MUSP
  SZPRF SZPRF
  BOUNI BOUNI
  IBIS  IBIS
  +++++ PAZK42
  *****

Класс `OptLine` представляет одну строку в OPT-файле. Содержит следующие поля.

Поле      | Тип | Значение
--------== ==-== ==---------------
pattern   | str | Шаблон для имени рабочего листа (см. ниже).
worksheet | str | Имя соответствующего WS-файла (без расширения).

Шаблон для имени может содержать символ `+`, означающий «любой символ, в том числе его отсутствие».

Класс `OptFile` представляет OPT-файл в целом. Содержит следующие поля.

Поле      | Тип  | Значение
--------== ==--== ==---------------
lines     | list | Список строк (`OptLine`).
length    | int  | Длина шаблона в символах.
tag       | int  | Метка поля в записи, хранящего имя рабочиего листа.

Определены следующие методы:

* **def parse(self, text)** -- разбор текстового представления OPT-файла.

* **def resolve_worksheet(self, tag: str) -> Optional\[str\]** -- поиск имени WS-файла для указанного значения (например, "SPEC"). Если соответствующего имени не найдено, возвращается `None`.

* **def save(self, filename)** -- сохранение в текстовый файл с указанным именем.

Прочитать OPT-файл из локального файла можно с помощью функции `load_opt_file`:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  opt = irbis.load_opt_file(r"C:\IRBIS64\Datai\IBIS\WS31.opt")
  record = client.read_record(123)
  worklist = record.fm(opt.tag)
  ws_name = opt.resolve_worksheet(worklist)
  print(f"WS name: {ws_name}")
  client.disconnect()

Загрузить OPT-файл с сервера можно с помощью функции `read_opt_file`:

.. code-block:: python

  import irbis
  
  client = irbis.Connection()
  client.connect('host', 6666, 'librarian', 'secret')
  opt = client.read_opt_file('2.IBIS.WS31.opt')
  record = client.read_record(123)
  worklist = record.fm(opt.tag)
  ws_name = opt.resolve_worksheet(worklist)
  print(f"WS name: {ws_name}")
  client.disconnect()

GblStatement и GblSettings
==========================

Классы для глобальной корректировки базы данных.

ClientQuery
===========

Клиентский запрос. Инфраструктурный класс.

ServerResponse
==============

Ответ сервера. Инфраструктурный класс.
