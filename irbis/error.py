# coding: utf-8

"""
Ошибка, специфичная для ИРБИС.
"""

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union
    from irbis.specification import FileSpecification


def get_error_description(code: int) -> str:
    """
    Получение описания ошибки.

    :param code: Код ошибки
    :return: Описание ошибки
    """

    errors = {
        -100: 'Заданный MFN вне пределов БД',
        -101: 'Ошибочный размер полки',
        -102: 'Ошибочный номер полки',
        -140: 'MFN вне пределов БД',
        -141: 'Ошибка чтения',
        -200: 'Указанное поле отсутствует',
        -201: 'Предыдущая версия записи отсутствует',
        -202: 'Заданный термин не найден (термин не существует)',
        -203: 'Последний термин в списке',
        -204: 'Первый термин в списке',
        -300: 'База данных монопольно заблокирована',
        -301: 'База данных монопольно заблокирована',
        -400: 'Ошибка при открытии файлов MST или XRF (ошибка файла данных)',
        -401: 'Ошибка при открытии файлов IFP (ошибка файла индекса)',
        -402: 'Ошибка при записи',
        -403: 'Ошибка при актуализации',
        -600: 'Запись логически удалена',
        -601: 'Запись физически удалена',
        -602: 'Запись заблокирована на ввод',
        -603: 'Запись логически удалена',
        -605: 'Запись физически удалена',
        -607: 'Ошибка autoin.gbl',
        -608: 'Ошибка версии записи',
        -700: 'Ошибка создания резервной копии',
        -701: 'Ошибка восстановления из резервной копии',
        -702: 'Ошибка сортировки',
        -703: 'Ошибочный термин',
        -704: 'Ошибка создания словаря',
        -705: 'Ошибка загрузки словаря',
        -800: 'Ошибка в параметрах глобальной корректировки',
        -801: 'ERR_GBL_REP',
        -801: 'ERR_GBL_MET',
        -1111: 'Ошибка исполнения сервера (SERVER_EXECUTE_ERROR)',
        -2222: 'Ошибка в протоколе (WRONG_PROTOCOL)',
        -3333: 'Незарегистрированный клиент (ошибка входа на сервер) ' +
               '(клиент не в списке)',
        -3334: 'Клиент не выполнил вход на сервер (клиент не используется)',
        -3335: 'Неправильный уникальный идентификатор клиента',
        -3336: 'Нет доступа к командам АРМ',
        -3337: 'Клиент уже зарегистрирован',
        -3338: 'Недопустимый клиент',
        -4444: 'Неверный пароль',
        -5555: 'Файл не существует',
        -6666: 'Сервер перегружен. Достигнуто максимальное число ' +
               'потоков обработки',
        -7777: 'Не удалось запустить/прервать поток администратора ' +
               '(ошибка процесса)',
        -8888: 'Общая ошибка',
    }

    if code >= 0:
        return 'Нормальное завершение'

    if code not in errors:
        return 'Неизвестная ошибка'

    return errors[code]


class IrbisError(Exception):
    """
    Исключнение - ошибка протокола.
    """

    __slots__ = ('code', 'message')

    def __init__(self, code: 'Union[int, str]' = 0) -> None:
        super().__init__(self)
        if isinstance(code, int):
            self.code: int = code
        if isinstance(code, str):
            self.message: str = code

    def __str__(self):
        if self.message is not None:
            return self.message
        return f'{self.code}: {get_error_description(self.code)}'


class IrbisFileNotFoundError(IrbisError):
    """
    Файл на сервере не найден.
    """

    __slots__ = ('filename',)

    def __init__(self, filename: 'Union[str, FileSpecification]') -> None:
        super().__init__()
        self.filename: str = str(filename)

    def __str__(self):
        return f'File not found: {self.filename}'


__all__ = ['IrbisError', 'IrbisFileNotFoundError']
