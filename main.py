# pip install -r requirements.txt
# pip freeze > requirements.txt (only run to update requirements.txt)
import requests
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import webbrowser
import folium
import os
import geocoder
import mysql.connector
import pandas as pd
from tkintermapview import TkinterMapView
import numpy as np
import mysql.connector
from transformers import MarianMTModel, MarianTokenizer
from typing import Sequence

def connectDB(db_use):
    mydb = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '1083', # have to change
    database = db_use
    )
    mycursor = mydb.cursor()
    return mydb, mycursor

mydb, mycursor = connectDB('project')

def calculator_distance(para) :
    def haversine1(loc1, loc2):
        lat1 = loc1[0]
        lon1 = loc1[1]
        lat2 = loc2[0]
        lon2 = loc2[1]
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

        c = 2 * np.arcsin(np.sqrt(a))
        radius_earth = 6371000  # Earth's radius in meters
        distances = c * radius_earth
        return np.round(distances,1)
    
    
    mydb, mycursor = connectDB('project')
    
    mycursor.execute("SELECT lat, lon FROM restaurant")
    myResult = mycursor.fetchall()
    location = list(myResult)
    #location list = my sql query with category
    mycursor.execute("SELECT category_id FROM restaurant")
    myResult = mycursor.fetchall()
    catintup = list(myResult)
    restaurant_list = []
    #create dataframe df with 2 columns id and distance, length of location

    catintup = [int(str(i).replace('(', '').replace(')', '').replace(',', '')) for i in catintup]
    df = pd.DataFrame({
    'id': range(1,len(location)+1),
    'distance': range(len(location)),
    'category': catintup}) 

    df['distance'] = [haversine1(para, loc) for loc in location]  # Calculate distances
    #filter after category, where category in category_subquery
    df = df[df['category'].isin(category_subquery)]
    # Sort by distance and get top 5
    df = df.sort_values(by='distance').head(5)
    restaurant_list = df['id'].tolist()
    return restaurant_list

