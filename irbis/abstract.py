"""
Абстрактные классы для других модулей библиотеки
"""

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Any, Iterable


class DictLike:
    """
    Словареподобный абстрактный класс для хранения структур данных вида
    ключ-значение.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def keys(self) -> 'Iterable':
        """
        Абстрактный метод получения последовательности ключей.

        :return: последовательность ключей
        """

    @abstractmethod
    def __getitem__(self, key: 'Any') -> 'Any':
        """
        Абстрактный метод получения значения по ключу. Должен быть реализован
        у дочернего класса. Может использоваться для получения значения
        по индексу -- obj[key].

        :param key: ключ
        :return: значение по ключу
        """

    def get(self, key: 'Any', default: 'Any' = None) -> 'Any':
        """
        Метод получения значения по ключу без срабатывания исключения KeyError,
        когда ключ отсутствует.

        :param key: ключ
        :param default: возвращается, если значение не найдено по ключу
        :return: значение по ключу или аргумент default
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    @abstractmethod
    def __setitem__(self, key: 'Any', value: 'Any'):
        """
        Абстрактный метод установки значения по ключу. Должен быть реализован
        у дочернего класса.

        :param key: ключ
        :param value: устанавливаемое значение
        :return:
        """

    @abstractmethod
    def __delitem__(self, key):
        """
        Абстрактный метод удаления пары ключ-значение. Должен быть реализован
        у дочернего класса. Может вызываться следующим образом -- del obj[key].

        :param key: ключ
        :return:
        """

    def pop(self, key) -> 'Any':
        """
        Метод удаления пары ключ-значение, возвращающий значение.

        :param key: ключ
        :return: удалённое значение
        """
        values = self.__getitem__(key)
        if values:
            self.__delitem__(key)
        return values


class Hashable:
    """
    Хэшируемость -- абстрактный класс с говорящим названием. Может быть
    использован для реализации следующих новшеств:

    * сравнение объектов класса по значению с помощью операторов == и !=
    * хранение объектов класса внутри множества (тип set)
    * использование объектов класса как ключей словаря (тип dict)
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __hash__(self) -> int:
        """
        Абстрактный метод вычисления хэша. Должен быть реализован у дочернего
        класса. Требуется для работы метода __eq__(other).

        Если хэш вычисляется встроенной функцией hash(__o), помните:

        * аргумент должен быть хэшируемым объектом, например кортежем
        * порядок элементов внутри переданного кортежа влияет на результат

        :return: числовой хэш
        """

    def __eq__(self, other) -> bool:
        """
        Стандартный метод сравнения двух объектов одного типа по значению. Для
        работы должен быть реализован метод __hash__(). Позволяет сравнивать
        объекты с помощью операторов == и !=.

        :param other: другой объект для сравнения с текущим
        :return: True или False
        """
        return all((
            isinstance(self, type(other)),
            isinstance(other, type(self)),
            hash(self) == hash(other),
        ))
