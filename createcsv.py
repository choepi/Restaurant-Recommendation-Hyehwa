import csv
import pandas as pd
import random

# Create sample restaurant names
restaurant_names = [f"Restaurant_{i}" for i in range(100)]

# Adjusted coordinates generation to be centered around Hyehwa, Seoul.
hyehwa_latitude = 37.5822
hyehwa_longitude = 127.0019
variance = 0.01  # about 1km

latitudes = [random.uniform(hyehwa_latitude - variance, hyehwa_latitude + variance) for _ in range(100)]
longitudes = [random.uniform(hyehwa_longitude - variance, hyehwa_longitude + variance) for _ in range(100)]
review_points = [random.randint(1, 5) for _ in range(100)]
reviews = [f"Review for {name}" for name in restaurant_names]

# Sample categories
categories = [
    "Korean", "Chinese", "Japanese", "Western", "Fusion",
    "Fast Food", "Dessert", "Seafood", "Barbecue", "Vegetarian"
]

# Create a pandas DataFrame from the generated data
data = pd.DataFrame({
    "Name": restaurant_names,
    "Latitude": latitudes,
    "Longitude": longitudes,
    "Review Point": review_points,
    "Review": reviews,
    "Category": [random.choice(categories) for _ in range(100)]
})

# Write the data to a CSV file
csv_path = "sample_data.csv"
data.to_csv(csv_path, index=False)
