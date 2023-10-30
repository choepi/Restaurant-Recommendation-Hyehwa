# pip install folium
# pip install geocoder
# pip install mysql-connector-python
import requests
import tkinter as tk
from tkinter import ttk
import webbrowser
import folium
import os
import geocoder
import mysql.connector
from translate import LibreTranslate


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
        
        # Mock database with sample search results categorized into three options
        self.database = {
            "Option 1": [
                {"name": "Result 1A", "link": "https://example.com/result1A", "lat": 37.7749, "lon": -122.4194},
                {"name": "Result 1B", "link": "https://example.com/result1B", "lat": 34.0522, "lon": -118.2437},
            ],
            "Option 2": [
                {"name": "Result 2A", "link": "https://example.com/result2A", "lat": 40.7128, "lon": -74.0060},
                {"name": "Result 2B", "link": "https://example.com/result2B", "lat": 41.8781, "lon": -87.6298},
            ],
            "Option 3": [
                {"name": "Result 3A", "link": "https://example.com/result3A", "lat": 51.5074, "lon": -0.1278},
                {"name": "Result 3B", "link": "https://example.com/result3B", "lat": 48.8566, "lon": 2.3522},
            ]
        }
                
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
        categories = ["None", "Category A", "Category B", "Category C"]
        for category in categories:
            radiobutton = tk.Radiobutton(self, text=category, variable=self.selected_category, value=category)
            radiobutton.pack(anchor="w")
        
        # Search button
        self.search_button = tk.Button(self, text="Search", command=self.perform_search)
        self.search_button.pack(pady=10)
        
        self.exit_button = tk.Button(self, text="Exit", command=self.controller.quit)
        self.exit_button.pack()
    
    def load_csv_to_db(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return

        # Load the CSV file into a pandas DataFrame
        data = pd.read_csv(file_path)

        # Connect to MySQL
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1083"
        )
        cursor = conn.cursor()

        # Insert the data into the MySQL table
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
    
    def fetch_data_from_db(self, query=None, category=None):
        # Mock function simulating fetching data from the database based on search criteria.
        # In a real scenario, this function would interact with your database.
        mock_data = [
            {"name": "Item 1", "category": "Category A"},
            {"name": "Item 2", "category": "Category B"},
            {"name": "Item 3", "category": "Category C"}
        ]
        if query:
            mock_data = [item for item in mock_data if query.lower() in item["name"].lower()]
        if category:
            mock_data = [item for item in mock_data if category == item["category"]]
        return mock_data

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
        
        self.exit_button = tk.Button(self, text="Exit", command=self.controller.quit)
        self.exit_button.pack()

    def perform_search(self, query, category):
        # Here, fetch the results based on the search criteria and display them in the Listbox.
        # For demonstration, we're using mock data.
        mock_results = ["Result 1", "Result 2", "Result 3", "Result 4"]  # Replace with actual results
        for result in mock_results:
            self.results_listbox.insert(tk.END, result)

    def select_result(self, event):
        # Get the selected result
        selected_result = self.results_listbox.get(self.results_listbox.curselection())
        
        # Switch to the Result and display the details of the selected result
        self.controller.show_page("Result")
        Result = self.controller.pages["Result"]
        Result.display_details(selected_result)

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

    def display_details(self, result):
        # Display the details of the selected result and show its location on the map.
        # For demonstration, we're just printing the result. You can enhance this to fetch more details
        # and display them in the GUI, as well as update the map location.
        print(f"Displaying details for: {result}")
        # Here, update the GUI widgets and map to reflect the details of the selected result.

    def copy_to_clipboard(self):
        # Here, for demonstration purposes, I'm copying the first link from "Option 1" in the database. 
        # You can modify this based on your requirements.
        link = self.controller.database["Option 1"][0]["link"]
        self.clipboard_clear()
        self.clipboard_append(link)
        self.update()  # This is necessary to finalize the clipboard changes


if __name__ == "__main__":
    app = NaverApp()
    app.mainloop()

    #cd D:\RDMS\RDBMS_Project\
    #pyinstaller --onefile --noconsole D:\RDMS\RDBMS_Project\main.py

