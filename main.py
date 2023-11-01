# pip install folium
# pip install geocoder
# pip install mysql-connector-python
# pip install tkintermapview
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
from tkintermapview import TkinterMapView
import numpy as np
import math
from math import sin, cos, sqrt, atan2, radians

class NaverApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("1000x800")
        self.title("NaverFood")
        self.iconbitmap("RDBMS_Project/naverfood.ico")
        
        # Create a container frame to hold the pages
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # Create a notebook for tabs
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)
        
        # Load the CSV data into a pandas DataFrame
        self.database = pd.read_csv('RDBMS_Project/sample_data.csv')

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
        

        # Create a TkinterMapView widget
        MAP_WIDTH = 500  # Adjusted width
        MAP_HEIGHT = 400  # Adjusted height
        script_directory = os.path.dirname(os.path.abspath(__file__))
        database_path = os.path.join(script_directory, "offline_tiles_hye.db")
        self.map_widget = TkinterMapView(width=MAP_WIDTH, height=MAP_HEIGHT, corner_radius=1,database_path=database_path, max_zoom=15)
        self.map_widget.set_address("Hyehwa Station, Seoul, South Korea")
        self.map_widget.pack(fill="both", expand=True, padx=10, pady=10)
        # Multiple-choice radio buttons for filtering
        self.filter_label = tk.Label(self, text="Filter by Category:")
        self.filter_label.pack(pady=5)
        

        # Search input
        self.search_label = tk.Label(self, text="Enter Lat Lon")
        self.search_label.pack(pady=5)

        # Create a Text widget to display messages
        self.message_text = tk.Text(self, height=1, width=50)
        self.message_text.pack_forget()
        
        self.search_entry = tk.Entry(self)
        self.search_entry.pack(pady=5)


        # Create a new frame for the category radio buttons
        category_frame = tk.Frame(self)
        category_frame.pack(pady=10)
        # Initialize the selected_category variable
        self.selected_category = tk.StringVar()
        # Fetch unique categories from the database
        if 'Category' in self.controller.database.columns:
            categories = self.controller.database['Category'].unique().tolist()
        else:
            categories = ["None"]

        # Define the number of categories per row
        categories_per_row = 5
        for index, category in enumerate(categories):
            radiobutton = tk.Radiobutton(category_frame, text=category, variable=self.selected_category, value=category)
            row_idx = index // categories_per_row
            col_idx = index % categories_per_row
            radiobutton.grid(row=row_idx, column=col_idx, sticky="w", padx=5, pady=5)
        
        
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
        '''
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
        '''
    
    def perform_search(self):
        # Fetch the clicked location from the map
        input_text = self.search_entry.get()
        self.go = 1
        if not input_text:
            self.go = 0
            message = "Please enter a valid location."
        else:
            try:
                lat, lon = input_text.split()
                message = f"selected:Lat: {lat}, Lon: {lon}"
            except ValueError:
                self.go = 0
                message = "Invalid input format. Please enter Lat and Lon separated by a space."

        # Show the Text widget and insert the message
        self.message_text.delete(1.0, tk.END)
        self.message_text.pack()
        self.message_text.insert(tk.END, message)
        filter_category = self.selected_category.get() if self.selected_category.get() != "None" else None
        
        # Pass the English and Kids options to the SearchResult for filtering
        english = self.english_option.get()
        kids = self.kids_option.get()
        
        
        
        
        if self.go == 1:
            self.message_text.delete(1.0, tk.END)
            lat, lon = input_text.split()
            message = f"selected:Lat: {lat}, Lon: {lon}"
            self.message_text.insert(tk.END, message)
            # Switch to thse SearchResult
            self.controller.show_page("SearchResult")
        
            # Pass the search criteria to the SearchResult and perform the search there
            search_page = self.controller.pages["SearchResult"]
            search_page.perform_search(lat,lon,filter_category, english, kids)
    
class SearchResult(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.no_results_label = tk.Label(self, text="", fg="red")
        self.no_results_label.pack()

        self.search_label = tk.Label(self, text="Search Results:")
        self.search_label.pack(pady=10)
        
        self.results_listbox = tk.Listbox(self, height=15, width=100)
        self.results_listbox.pack(pady=10)
        
        self.scrollbar = tk.Scrollbar(self, command=self.results_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        
        self.results_listbox.config(yscrollcommand=self.scrollbar.set)
        self.results_listbox.bind("<Double-Button-1>", self.select_result)

    def perform_search(self, lat, lon, category, english, kids):
        # Filter the results based on the search criteria from the database (pandas DataFrame)
        self.filtered_data = self.controller.database

        if category and category != "None":
            self.filtered_data = self.filtered_data[self.filtered_data['Category'] == category]

        # Additional filters based on English and Kids options
        if english == "Yes":
            self.filtered_data = self.filtered_data[self.filtered_data['English'] == 'Yes']
        if kids == "Yes":
            self.filtered_data = self.filtered_data[self.filtered_data['Kids'] == 'Yes']

        # Clear the previous results in the Listbox
        self.results_listbox.delete(0, tk.END)
        def haversine(lat1, lon1, lat2, lon2):
            # Convert latitude and longitude from degrees to radians
            lat1 = radians(lat1)
            lon1 = radians(lon1)
            lat2 = radians(lat2)
            lon2 = radians(lon2)

            # Radius of the Earth in kilometers
            R = 6371.0

            # Differences in latitude and longitude
            dlat = lat2 - lat1
            dlon = lon2 - lon1

            # Haversine formula
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            # Calculate the distance
            distance = R * c

            return distance
        

        if not self.filtered_data.empty:
            # Calculate distances between the clicked location and each restaurant
            # (You may need to adjust this part to access the correct database)
            self.filtered_data['Distance'] = self.filtered_data.apply(
                lambda row: haversine(float(lat), float(lon), row['Lat'], row['Lon']),
                    axis=1)

            # Sort the filtered data by distance
            sorted_data = self.filtered_data.sort_values(by='Distance').head(10)

            # Display the sorted results in the Listbox
            for _, row in sorted_data.iterrows():
                d = row['Distance']
                if d>1:
                    distance = str(round(row['Distance'], 2)) + "km"
                else:
                    distance = str(round(row['Distance']*1000, 2)) + "m"
                review_point = round(row['Review_Point'], 2)
                display_text = f"{row['Name']} (Category: {row['Category']}, Distance: {distance}, ReviewPoint: {review_point:.2f}, Review: {row['Review']})"
                self.results_listbox.insert(tk.END, display_text)
        else:
            # Show a message if there are no matching results
            self.no_results_label.config(text="No matching results found.")

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
        
        self.result_label = tk.Label(self, text="Chosen Result")
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

    def translate_to_english(self, text):
        translator = LibreTranslate(api_url="https://api_url", api_key="YOUR_API_KEY")
        return translator.translate(text, source_lang="auto", target_lang="en")

    def display_details(self, record):
        # Display the details of the selected result and show its location on the map.
        # Update the result label with the restaurant's name
        self.result_label.config(text=f"Result Page: {record['Name']}")
        
        # If English was selected, translate the review
        review_text = record['Review']
        if self.controller.pages["MainPage"].english_option.get() == "Yes":
            review_text = self.translate_to_english(review_text)
        
        # Display the (possibly translated) review (you can adjust this to show it in a GUI element)
        print(f"Review: {review_text}")
        
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

