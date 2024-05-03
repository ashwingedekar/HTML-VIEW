import requests
import pandas as pd
from datetime import datetime
from collections import defaultdict
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
status_counts = df['Status'].value_counts()
# Initialize defaultdict to store data by status and type
data_by_status = defaultdict(lambda: defaultdict(list))

# Populate the defaultdict with data from the DataFrame
for _, row in df.iterrows():
    status = row['Status']
    type_ = row['Type']
    date_time = row['Date Time']
    object_ = row['Object']
    parent = row.get('Parent', '')  
    message = row.get('Message(RAW)', '')  
    data_by_status[status][type_].append((date_time, object_, parent, message))

# Generate HTML content dynamically
html_content = """
<!DOCTYPE html>
<html>
<head>
<title>Status Summary</title>
<style>
body
{
font-family: Calibri, sans-serif;
}
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

/* Define styles for different status backgrounds */
.status-up {
  color: green;
}
.status-down {
  color: red;
}
.status-warning {
  
}
.hidden {
  display: none;
}

</style>
</head>
<body>
<h2>PRTG-101.100-Logs</h2>

<ul class="tree">
"""

# Iterate through status and types
for status, types in data_by_status.items():
    status_class = ""
    if status == "Up":
        status_class = "status-up"
    elif status == "Down":
        status_class = "status-down"
    elif status == "Warning":
        status_class = "status-warning"

    # Add the status node with the appropriate class
    html_content += f"<li onclick='toggleChildren(event)' class='{status_class}'>{status} ({len(types)})<ul class='hidden'>"
    
    # Iterate through types
    for type_, objects in types.items():
        # Start the type node
        html_content += f"<li onclick='toggleChildren(event)'>{type_} ({len(objects)})<ul class='hidden'>"
        
        # Group objects by parent
        grouped_objects = defaultdict(list)
        for date_time, object_, parent, message in objects:
            grouped_objects[parent].append((date_time, object_, message))
        
        # Iterate through grouped objects
        for parent, grouped_items in grouped_objects.items():
            # Start the parent node
            html_content += f"<li onclick='showMessage(event)'>{parent}<ul class='hidden'>"
            
            # Add grouped items under the parent
            for date_time, object_, message in grouped_items:
                html_content += f"<li>Type: {object_}<ul class='hidden'><li>DateTime: {date_time}, Message: {message}</li></ul></li>"
            
            # Close the parent node
            html_content += "</ul></li>"
        
        # Close the type node
        html_content += "</ul></li>"
    
    # Close the status node
    html_content += "</ul></li>"

# Generate HTML content dynamically
html_content = """
<!DOCTYPE html>
<html>
<head>
<title>Status Summary</title>
<style>
body
{
font-family: Calibri, sans-serif;
}
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

/* Define styles for different status backgrounds */
.status-up {
  color: green;
}
.status-down {
  color: red;
}
.status-warning {
  
}
.hidden {
  display: none;
}

</style>
</head>
<body>
<h2>PRTG-101.100-Logs</h2>

<ul class="tree">
"""

# Iterate through status and types
for status, types in data_by_status.items():
    status_class = ""
    if status == "Up":
        status_class = "status-up"
    elif status == "Down":
        status_class = "status-down"
    elif status == "Warning":
        status_class = "status-warning"

    # Add the status node with the appropriate class
    html_content += f"<li onclick='toggleStatus(event)' class='{status_class}'>{status} ({len(types)})<ul class='hidden'>"
    
    # Iterate through types
    for type_, objects in types.items():
        # Start the type node
        html_content += f"<li onclick='toggleChildren(event)'>{type_} ({len(objects)})<ul class='hidden'>"
        
        # Group objects by parent
        grouped_objects = defaultdict(list)
        for date_time, object_, parent, message in objects:
            grouped_objects[parent].append((date_time, object_, message))
        
        # Iterate through grouped objects
        for parent, grouped_items in grouped_objects.items():
            # Start the parent node
            html_content += f"<li onclick='toggleChildren(event)'>{parent}<ul class='hidden'>"
            
            # Group objects by object_
            grouped_objects_by_type = defaultdict(list)
            for date_time, object_, message in grouped_items:
                grouped_objects_by_type[object_].append((date_time, message))
            
            # Iterate through grouped objects by object_
            for obj, grouped_items_by_type in grouped_objects_by_type.items():
                # Start the object_ node
                html_content += f"<li>{obj}<ul class='hidden'>"
                
                # Add grouped items under the object_
                for date_time, message in grouped_items_by_type:
                    html_content += f"<li>DateTime: {date_time}, Message: {message}</li>"
                
                # Close the object_ node
                html_content += "</ul></li>"
            
            # Close the parent node
            html_content += "</ul></li>"
        
        # Close the type node
        html_content += "</ul></li>"
    
    # Close the status node
    html_content += "</ul></li>"

html_content += """
</ul>
<script>
function toggleStatus(event) {
  const target = event.target;
  const childUl = target.querySelector('ul');
  if (childUl) {
    childUl.classList.toggle('hidden');
    // Prevent toggling the parent UL when clicking on an inner LI
    event.stopPropagation();
  }
}

function toggleChildren(event) {
  const target = event.target;
  const childUl = target.querySelector('ul');
  if (childUl) {
    childUl.classList.toggle('hidden');
    // Prevent toggling the parent UL when clicking on an inner LI
    event.stopPropagation();
  }
}

function showMessage(event) {
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

# Write the HTML content to a file
with open("status_summary.html", "w") as file:
    file.write(html_content)

print("HTML page generated successfully.")

# Open the HTML page in a web browser
webbrowser.open("status_summary.html")