def translate_korean_to_english(korean_text):
    url = "https://google-translate1.p.rapidapi.com/language/translate/v2"
        
    payload = {
        "q": korean_text,
        "target": "en",
        "source": "ko"
    }
    headers = {
        "content-type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "application/gzip",
        "X-RapidAPI-Key": "2f168c8413msh98205027eeeb4d9p1410bejsn6f4d9cf9b76e",
        "X-RapidAPI-Host": "google-translate1.p.rapidapi.com"
    }

    response = requests.post(url, data=payload, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result['data']['translations'][0]['translatedText']
    else:
        return "Error: Unable to translate"

class NaverApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("800x600")
        self.title("NaverFood")
        # self.iconbitmap("C:/Users/Admin/OneDrive/바탕 화면/RDBMS_Project/naverfood.ico")
        
        # Create a container frame to hold the pages
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        
        # Create a notebook for tabs
        self.notebook = ttk.Notebook(container)
        self.notebook.pack(fill="both", expand=True)
        
        # Load the CSV data into a pandas DataFrame
        # self.database = pd.read_csv('RDBMS_Project/sample_data.csv')    

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


class Translator:
    def __init__(self, source_lang: str, dest_lang: str) -> None:
        self.model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{dest_lang}'
        self.model = MarianMTModel.from_pretrained(self.model_name)
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        
    def translate(self, texts: Sequence[str]) -> Sequence[str]:
        tokens = self.tokenizer(list(texts), return_tensors="pt", padding=True)
        translate_tokens = self.model.generate(**tokens)
        return [self.tokenizer.decode(t, skip_special_tokens=True) for t in translate_tokens]
translator = Translator('ko', 'en')


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
        self.message_text.config(state="disabled")
        self.message_text.pack_forget()
        
        self.search_entry = tk.Entry(self)
        current_location = geocoder.ip('me').latlng
        current_location = ' '.join(map(str, current_location))
        self.search_entry.insert(0, current_location)
        self.search_entry.bind("<Return>", lambda event: self.perform_search())
        self.search_entry.pack(pady=5)

        self.cat_num = 0
        # Create a new frame for the category radio buttons
        category_frame = tk.Frame(self)
        category_frame.pack(pady=10)
        # Initialize the selected_category variable
        self.selected_category = tk.StringVar()
        self.selected_category.set('None')
        # Fetch unique categories from the database
        mycursor.execute("SELECT category FROM category")
        myResult = mycursor.fetchall()
        categories = list(myResult) # cafe & dessert question
        categories.insert(0, 'None')
        self.categories =  [i[0] if isinstance(i, tuple) else i for i in categories]

        # category search function
        def category_search():
            def tuptoval(tup):
                val = []
                for o in tup:
                    v = o[0] if isinstance(o, tuple) else o
                    val.append(int(v))
                return val
            global category_subquery
            if self.selected_category.get() != "None" :
                selected_category_str = self.selected_category.get()
                # Strip curly braces if they are present
                cleaned_str = selected_category_str.strip("{}")
                mycursor.execute("Select category_id FROM category WHERE category='"+str(cleaned_str+"'"))
                category = mycursor.fetchall()
                category = tuptoval(category)
                category_subquery = list(category)
            else:
                mycursor.execute("Select DISTINCT(category_id) FROM category")
                category = mycursor.fetchall()
                category = tuptoval(category)
                category_subquery = (category)

        # Define the number of categories per row
        categories_per_row = 5
        category_search()
        for index, category in enumerate(categories):
            radiobutton = tk.Radiobutton(category_frame, text=category, variable= str(self.selected_category), value=category, command = category_search) #quesition
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
        
        # Search button
        self.search_button = tk.Button(self, text="Search", command=self.perform_search)
        self.search_button.pack(pady=10)
        
        self.exit_button = tk.Button(self, text="Exit", command=self.controller.quit)
        self.exit_button.pack()

    def perform_search(self):
        # Fetch the clicked location from the map
        input_text = self.search_entry.get()
        self.go = 1
        if not input_text:
            self.go = 0 # question
            message = "Please enter a valid location."
        else:
            try:
                x = input_text.split(' ')
                lat = x[0]
                lon = x[1]
                message = f"selected:Lat: {lat}, Lon: {lon}"

            except ValueError:
                self.go = 0
                message = "Invalid input format. Please enter Lat and Lon separated by a space."

        # Show the Text widget and insert the message
        self.message_text.delete(1.0, tk.END)
        self.message_text.pack()
        self.message_text.config(state="normal")
        self.message_text.insert(tk.END, message)
        self.message_text.config(state="disabled")
        
        # Pass the English options to the SearchResult for filtering
        english = self.english_option.get()
        
        
        if self.go == 1:
            self.message_text.delete(1.0, tk.END)
            x = input_text.split(' ')
            lat = x[0]
            lon = x[1]
            message = f"selected:Lat: {lat}, Lon: {lon}"
            self.message_text.insert(tk.END, message)
            # Switch to thse SearchResult
            self.controller.show_page("SearchResult")
        
            # Pass the search criteria to the SearchResult and perform the search there
            search_page = self.controller.pages["SearchResult"]
            for i in self.categories:
                selected_category_str = self.selected_category.get()
                # Strip curly braces if they are present
                cleaned_str = selected_category_str.strip("{}")
                if i == cleaned_str:
                    self.cat_num = self.categories.index(i)
            search_page.perform_search(lat,lon, self.cat_num, english)


dataframe_name = ['category_id', 'point_average']
mycursor.execute("""SELECT c.category_id, avg(s.starRating) FROM score s
                    JOIN restaurant r ON r.restaurant_id = s.restaurant_id
                    JOIN category c ON r.category_id = c.category_id 
                    WHERE s.starRating != 0 
                    GROUP BY c.category_id
                    ORDER BY c.category_id""")
point_average = mycursor.fetchall()
category_starpoint = pd.DataFrame(point_average, columns = dataframe_name)

# calculate starpoint
def starpoint(restaurant_id, category_id):
    query = """SELECT s.starRating FROM score s
                JOIN restaurant r ON r.restaurant_id = s.restaurant_id
                WHERE r.restaurant_id = {}""".format(str(restaurant_id))
    mycursor.execute(query)
    point = mycursor.fetchone()

    if point == ("",):
        text = "None"
    else:
        point = float(point[0])
        category_point_series = category_starpoint.loc[category_starpoint['category_id'] == category_id]['point_average']
        
        # Check if the Series is not empty before accessing its element
        if not category_point_series.empty:
            category_point = float(category_point_series.iloc[0])
            if point > category_point:
                text = 'Low'
            elif point == category_point:
                text = 'Same'
            else:
                text = 'High'
        else:
            text = 'Data Not Found'
        
    return text



class SearchResult(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        self.no_results_label = tk.Label(self, text="", fg="red")
        self.no_results_label.pack()

        self.search_label = tk.Label(self, text="Search Results:")
        self.search_label.pack(pady=10)

        self.results_listbox = tk.Listbox(self, height=15, width=100)
        #for i in range(5) :
        #   self.results_listbox.insert(tk.END, restaurant[i])
        self.results_listbox.pack(pady=10)
        
        self.scrollbar = tk.Scrollbar(self, command=self.results_listbox.yview)
        self.scrollbar.pack(side="right", fill="y")
        
        self.results_listbox.config(yscrollcommand=self.scrollbar.set)
        self.results_listbox.bind("<Double-Button-1>", self.select_result)
        self.selected_record = None

    def perform_search(self, lat, lon, category, english): # question
        self.no_results_label.config(text="")
        self.results_listbox.delete(0, tk.END)
        user_location = (float(lat), float(lon))

        restaurant_list = calculator_distance(user_location)
        restaurant=restaurant_list
        if not len(restaurant) == 0 :
            global sorted_data
            # Calculate distances between the clicked location and each restaurant
            # (You may need to adjust this part to access the correct database)
            sorted_data = []
            dataframe_name = ['id', 'Name','Review_Point', 'Category_id', 'Category', 'Lat', 'Lon', 'url']
            mycursor.execute("SELECT rt.restaurant_id, rt.name, s.starRating, c.category_id, c.category, rt.lat, rt.lon, rt.naver_map_url\
                                FROM restaurant rt\
                                JOIN score s using(restaurant_id)\
                                JOIN category c using(category_id)\
                                WHERE rt.restaurant_id IN {} ORDER BY s.starRating DESC".format(tuple(restaurant) if restaurant else (0,)))
            sorted_value = mycursor.fetchall()
            sorted_data = pd.DataFrame(sorted_value, columns = dataframe_name)

            # Display the sorted results in the Listbox
            for i in range(len(sorted_data)):
                display_text = f"{sorted_data.loc[i, 'Name']} (Category: {sorted_data.loc[i, 'Category']}, \
                    ReviewPoint: {sorted_data.loc[i, 'Review_Point']}, {starpoint(sorted_data.loc[i, 'id'], sorted_data.loc[i, 'Category_id'])})"
                self.results_listbox.insert(tk.END, display_text)
        else:
            # Show a message if there are no matching results
            self.no_results_label.config(text="No matching results found.")

    def select_result(self, event):
        # Get the selected result's index
        index = self.results_listbox.curselection()[0]
        global selected_record
        # Fetch the full record from the filtered_data DataFrame based on the index
        selected_record = pd.DataFrame(sorted_data.loc[index])
        
        # Switch to the Result and display the details of the selected result
        self.controller.show_page("Result") # question
        result_page = self.controller.pages["Result"]
        result_page.display_details(selected_record)

class Result(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.url = ''
        
        self.index2 = 0

        self.result_label = tk.Label(self, text="Chosen Result", wraplength=800)
        self.result_label.pack(pady=10)
        self.results_listbox2 = tk.Listbox(self, height=15, width=100)

        self.review_label = tk.Label(self,text="please insert new review!")
        self.review_label.pack(pady=10)
        self.reivewEntry = tk.Entry(self)
        self.reivewEntry.pack(pady=5)
        self.review_button = tk.Button(self,text="update",command=self.insert_review)
        self.review_button.pack(pady=3)

        self.results_listbox2.pack(pady=10)
        self.scrollbar2 = tk.Scrollbar(self, command=self.results_listbox2.yview)
        self.scrollbar2.pack(side="right", fill="y")

        self.results_listbox2.config(yscrollcommand=self.scrollbar2.set)
        self.results_listbox2.bind("<Double-Button-1>", self.select_result2)

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
    
    def insert_review(self):
            new_review = self.reivewEntry.get()
            result = (real_record.id[0],new_review)
            mycursor.execute(f"INSERT INTO review VALUES {result}") 
            mydb.commit() # make the change permanent
            messagebox.showinfo("Confirmation", "Your review has been updated.")

            self.results_listbox2.delete(0, tk.END) # delete result for updating new review
            self.display_details(selected_record) # print new result with inserted review

    def select_result2(self,event):
            # Get the selected result's index
            self.index2 = self.results_listbox2.curselection()[0]
            Result.display_details(self,selected_record)

    def display_details(self, record):
         # Display the details of the selected result and show its location on the map.
        # Update the result label with the restaurant's name
        global real_record
        real_record = record.transpose()
        index = int(real_record.index[0])
        restaurantid = int(real_record.loc[index, 'id'])
        mydb, mycursor = connectDB('project')
        dataframe_name2 = ['id', 'Name', 'Review','Review_Point', 'Category', 'Lat', 'Lon', 'url']
        mycursor.execute(f"SELECT rt.restaurant_id, rt.name, r.review, s.starRating, c.category, rt.lat, rt.lon, rt.naver_map_url\
                            FROM restaurant rt\
                            JOIN review r using(restaurant_id)\
                            JOIN score s using(restaurant_id)\
                            JOIN category c using(category_id)\
                            WHERE rt.restaurant_id = {restaurantid} ORDER BY s.starRating DESC")
        sorted_value = mycursor.fetchall()
        real_record = pd.DataFrame(sorted_value, columns = dataframe_name2)

        self.url = str(real_record.loc[0,'url'])

        self.results_listbox2.delete(0, tk.END)
        for i in range(len(real_record)):
                display_text = f"{real_record.loc[i, 'Review']} "
                self.results_listbox2.insert(tk.END, display_text)

        index2 = self.index2
        review_text = str(real_record.loc[index2,'Review'])
        
        if self.controller.pages["MainPage"].english_option.get() == "Yes":
            marian_ko_en = Translator('ko', 'en') # If you want to see real delay use time.sleep(5)
            review_text = marian_ko_en.translate([review_text])[0] #machine translation
            #text =translate_korean_to_english(review_text) #google translation


        # Display the (possibly translated) review (you can adjust this to show it in a GUI element)
        
        self.result_label.config(text=f"Result Page: {str(real_record.loc[0,'Name'])}\
                                    \n Review: {review_text}")
        
        # Update the map marker to the location of the selected restaurant
        lat = int(real_record.loc[0,'Lat'])
        lon = int(real_record.loc[0,'Lon'])
        self.result_marker.location = [lat, lon]
        self.result_marker.popup = folium.Popup(real_record.loc[0,'Name'])
        
        # Center the map around the selected restaurant's location
        self.map.location = [lat, lon]
        
        # Refresh the map by saving it again
        self.map.save(self.map_filepath)


        
    def copy_to_clipboard(self):
        # Here, for demonstration purposes, I'm copying the first link from "Option 1" in the database. 
        # You can modify this based on your requirements.
        link = self.url
        self.clipboard_clear() # question
        self.clipboard_append(link)
        self.update()  # This is necessary to finalize the clipboard changes
    


if __name__ == "__main__":
    app = NaverApp()
    app.mainloop()

    #cd D:\RDMS\RDBMS_Project\
    #pyinstaller --onefile --noconsole D:\RDMS\RDBMS_Project\main.py

