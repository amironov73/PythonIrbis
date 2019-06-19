# coding: utf-8

import wx

from pyirbis.core import *


class Window(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title="Поиск по ЭК", size=(500, 300))
        panel = wx.Panel(self)
        self.control = panel
        wx.StaticText(panel, label='Ключевое слово', size=(450, 20),
                      pos=(10, 5))
        self.input = wx.TextCtrl(panel, size=(300, 20), pos=(10, 25))
        self.button = wx.Button(panel, label='Поиск', size=(150, 20),
                                pos=(320, 25))
        wx.StaticText(panel, label='Найденные записи', size=(450, 20),
                      pos=(10, 55))
        self.listbox = wx.ListBox(panel, size=(460, 175), pos=(10, 75))
        self.Bind(wx.EVT_BUTTON, self.on_click, self.button)
        self.Show(True)

    # noinspection PyUnusedLocal
    def on_click(self, event):
        keyword = self.input.GetValue()
        connection = Connection()
        connection.host = '127.0.0.1'
        connection.port = 6666
        connection.username = '1'
        connection.password = '1'
        connection.database = 'ISTU'
        connection.workstation = 'C'
        connection.connect()

        expression = "K=" + keyword
        found = connection.search(expression)
        self.listbox.Clear()
        for mfn in found:
            line = connection.format_record("@sbrief", mfn)
            self.listbox.Append(line)

        connection.disconnect()


app = wx.App()
wnd = Window()
app.MainLoop()
