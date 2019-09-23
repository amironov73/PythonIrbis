# coding: utf-8

"""
Пользователи системы.
"""

from typing import List, Optional
from ._common import safe_str, same_string
from .response import ServerResponse


class UserInfo:
    """
    Информация о зарегистрированном пользователе системы.
    """

    __slots__ = ('number', 'name', 'password', 'cataloger',
                 'reader', 'circulation', 'acquisitions',
                 'provision', 'administrator')

    def __init__(self, name: Optional[str] = None,
                 password: Optional[str] = None) -> None:
        self.number: Optional[str] = None
        self.name: Optional[str] = name
        self.password: Optional[str] = password
        self.cataloger: Optional[str] = None
        self.reader: Optional[str] = None
        self.circulation: Optional[str] = None
        self.acquisitions: Optional[str] = None
        self.provision: Optional[str] = None
        self.administrator: Optional[str] = None

    # noinspection DuplicatedCode
    @staticmethod
    def parse(response: ServerResponse) -> List['UserInfo']:
        """
        Parse the server response for the user info.

        :param response: Response to parse.
        :return: List of user infos.
        """

        result: List = []
        user_count = response.number()
        lines_per_user = response.number()
        if not user_count or not lines_per_user:
            return result
        for _ in range(user_count):
            user: UserInfo = UserInfo()
            user.number = response.ansi()
            user.name = response.ansi()
            user.password = response.ansi()
            user.cataloger = response.ansi()
            user.reader = response.ansi()
            user.circulation = response.ansi()
            user.acquisitions = response.ansi()
            user.provision = response.ansi()
            user.administrator = response.ansi()
            result.append(user)
        return result

    @staticmethod
    def format_pair(prefix: str, value: str, default: str) -> str:
        """
        Format the pair prefix=value.

        :param prefix: Prefix to use
        :param value: Value to use
        :param default: Default value
        :return: Formatted text
        """

        if same_string(value, default):
            return ''

        return prefix + '=' + safe_str(value) + ';'

    def encode(self):
        """
        Encode the user info.

        :return: Text representation of the user info.
        """

        return self.name + '\n' + self.password + '\n' \
            + UserInfo.format_pair('C', self.cataloger, "irbisc.ini") \
            + UserInfo.format_pair('R', self.reader, "irbisr.ini") \
            + UserInfo.format_pair('B', self.circulation, "irbisb.ini") \
            + UserInfo.format_pair('M', self.acquisitions, "irbism.ini") \
            + UserInfo.format_pair('K', self.provision, "irbisk.ini") \
            + UserInfo.format_pair('A', self.administrator, "irbisa.ini")

    def __str__(self):
        buffer = [self.number, self.name, self.password, self.cataloger,
                  self.reader, self.circulation, self.acquisitions,
                  self.provision, self.administrator]
        return ' '.join(x for x in buffer if x)


__all__ = ['UserInfo']
