from tkinter import *

FONT = ('Segoe UI', 10)

window = Tk()
window.title('Gaming Time Converter')
window.minsize(width= 400, height= 200)

subtitle = Label(text='Hours played. Days revealed.', font= FONT)
subtitle.grid(column=5, row=0)

choose = Entry(width= 10)
choose.grid(column=2, row=1)

hours = Label(text= 'Hours', font= FONT)
hours.grid(column=3, row=1)







window.mainloop()