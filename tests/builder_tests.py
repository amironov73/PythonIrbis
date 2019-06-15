# coding: utf-8

"""
Tests for search expression builder.
"""

from pyirbis.builder import Search, keyword, author, title, number

print(Search.need_wrap(''))
print(Search.need_wrap('Hello'))
print(Search.need_wrap('Hello, world'))

print()

print(Search.wrap(''))
print(Search.wrap('Hello'))
print(Search.wrap('Hello, world'))

print()

print(keyword('Hello'))
print(keyword('Hello', 'world'))
print(keyword('Hello, world'))

print()

print(keyword(1))
print(keyword(1, 2))

print()

print(keyword(1).and_(title(2)))
print(keyword(1,2).and_(title(3,4)))
print(keyword(1).or_(author(2)))
print(keyword(1,2).or_(author(3,4)))

print()

print(keyword(1).not_(number(2)))
print(keyword(1,2).not_(number(3,4)))
