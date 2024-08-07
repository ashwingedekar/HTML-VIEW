import requests
import pandas as pd
from datetime import datetime
from collections import defaultdict
import webbrowser
import json
import csv

prtg_choice = input("Enter the PRTG you want (99.100, 101.100, or 99.102): ")

if prtg_choice == "99.100":
    with open("server_address-99.100.txt", "r") as file:
       server_parameters = dict(line.strip().split("=") for line in file)

    server_address = server_parameters.get("server")
    username = server_parameters.get("username")
    passhash = server_parameters.get("passhash")
    param = server_parameters.get("day")
elif prtg_choice == "101.100":
    with open("server_address-101.100.txt", "r") as file:
        server_parameters = dict(line.strip().split("=") for line in file)
    server_address = server_parameters.get("server")
    username = server_parameters.get("username")
    passhash = server_parameters.get("passhash")
    param = server_parameters.get("day")
elif prtg_choice == "99.102":
    with open("server_address-99.102.txt", "r") as file:
        server_parameters = dict(line.strip().split("=") for line in file)
    server_address = server_parameters.get("server")
    username = server_parameters.get("username")
    passhash = server_parameters.get("passhash")
    param = server_parameters.get("day")
else:
    print("Invalid input! Please enter either '99.100', '101.100', or '99.102'.")
    exit()

current_datetime = datetime.now().strftime("%d %B %Y %I:%M %p")

if server_address and "99-102" in server_address:
    h2_content = f"Prtg-99-102-Logs-{current_datetime}"
elif server_address and "101-100" in server_address:
     h2_content = f"Prtg-101-100 Logs-{current_datetime}"
elif server_address and "99-100" in server_address:
    h2_content = f"Prtg-99-100 Logs-{current_datetime}"
else:
    h2_content ="PRTG LOGS"

api_endpoint = f'https://{server_address}/api/table.json?content=messages&columns=objid,datetime,parent,type,name,status,message&filter_drel={param}&count=*&username={username}&passhash={passhash}'
current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")

if "101-100" in server_address:
    file_path = f"prtg-{current_datetime}-101.100.json"
    csv_path  = f"prtg-{current_datetime}-101.100.csv"
elif "99-100" in server_address:
    file_path = f"prtg-{current_datetime}-99.100.json"
    csv_path  = f"prtg-{current_datetime}-99.100.csv"
elif "99-102" in server_address:
    file_path = f"prtg-{current_datetime}-99.102.json"
    csv_path  = f"prtg-{current_datetime}-99.102.csv"
else:
    file_path = f"prtg-{current_datetime}-default.json"
    csv_path  = f"prtg-{current_datetime}-default.csv"
response = requests.get(api_endpoint, stream=True)
response.raise_for_status()

with open(file_path, "wb") as file:
    for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)

print(f"Json data saved to {file_path}")

json_file = f'{file_path}'
csv_file = f'{csv_path}'
def json_to_csv(json_file, csv_file):
   
    with open(json_file, 'r') as f:
        data = json.load(f)
      
    with open(csv_file, 'w', newline='') as f:
        writer = csv.writer(f)
        
        headers = data['messages'][0].keys()  
        writer.writerow(headers)
        
        
        for message in data['messages']:
            writer.writerow(message.values())

json_to_csv(json_file, csv_file)

df = pd.read_csv(f"{csv_path}")

df.rename(columns={
    'objid': 'ID',
    'objid_raw': 'ID(RAW)',
    'datetime': 'Date Time',
    'datetime_raw': 'Date Time(RAW)',
    'parent': 'Parent',
    'parent_raw': 'Parent(RAW)',
    'type': 'Type',
    'type_raw': 'Type(RAW)',
    'name': 'Object',
    'name_raw': 'Object(RAW)',
    'status': 'Status',
    'status_raw': 'Status(RAW)',
    'message': 'Message',
    'message_raw': 'Message(RAW)'
}, inplace=True)

df.to_csv(f"{csv_path}", index=False)

