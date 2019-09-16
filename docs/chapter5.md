### Построитель запросов

Класс `Search` представляет собой построитель запросов в синтаксисе прямого поиска ИРБИС64. Он определён в модуле `irbis.builder`. В нём имеются следующие статические методы:

* **def all() -> Search** -- отбор всех документов в базе. Фактически строит запрос `I=$`.

* **def equals(prefix, \*values) -> Search** -- поиск по совпадению с одним из перечисленных значений. Возвращает построитель запросов для последующих цепочечных вызовов.

Экземплярные методы:

* **def and_(self, \*items) -> Search** -- логическое И. Возвращает построитель запросов для последующих цепочечных вызовов.

* **def not_(self, text) -> Search** -- логическое НЕ. Возвращает построитель запросов для последующих цепочечных вызовов.

* **def or_(self, \*items) -> Search** -- логическое ИЛИ. Возвращает построитель запросов для последующих цепочечных вызовов.

* **def same_field_(self, \*items) -> Search** -- логический оператор "в том же поле". Возвращает построитель запросов для последующих цепочечных вызовов.

* **def same_repeat_(self, \*items) -> Search** -- логический оператор "в том же повторении поля". Возвращает построитель запросов для последующих цепочечных вызовов.

Кроме того, предоставляются следующие функции, значительно упрощающие формирование запроса:

| Функция       | Поиск по 
|---------------|---------
| author        | автору
| bbk           | индексу ББК
| document_kind | виду документа
| keyword       | ключевым словам
| language      | языку текста
| magazine      | заглавию журнала
| mhr           | месту хранения
| number        | инвентарному номеру
| place         | месту издания (городу)
| publisher     | издательству
| rzn           | разделу знаний
| subject       | предметной рубрике
| title         | заглавию
| udc           | индексу УДК
| year          | году издания

Пример применения построителя запросов:

```python
import irbis.core as bars
from irbis.builder import *

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
expression = author('ПУШКИН$').and_(title('СКАЗКИ$'))
found = client.search_count(expression)
print(f"Найдено: {found}")
client.disconnect()
```

[Предыдущая глава](chapter4.md)