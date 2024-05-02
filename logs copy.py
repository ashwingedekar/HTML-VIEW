import requests
import pandas as pd
from datetime import datetime
import webbrowser

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


# Count occurrences of each status
status_counts = df['Status'].value_counts()

# Generate HTML
html_content = f"""
<!DOCTYPE html>
<html>
<head>
<title>Status Summary</title>
<style>
.button {{
  border: none;
  color: white;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 12px;
  padding: 10px 20px;
}}
</style>
</head>
<body>
<h2>Status Summary</h2>
<button class="button" style="background-color:green">Up: {status_counts.get('Up', 0)}</button>
<button class="button" style="background-color:red">Down: {status_counts.get('Down', 0)}</button>
<button class="button" style="background-color:yellow;color:black">Warning: {status_counts.get('Warning', 0)}</button>
<button class="button" style="background-color:pink">Down (Acknowledged): {status_counts.get('Down (Acknowledged)', 0)}</button>
<button class="button" style="background-color:grey">Unknown: {status_counts.get('Unknown', 0)}</button>
</body>
</html>
"""

# Write HTML to file
with open("status_summary.html", "w") as file:
    file.write(html_content)

print("HTML page generated successfully.")

# Open the HTML page in Chrome
webbrowser.open("status_summary.html")