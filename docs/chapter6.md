### Экспорт/импорт в текст

Модуль `irbis.export` содержит функции, необходимые для экспорта и импорта записей в текстовом формате, принятом в системах ИРБИС32 и ИРБИС64.

Вот как выглядит типичный файл в обменном формате ИРБИС:

```
#920: SPEC
#102: RU
#101: rus
#606: ^AХУДОЖЕСТВЕННАЯ ЛИТЕРАТУРА (ПРОИЗВЕДЕНИЯ)
#919: ^Arus^N02  ^KPSBO^Gca
#60: 10
#961: ^ZДА^AШукшин^BВ. М.^GВасилий Макарович
#210: ^D1998
#610: РУССКАЯ ЛИТЕРАТУРА
#610: РАССКАЗЫ
#1119: 7ef4c9af-f1d3-4adc-981b-5012463155a1
#900: ^B03^C11a^Xm^Ta
#215: ^A528^3в пер.
#200: ^VКн. 3^AСтранные люди
#10: ^A5-86150-048-7^D80
#907: ^CПК^A20180613^BNovikovaIA
#461: ^CСобрание сочинений : в 6 кн.^FВ. М. Шукшин^GНадежда-1^H1998^Z1998^XШукшин, Василий Макарович^DМосква^U1
#903: -051259089
#910: ^A0^B1759089^DФ104^U2018/45^Y45^C20180607
#905: ^21^D1^J1^S1
*****
```

#### Функция read_text_record

Функция определена следующим образом:

```python
def read_text_record(stream: TextIO) -> Optional[MarcRecord]:
    pass
```

Она принимает в качестве аргумента текстовый поток, считывает запись и возвращает её. Если достигнут конец потока, возвращается `None`. Вот как можно использовать эту функцию:

```python
import irbis.export as bars

filename ='data/records.txt'
with open(filename, 'rt', encoding='utf-8') as stream:
    while True:
        # Считываем все записи из файла
        record = bars.read_text_record(stream)
        if not record:
            break
        # и распечатываем заглавия
        print(record.fm(200, 'a') or '(null)')
```

Обратите внимание, что функция принимает любой вид текстового потока: не только файло, но и сокет, консоль, массив символов в оперативной памяти и т. д.

#### Функция write_text_record

Функция, обратная `read_text_record`. Определена следующим образом:

```python
def write_text_record(stream: TextIO, record: MarcRecord) -> None:
    pass
```

В качестве аргумента она принимает текстовый поток, в который разрешена запись. Это может быть как файл, так и сокет, консоль, вообще любой объект, реализующий протокол текстового вывода. Вот как можно использовать данную функцию:

```python
import irbis.core as bars
import irbis.export as predator
import tempfile

client = bars.Connection()
client.connect('host', 6666, 'librarian', 'secret')
# Находим и загружаем с сервера 5 сказок Пушкина
found = client.search_read('"A=ПУШКИН$" * "T=СКАЗКИ$"', 5)
client.disconnect()

# Создаём временный текстовый файл
with tempfile.NamedTemporaryFile(mode='wt', 
    encoding='utf-8', delete=False) as stream:
    # Сохраняем найденные записи в файле
    for record in found:
        predator.write_text_record(stream, record)
    # Не забываем записать признак окончания 
    stream.write(predator.STOP_MARKER)
```
