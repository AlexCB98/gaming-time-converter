from tkinter import *

FONT = ('Segoe UI', 10)

window = Tk()
window.title('Gaming Time Converter')
window.minsize(width= 300, height= 100)

subtitle = Label(text='-> Hours played. Days revealed.', font= FONT)
subtitle.grid(column=0, row=0, columnspan=3)

text_1 = Label(text= 'If you played', font= FONT)
text_1.grid(column=0, row=1, padx=5)

choose = Entry(width= 10)
choose.grid(column=1, row=1, padx=5)

hours_text = Label(text= 'Hours', font= FONT)
hours_text.grid(column=2, row=1, padx=5)

text_2 = Label(text='That means exactly', font= FONT)
text_2.grid(column=0 , row=2, padx=5)

result = Label(text='0', font= FONT)
result.grid(column=1, row=2, padx=5)

days_text = Label(text='Day/s', font= FONT)
days_text.grid(column=2, row=2, padx=5)

def converter():
    result['text'] = round((float(choose.get()) / 24), 2)

button = Button(text='Convert', command=converter)
button.grid(column=1, row=3)




window.mainloop()