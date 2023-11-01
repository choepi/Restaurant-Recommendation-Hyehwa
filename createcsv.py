import pandas as pd
import numpy as np
import random

# Set random seed for reproducibility
np.random.seed(42)

# Generate random data
num_samples = 100
restaurant_names = [f"Restaurant {i}" for i in range(1, num_samples + 1)]
lats = [37.5822 + random.uniform(-0.01, 0.01) for _ in range(num_samples)]  # Around Hyehwa
lons = [126.9988 + random.uniform(-0.01, 0.01) for _ in range(num_samples)]  # Around Hyehwa
review_points = [random.uniform(0, 5) for _ in range(num_samples)]
reviews = [f"Review for {name}" for name in restaurant_names]

# Random categories for the restaurants
categories = ['Korean', 'Western', 'Chinese', 'Japanese', 'Fast Food', 'Seafood', 'Dessert', 'Beverages', 'Barbecue', 'Vegetarian']
restaurant_categories = [random.choice(categories) for _ in range(num_samples)]

# Random values for the "Kids" column
kids_options = ['Yes', 'No']
kids_values = [random.choice(kids_options) for _ in range(num_samples)]

# Create DataFrame
data = {
    'Name': restaurant_names,
    'Lat': lats,
    'Lon': lons,
    'Review_Point': review_points,
    'Review': reviews,
    'Category': restaurant_categories,
    'Kids': kids_values
}
df = pd.DataFrame(data)

# Save to CSV
df.to_csv('sample_data.csv', index=False)
