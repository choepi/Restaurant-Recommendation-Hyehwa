import tkinter as tk

class SampleApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        # Create a container frame to hold the pages
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # Create a dictionary to hold pages
        self.pages = {}
        
        # Create and add pages to the dictionary
        for PageClass in (StartPage, PageOne, PageTwo):
            page_name = PageClass.__name__
            page = PageClass(parent=container, controller=self)
            self.pages[page_name] = page
            page.grid(row=0, column=0, sticky="nsew")
        
        self.show_page("StartPage")
    
    def show_page(self, page_name):
        page = self.pages[page_name]
        page.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Welcome to the Start Page")
        label.pack(pady=100, padx=100)
        
        button1 = tk.Button(self, text="Go to Page One",
                            command=lambda: controller.show_page("PageOne"))
        button2 = tk.Button(self, text="Go to Page Two",
                            command=lambda: controller.show_page("PageTwo"))
        button1.pack()
        button2.pack()

class PageOne(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Welcome to Page One")
        label.pack(pady=100, padx=100)
        
        button = tk.Button(self, text="Back to Start Page",
                           command=lambda: controller.show_page("StartPage"))
        button.pack()

class PageTwo(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        label = tk.Label(self, text="Welcome to Page Two")
        label.pack(pady=100, padx=100)
        
        button = tk.Button(self, text="Back to Start Page",
                           command=lambda: controller.show_page("StartPage"))
        button.pack()

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
    #cd D:\RDMS\RDBMS_Project\
    #pyinstaller --onefile --noconsole D:\RDMS\RDBMS_Project\main.py

