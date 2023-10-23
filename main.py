from tkinter import *

window = Tk()
window.title('Search Restaurants')
window.geometry('500x500')
label = Label(window, text='Choose Restaurant!', bg='green', font=('Arial', 12), width=30, height=2)
label.pack()
text = Text(window, height=2, font=('courier', 12))
text.pack() 
button = Button(window, text='hit me', font=('Arial', 12), width=10, height=1)
button.pack()
window.mainloop() #keep display window and listen for request




