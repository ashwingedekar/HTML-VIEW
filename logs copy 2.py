import requests
import pandas as pd
from datetime import datetime
import webbrowser
import plotly.graph_objects as go

with open("server_address.txt", "r") as file:
    server_parameters = dict(line.strip().split("=") for line in file)

server_address = server_parameters.get("server")
username = server_parameters.get("username")
passhash = server_parameters.get("passhash")
param = server_parameters.get("day")

api_endpoint = f'https://{server_address}/api/table.csv?content=messages&columns=objid,datetime,parent,type,name,status,message&filter_drel={param}&count=*&username={username}&passhash={passhash}'
current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")
file_path = f"prtg-{current_datetime}-101.100.csv"

response = requests.get(api_endpoint, stream=True)
response.raise_for_status()

with open(file_path, "wb") as file:
    for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)

print(f"CSV data saved to {file_path}")

# Now read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Drop unnecessary columns
columns_to_drop = ['ID(RAW)', 'Date Time(RAW)', 'Parent(RAW)', 'Type(RAW)', 'Object(RAW)', 'Status(RAW)', 'Message']
df.drop(columns=columns_to_drop, inplace=True)

# Save the updated DataFrame back to the CSV file
df.to_csv(file_path, index=False)

print("CSV data processed successfully.")

df = pd.read_csv(file_path)

# Filter dataframe for 'Up' status
up_df = df[df['Status'] == 'Up']

# Group by 'Type' column and count occurrences
up_type_counts = up_df['Type'].value_counts()

# Create tree structure
up_tree = go.Figure(go.Treemap(
    labels=up_type_counts.index,
    parents=[''] * len(up_type_counts.index),  # Parent of root nodes
    values=up_type_counts.values
))

up_tree.update_layout(title='Up Status - Type Tree Structure')

# Save HTML file for the tree structure
up_tree_path = "up_tree_structure.html"
up_tree.write_html(up_tree_path)

print("Up status tree structure generated successfully.")

# Open the HTML page in the default web browser
webbrowser.open(up_tree_path)
