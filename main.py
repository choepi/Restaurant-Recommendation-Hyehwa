# pip install folium
# pip install geocoder
# pip install mysql-connector-python
import requests
import tkinter as tk
from tkinter import ttk, filedialog
import webbrowser
import folium
import os
import geocoder
import mysql.connector
from translate import LibreTranslate
import pandas as pd

class NaverApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("NaverFood")
        self.iconbitmap("RDBMS_Project/naverfood.png")
        
        # Create a container frame to hold the pages
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # Create a notebook for tabs
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)
        
        # Load the CSV data into a pandas DataFrame
        self.database = pd.read_csv('sample_data.csv')
        print(self.database)
        # Create a dictionary to hold pages 
        self.pages = {}
        
        # Create and add pages to the dictionary
        for PageClass in (MainPage, SearchResult, Result):
            page_name = PageClass.__name__
            page = PageClass(parent=self.notebook, controller=self)
            self.pages[page_name] = page
            self.notebook.add(page, text=page_name)
        
        self.show_page("MainPage")
    
    def show_page(self, page_name):
        page = self.pages[page_name]
        self.notebook.select(page)

class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.title_label = tk.Label(self, text="Main Page: Title")
        self.title_label.pack(pady=10)
        
        # Search input
        self.search_label = tk.Label(self, text="Search:")
        self.search_label.pack(pady=5)
        
        self.search_entry = tk.Entry(self)
        self.search_entry.pack(pady=5)
        
        # Multiple-choice radio buttons for filtering with a default "None" option
        self.filter_label = tk.Label(self, text="Filter by Category:")
        self.filter_label.pack(pady=5)
        
        self.selected_category = tk.StringVar(value="None")  # Default is "None"
        
        # Fetch unique categories from the database
        if 'Category' in self.controller.database.columns:
            categories = ["None"] + self.controller.database['Category'].unique().tolist()
        else:
            categories = ["None", "Category A", "Category B", "Category C"]
        
        for category in categories:
            radiobutton = tk.Radiobutton(self, text=category, variable=self.selected_category, value=category)
            radiobutton.pack(anchor="w")
        
        # Radio buttons for English and Kids options
        self.english_label = tk.Label(self, text="English:")
        self.english_label.pack(pady=5)
        self.english_option = tk.StringVar(value="No")
        for option in ["Yes", "No"]:
            radiobutton = tk.Radiobutton(self, text=option, variable=self.english_option, value=option)
            radiobutton.pack(anchor="w")

        self.kids_label = tk.Label(self, text="Kids:")
        self.kids_label.pack(pady=5)
        self.kids_option = tk.StringVar(value="No")
        for option in ["Yes", "No"]:
            radiobutton = tk.Radiobutton(self, text=option, variable=self.kids_option, value=option)
            radiobutton.pack(anchor="w")
        
        # Search button
        self.search_button = tk.Button(self, text="Search", command=self.perform_search)
        self.search_button.pack(pady=10)
        
        self.exit_button = tk.Button(self, text="Exit", command=self.controller.quit)
        self.exit_button.pack()

    def load_csv_to_db(self):
        # Load the CSV file into a pandas DataFrame
        data = self.database

        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password"
        )
        cursor = conn.cursor()

        # Insert the data into the MySQL table (you'll need to adjust the placeholders and columns accordingly)
        for index, row in data.iterrows():
            cursor.execute("INSERT INTO your_table_name (column1, column2, ...) VALUES (%s, %s, ...)", 
                           (row['column1'], row['column2'], ...))

        conn.commit()
        cursor.close()
        conn.close()
    
    def perform_search(self):
        query = self.search_entry.get() or None
        filter_category = self.selected_category.get() if self.selected_category.get() != "None" else None
        
        # Switch to the SearchResult
        self.controller.show_page("SearchResult")
        
        # Pass the search criteria to the SearchResult and perform the search there
        search_page = self.controller.pages["SearchResult"]
        search_page.perform_search(query, filter_category)  
    
