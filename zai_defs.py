import json
import os

# The name of the file where data will be saved
DATA_FILE = "inventory_data.json"

# Initialize the lists
stocks = []
aggr = []
ddc = []

def load():
    global stocks, aggr, ddc
    # Check if the file exists
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                stocks = data.get('stocks', [])
                aggr = data.get('aggr', [])
                ddc = data.get('ddc', [])
            print("Data loaded successfully!")
        except Exception as e:
            print(f"Error loading data: {e}")
    else:
        print("No data file found. Starting fresh.")
        # Optional: Add some default data for the first run
        stocks = [['T-Shirt', 'M', 'Cotton', '10', '15000']]

def save():
    data = {
        'stocks': stocks,
        'aggr': aggr,
        'ddc': ddc
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f)
        print("Data saved successfully!")
    except Exception as e:
        print(f"Error saving data: {e}")