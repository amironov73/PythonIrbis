# coding: utf-8

from tkinter import *
import irbis

root = Tk()
root.title('Поиск по ЭК')
root.geometry('400x300')

label1 = Label(text='Ключевое слово', justify=LEFT)
label1.place(x=10, y=5)

keyword = StringVar()
input1 = Entry(textvariable=keyword)
input1.place(x=10, y=25, width=280)

button1 = Button(text='Найти')
button1.place(x=300, y=25, width=90)

label2 = Label(text='Найденные записи')
label2.place(x=10, y=55, anchor='nw')

output1 = Listbox()
output1.place(x=10, y=75, width=380, height=200)


def do_search():

    if output1.size():
        output1.delete(0, last=output1.size()-1)

    connection = irbis.Connection()
    connection.host = '192.168.7.13'
    connection.port = 6666
    connection.username = 'librarian'
    connection.password = 'secret'
    connection.database = 'IBIS'
    connection.workstation = 'C'
    connection.connect()
    if not connection.connected:
        output1.insert(END, "Не удалось подключиться")
        return

    expression = '"K=' + keyword.get().strip() + '"'
    found = connection.search(expression)
    if len(found) > 10:
        found = found[:10]

    for mfn in found:
        line = connection.format_record("@sbrief", mfn)
        output1.insert(END, line)

    if not found:
        output1.insert(END, "Ничего не найдено")

    connection.disconnect()


button1.config(command=do_search)

root.mainloop()