class SearchResult(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.search_label = tk.Label(self, text="Search Results:")
        self.search_label.pack(pady=10)
        
        self.results_listbox = tk.Listbox(self, height=10, width=50)
        self.results_listbox.pack(pady=10)
        
        self.scrollbar = tk.Scrollbar(self, command=self.results_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        
        self.results_listbox.config(yscrollcommand=self.scrollbar.set)
        self.results_listbox.bind("<Double-Button-1>", self.select_result)

    def perform_search(self, query, category):
        # Filter the results based on the search criteria from the database (pandas DataFrame)
        self.filtered_data = self.controller.database
        
        if query:
            self.filtered_data = self.filtered_data[self.filtered_data['Name'].str.contains(query, case=False)]
            
        if category and category != "None":
            self.filtered_data = self.filtered_data[self.filtered_data['Category'] == category]
        
        # Display the filtered results in the Listbox
        for _, row in self.filtered_data.iterrows():
            display_text = f"{row['Name']} (Lat: {row['Lat']}, Lon: {row['Lon']})"
            self.results_listbox.insert(tk.END, display_text)

    def select_result(self, event):
        # Get the selected result's index
        index = self.results_listbox.curselection()[0]
        
        # Fetch the full record from the filtered_data DataFrame based on the index
        selected_record = self.filtered_data.iloc[index]
        
        # Switch to the Result and display the details of the selected result
        self.controller.show_page("Result")
        result_page = self.controller.pages["Result"]
        result_page.display_details(selected_record)

class Result(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        
        self.result_label = tk.Label(self, text="Result Page: Chosen Result")
        self.result_label.pack(pady=10)
        
        # Button to copy the link to clipboard
        self.copy_button = tk.Button(self, text="Copy Name and Link to Clipboard", command=self.copy_to_clipboard)
        self.copy_button.pack(pady=10)
        
        # Create a map centered around Seoul (or you can center it around the user's location)
        self.map = folium.Map(location=[37.5665, 126.9780], zoom_start=10)
        
        # Create a marker for the search result (Seoul's coordinates as a placeholder)
        self.result_marker = folium.Marker([37.5665, 126.9780], popup="Search Result")
        self.result_marker.add_to(self.map)
        
        # Get current location and add a marker for it
        current_location = geocoder.ip('me').latlng
        if current_location:
            folium.Marker(
                location=current_location,
                popup="You are here!",
                icon=folium.Icon(color="green")
            ).add_to(self.map)
        
        # Save the map to an HTML file
        self.map_filepath = "map.html"
        self.map.save(self.map_filepath)
        
        # Button to open the map in a browser
        self.view_map_button = tk.Button(self, text="View Map", command=lambda: webbrowser.open('file://' + os.path.realpath(self.map_filepath)))
        self.view_map_button.pack(pady=10)
        
        self.exit_button = tk.Button(self, text="Exit", command=self.controller.quit)
        self.exit_button.pack()

    def display_details(self, record):
        # Display the details of the selected result and show its location on the map.
        # Update the result label with the restaurant's name
        self.result_label.config(text=f"Result Page: {record['Name']}")
        
        # Update the map marker to the location of the selected restaurant
        self.result_marker.location = [record['Lat'], record['Lon']]
        self.result_marker.popup = folium.Popup(record['Name'])
        
        # Center the map around the selected restaurant's location
        self.map.location = [record['Lat'], record['Lon']]
        
        # Refresh the map by saving it again
        self.map.save(self.map_filepath)

    def copy_to_clipboard(self):
        # Here, for demonstration purposes, I'm copying the first link from "Option 1" in the database. 
        # You can modify this based on your requirements.
        link = self.controller.database.loc[0, "Name"]  # Using pandas DataFrame for example
        self.clipboard_clear()
        self.clipboard_append(link)
        self.update()  # This is necessary to finalize the clipboard changes

if __name__ == "__main__":
    app = NaverApp()
    app.mainloop()


    #cd D:\RDMS\RDBMS_Project\
    #pyinstaller --onefile --noconsole D:\RDMS\RDBMS_Project\main.py

