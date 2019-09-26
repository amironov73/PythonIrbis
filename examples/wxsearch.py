# coding: utf-8

import wx

import irbis


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
        self.listbox.Clear()
        keyword = self.input.GetValue()
        if not keyword:
            self.listbox.Append("Не задано ключевое слово")
            return

        connection = irbis.Connection()
        connection.host = '192.168.7.13'
        connection.port = 6666
        connection.username = 'librarian'
        connection.password = 'secret'
        connection.database = 'IBIS'
        connection.workstation = irbis.CATALOGER
        connection.connect()
        if not connection.connected:
            self.listbox.Append("Не удалось подключиться")
            return

        expression = '"K=' + keyword + '"'
        found = connection.search(expression)
        if len(found) > 10:
            found = found[:10]

        for mfn in found:
            line = connection.format_record("@sbrief", mfn)
            self.listbox.Append(line)
        if not found:
            self.listbox.Append("Ничего не найдено")

        connection.disconnect()


app = wx.App()
wnd = Window()
app.MainLoop()
