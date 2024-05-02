import requests
import pandas as pd
from datetime import datetime
from collections import defaultdict
import webbrowser
import http.server
import socketserver


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



data_by_status = defaultdict(lambda: defaultdict(list))

for index, row in df.iterrows():
    status = row['Status']
    type_ = row['Type']
    date_time = row['Date Time']
    object_ = row['Object']
    data_by_status[status][type_].append((date_time, object_))

# Generate HTML content dynamically
html_content = """
<!DOCTYPE html>
<html>
<head>
<title>Status Summary</title>
<style>
.tree {
  list-style-type: none;
}

.tree ul {
  margin-left: 20px;
}

.tree ul ul {
  margin-left: 20px;
}

.tree li {
  cursor: pointer;
}
.hidden {
  display: none;
}
</style>
</head>
<body>
<h2>Status Summary</h2>
<ul class="tree">
"""

# Add status nodes
for status, types in data_by_status.items():
    html_content += f"<li onclick='toggleChildren(event)'>{status} ({len(types)})<ul class='hidden'>"
    for type_, objects in types.items():
        html_content += f"<li onclick='toggleChildren(event)'>{type_} ({len(objects)})<ul class='hidden'>"
        for date_time, object_ in objects:
            html_content += f"<li>{date_time}, {object_}</li>"
        html_content += "</ul></li>"
    html_content += "</ul></li>"

html_content += """
</ul>
<script>
function toggleChildren(event) {
  const target = event.target;
  const childUl = target.querySelector('ul');
  if (childUl) {
    childUl.classList.toggle('hidden');
    // Prevent toggling the parent UL when clicking on an inner LI
    event.stopPropagation();
  }
}
</script>
</body>
</html>
"""

# Write HTML to a temporary file
with open("status_summary.html", "w") as file:
    file.write(html_content)

print("HTML page generated successfully.")

# Open the HTML page in Chrome
webbrowser.open("status_summary.html")