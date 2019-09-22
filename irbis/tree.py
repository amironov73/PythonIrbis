# coding: utf-8

"""
Работа с TRE-файлами.
"""

from typing import Iterable, List, Optional
from ._common import ANSI, safe_str


class TreeNode:
    """
    TRE-file line.
    """

    __slots__ = 'children', 'value', 'level'

    def __init__(self, value: Optional[str] = None, level: int = 0) -> None:
        self.children: List = []
        self.value: Optional[str] = value
        self.level: int = level

    def add(self, name: str):
        """
        Add a child node.

        :param name: Name of the child.
        :return: Added subnode
        """

        result = TreeNode(name)
        self.children.append(result)
        return result

    def write(self) -> List[str]:
        """
        Represent the node and its child as lines.

        :return: List of lines
        """
        result = [TreeFile.INDENT * self.level + safe_str(self.value)]
        for child in self.children:
            inner = child.write()
            result.extend(inner)
        return result

    def __str__(self):
        return self.value


class TreeFile:
    """
    TRE-file.
    """

    INDENT = '\u0009'

    __slots__ = ('roots',)

    def __init__(self):
        self.roots: List[TreeNode] = []

    @staticmethod
    def _count_indent(text: str) -> int:
        result = 0
        for char in text:
            if char == TreeFile.INDENT:
                result += 1
            else:
                break
        return result

    @staticmethod
    def _arrange_level(nodes: List[TreeNode], level: int) -> None:
        count = len(nodes)
        index = 0
        while index < count:
            index = TreeFile._arrange_nodes(nodes, level, index, count)

    @staticmethod
    def _arrange_nodes(nodes: List[TreeNode], level: int,
                       index: int, count: int) -> int:
        nxt = index + 1
        level2 = level + 1
        parent = nodes[index]
        while nxt < count:
            child = nodes[nxt]
            if child.level <= level:
                break
            if child.level == level2:
                parent.children.append(child)
            nxt += 1
        return nxt

    def add(self, name: str) -> TreeNode:
        """
        Add zero level node with specified name.

        :param name: Name of the node
        :return: Created node
        """

        result = TreeNode(name)
        self.roots.append(result)
        return result

    @staticmethod
    def determine_level(nodes: Iterable[TreeNode], current: int) -> None:
        """
        Determine level of the nodes.

        :param nodes: Nodes to process
        :param current: Current level
        :return: None
        """

        for node in nodes:
            node.level = current
            TreeFile.determine_level(node.children, current + 1)

    def parse(self, text: Iterable[str]) -> None:
        """
        Parse the text for the tree structure.

        :param text: Text to parse
        :return: None
        """

        nodes = []
        for line in text:
            level = TreeFile._count_indent(line)
            line = line[level:]
            node = TreeNode(line, level)
            nodes.append(node)

        max_level = max(node.level for node in nodes)
        for level in range(max_level):
            TreeFile._arrange_level(nodes, level)

        for node in nodes:
            if node.level == 0:
                self.roots.append(node)

    def save(self, filename: str) -> None:
        """
        Save the tree to the specified file.

        :param filename: Name of the file
        :return: None
        """

        with open(filename, 'wt', encoding=ANSI) as stream:
            text = str(self)
            stream.write(text)

    def __str__(self):
        TreeFile.determine_level(self.roots, 0)
        result = []
        for node in self.roots:
            result.extend(node.write())
        return '\n'.join(result)


def load_tree_file(filename: str) -> TreeFile:
    """
    Load the tree from the specified file.

    :param filename: Name of the file.
    :return: Tree structure
    """

    result = TreeFile()
    with open(filename, 'rt', encoding=ANSI) as stream:
        lines = stream.readlines()
        result.parse(lines)
    return result


__all__ = ['load_tree_file', 'TreeFile', 'TreeNode']