print(f"CSV data saved to {csv_path}")

df = pd.read_csv(csv_path)
columns_to_drop = ['ID(RAW)', 'Date Time(RAW)', 'Parent(RAW)', 'Type(RAW)', 'Object(RAW)', 'Status(RAW)']
df.drop(columns=columns_to_drop, inplace=True)
df.to_csv(csv_path, index=False)
print("CSV data processed successfully.")

df['Message(RAW)'].fillna('', inplace=True)  # Fill NaN values in the 'Message' column with an empty string

status_counts = df['Status'].value_counts()
data_by_status = defaultdict(lambda: defaultdict(list))
data_by_no_data = defaultdict(lambda: defaultdict(list))
data_by_timeout = defaultdict(lambda: defaultdict(list))

for _, row in df.iterrows():
    status = row['Status']
    type_ = row['Type']
    date_time = row['Date Time']
    object_ = row['Object']
    parent = row.get('Parent', '')  
    message = row.get('Message(RAW)', '') 
    sensid = row.get('ID') 
    if "returned no data" in message:
        data_by_no_data['No Data'][type_].append((date_time, object_, parent, message, sensid))
    elif "Timeout" in message:
        data_by_timeout['Timeout'][type_].append((date_time, object_, parent, message, sensid))
    else:
        data_by_status[status][type_].append((date_time, object_, parent, message, sensid))

html_content = """
<!DOCTYPE html>
<html>
<head>
<title>Status Summary</title>
<style>
body {
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
.tree li:hover {
    cursor: pointer;
}
.tree li {}
.status-up {
    color: green;
}
.status-down {
    color: red;
}
.status-warning {}
.status-no-data {
    color: purple;
}
.status-timeout {
    color: purple;
}
.hidden {
    display: none;
}
</style>
</head>
<body>
<h2>%s</h2>
<ul class="tree">
""" % h2_content

# Calculate total types for each status
total_types_by_status = {status: sum(len(objects) for objects in types.values()) for status, types in data_by_status.items()}
total_types_by_no_data = {status: sum(len(objects) for objects in types.values()) for status, types in data_by_no_data.items()}
total_types_by_timeout = {status: sum(len(objects) for objects in types.values()) for status, types in data_by_timeout.items()}

# Display "No Data" section
no_data_count = total_types_by_no_data.get('No Data', 0)
html_content += f"<li onclick='toggleStatus(event)' class='status-no-data'>No Data <strong> ({no_data_count})</strong><ul class='hidden'>"
for type_, objects in data_by_no_data['No Data'].items():
    html_content += f"<li onclick='toggleChildren(event)'><b>Sensor Type:</b> {type_} <strong>({len(objects)})</strong><ul class='hidden'>"
    grouped_objects = defaultdict(list)
    for date_time, object_, parent, message, sensid in objects:
        grouped_objects[parent].append((date_time, object_, message, sensid))
    for parent, grouped_items in grouped_objects.items():
        html_content += f"<li onclick='toggleChildren(event)'><b>Device :</b> {parent} <strong>({len(grouped_items)})</strong><ul class='hidden'>"
        grouped_objects_by_type = defaultdict(list)
        for date_time, object_, message, sensid in grouped_items:
            grouped_objects_by_type[object_].append((date_time, message, sensid))
        for obj, grouped_items_by_type in grouped_objects_by_type.items():
            if grouped_items_by_type:
                first_item = grouped_items_by_type[0]
                sensid = first_item[2] if len(first_item) >= 3 else ''
            else:
                sensid = ''
            if "Group" in type_:
                sensor_url = f"https://{server_address}/group.htm?id={sensid}"
            elif "Device" in type_:
                sensor_url = f"https://{server_address}/device.htm?id={sensid}"
            elif "Probe" in type_:
                sensor_url = f"https://{server_address}/probenode.htm?id={sensid}"
            elif "Notification Template" in type_:
                sensor_url = f"https://{server_address}/editnotification.htm?id={sensid}"
            else:
                sensor_url = f"https://{server_address}/sensor.htm?id={sensid}"
            html_content += f"<li><strong>ID:<a href='{sensor_url}'> {sensid} </a>Sensor:</strong> {obj} <strong>({len(grouped_items_by_type)})</strong><ul class='hidden'>"
            for date_time, message, sensid in grouped_items_by_type:
                 highlight_style_warning = "style='background-color: yellow;'" if "error" in message else ""
                 highlight_style_error = "style='background-color: black; color: white;'" if "warning" in message else ""
                 parts = message.split(" ")
                 highlighted_message = ""
                 for part in parts:
                     if "Warning" in part:
                         highlighted_message += f"<span {highlight_style_warning}>{part}</span> "
                     elif "Error" in part:
                          highlighted_message += f"<span {highlight_style_error}>{part}</span> "
                     else:   
                          highlighted_message += part + " " 

            html_content += f"<li><b>DateTime:</b> {date_time}, <b>Message:</b> {highlighted_message.strip()}</li>"
            html_content += "</ul></li>"
        html_content += "</ul></li>"
    html_content += "</ul></li>"
