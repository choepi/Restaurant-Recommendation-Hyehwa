import csv
import random

# Create sample restaurant names
restaurant_names = [f"Restaurant_{i}" for i in range(100)]

# Adjusted coordinates generation to be centered around Hyehwa, Seoul.
# Coordinates for Hyehwa, Seoul: approximately 37.5822° N, 127.0019° E
hyehwa_latitude = 37.5822
hyehwa_longitude = 127.0019
variance = 0.01  # about 1km

latitudes = [random.uniform(hyehwa_latitude - variance, hyehwa_latitude + variance) for _ in range(100)]
longitudes = [random.uniform(hyehwa_longitude - variance, hyehwa_longitude + variance) for _ in range(100)]
review_points = [random.randint(1, 5) for _ in range(100)]
reviews = [f"Review for {name}" for name in restaurant_names]

# Write the data to a CSV file
csv_path = "sample_data.csv"
with open(csv_path, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["Name", "Latitude", "Longitude", "Review Point", "Review"])  # Write header
    for i in range(100):
        csvwriter.writerow([restaurant_names[i], latitudes[i], longitudes[i], review_points[i], reviews[i]])
