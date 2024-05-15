import json
import csv

def json_to_csv(json_file, csv_file):
    # Open JSON file
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    # Open CSV file in write mode
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Write header
        headers = data['messages'][0].keys()  # Assuming all messages have the same structure
        writer.writerow(headers)
        
        # Write data
        for message in data['messages']:
            writer.writerow(message.values())

# Example usage
json_file = 'baba.json'  # Replace 'data.json' with your JSON file path
csv_file = 'baba.csv'    # Replace 'data.csv' with your desired CSV file path

json_to_csv(json_file, csv_file)