html_content += "</ul></li>"

# Display "Timeout" section
timeout_count = total_types_by_timeout.get('Timeout', 0)
html_content += f"<li onclick='toggleStatus(event)' class='status-timeout'>Timeout <strong> ({timeout_count})</strong><ul class='hidden'>"
for type_, objects in data_by_timeout['Timeout'].items():
    html_content += f"<li onclick='toggleChildren(event)'><b>Sensor Type:</b> {type_} <strong>({len(objects)})</strong><ul class='hidden'>"
    grouped_objects = defaultdict(list)
    for date_time, object_, parent, message, sensid in objects:
        grouped_objects[parent].append((date_time, object_, message, sensid))
    for parent, grouped_items in grouped_objects.items():
        html_content += f"<li onclick='toggleChildren(event)'><b>Device :</b> {parent} <strong>({len(grouped_items)})</strong><ul class='hidden'>"
        grouped_objects_by_type = defaultdict(list)
        for date_time, object_, message, sensid in grouped_items:
            grouped_objects_by_type[object_].append((date_time, message, sensid))
        for obj, grouped_items_by_type in grouped_objects_by_type.items():
            if grouped_items_by_type:
                first_item = grouped_items_by_type[0]
                sensid = first_item[2] if len(first_item) >= 3 else ''
            else:
                sensid = ''
            if "Group" in type_:
                sensor_url = f"https://{server_address}/group.htm?id={sensid}"
            elif "Device" in type_:
                sensor_url = f"https://{server_address}/device.htm?id={sensid}"
            elif "Probe" in type_:
                sensor_url = f"https://{server_address}/probenode.htm?id={sensid}"
            elif "Notification Template" in type_:
                sensor_url = f"https://{server_address}/editnotification.htm?id={sensid}"
            else:
                sensor_url = f"https://{server_address}/sensor.htm?id={sensid}"
            html_content += f"<li><strong>ID:<a href='{sensor_url}'> {sensid} </a>Sensor:</strong> {obj} <strong>({len(grouped_items_by_type)})</strong><ul class='hidden'>"
            for date_time, message, sensid in grouped_items_by_type:
                highlight_style = "style='background-color: yellow;'" if "Warning" in message or "Error" in message else ""
                html_content += f"<li><b>DateTime:</b> {date_time}, <b>Message:</b> <span {highlight_style}>{message}</span></li>"
            html_content += "</ul></li>"
        html_content += "</ul></li>"
    html_content += "</ul></li>"
html_content += "</ul></li>"

# Display all other statuses
for status, types in data_by_status.items():
    if status in ['No Data', 'Timeout']:
        continue
    status_class = ""
    if "Up" in status:
        status_class = "status-up"
    elif "Down" in status:
        status_class = "status-down"
    elif "Warning" in status:
        status_class = "status-warning"
    html_content += f"<li onclick='toggleStatus(event)' class='{status_class}'>{status} <strong> ({total_types_by_status[status]})</strong><ul class='hidden'>"
    for type_, objects in types.items():
        html_content += f"<li onclick='toggleChildren(event)'><b>Sensor Type:</b> {type_} <strong>({len(objects)})</strong><ul class='hidden'>"
        grouped_objects = defaultdict(list)
        for date_time, object_, parent, message, sensid in objects:
            grouped_objects[parent].append((date_time, object_, message, sensid))
        for parent, grouped_items in grouped_objects.items():
            html_content += f"<li onclick='toggleChildren(event)'><b>Device :</b> {parent} <strong>({len(grouped_items)})</strong><ul class='hidden'>"
            grouped_objects_by_type = defaultdict(list)
            for date_time, object_, message, sensid in grouped_items:
                grouped_objects_by_type[object_].append((date_time, message, sensid))
            for obj, grouped_items_by_type in grouped_objects_by_type.items():
                if grouped_items_by_type:
                    first_item = grouped_items_by_type[0]
                    sensid = first_item[2] if len(first_item) >= 3 else ''
                else:
                    sensid = ''
                if "Group" in type_:
                    sensor_url = f"https://{server_address}/group.htm?id={sensid}"
                elif "Device" in type_:
                    sensor_url = f"https://{server_address}/device.htm?id={sensid}"
                elif "Probe" in type_:
                    sensor_url = f"https://{server_address}/probenode.htm?id={sensid}"
                elif "Notification Template" in type_:
                    sensor_url = f"https://{server_address}/editnotification.htm?id={sensid}"
                else:
                    sensor_url = f"https://{server_address}/sensor.htm?id={sensid}"
                html_content += f"<li><strong>ID:<a href='{sensor_url}'> {sensid} </a>Sensor:</strong> {obj} <strong>({len(grouped_items_by_type)})</strong><ul class='hidden'>"
                for date_time, message, sensid in grouped_items_by_type:
                    highlight_style_warning = "style='background-color: yellow;'" 
                    highlight_style_error = "style='background-color: black; color: white;'"
                    parts = message.split(" ")
                    highlighted_message = ""
                    for part in parts:
                      if "error" in part:
                         highlighted_message += f"<span {highlight_style_warning}>{part}</span> "
                      elif "warning" in part:
                          highlighted_message += f"<span {highlight_style_error}>{part}</span> "
                      else:
                         highlighted_message += part + " "
                    highlighted_message = highlighted_message.strip()
                    html_content += f"<li><b>DateTime:</b> {date_time}, <b>Message:</b> {highlighted_message}</li>"     
                html_content += "</ul></li>"
            html_content += "</ul></li>"
        html_content += "</ul></li>"
    html_content += "</ul></li>"

html_content += """
</ul>
<script>
function toggleChildren(event) {
    event.stopPropagation();
    const children = event.target.querySelectorAll(':scope > ul');
    children.forEach(child => {
        child.classList.toggle('hidden');
    });
}

function toggleStatus(event) {
    event.stopPropagation();
    const children = event.target.querySelectorAll(':scope > ul');
    children.forEach(child => {
        child.classList.toggle('hidden');
    });
}
</script>
</body>
</html>
"""


if "101-100" in server_address:
 with open(f"prtg-{current_datetime}-101.100.html", "w") as file:
    file.write(html_content)
    webbrowser.open(f"prtg-{current_datetime}-101.100.html")
if "99-100" in server_address:
 with open(f"prtg-{current_datetime}-99.100.html", "w") as file:
    file.write(html_content)
    webbrowser.open(f"prtg-{current_datetime}-99.100.html")
if "99-102" in server_address:
 with open(f"prtg-{current_datetime}-99.102.html", "w") as file:
    file.write(html_content)
    webbrowser.open(f"prtg-{current_datetime}-99.102.html")

print("HTML page generated successfully.")
