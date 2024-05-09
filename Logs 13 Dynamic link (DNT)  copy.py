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

if server_address and "prtg-99-102" in server_address:
    h2_content = "Prtg-99-102 Logs"
elif server_address and "prtg-101-100" in server_address:
     h2_content = "Prtg-101-100 Logs"
elif server_address and "prtg-99-100" in server_address:
    h2_content = "Prtg-99-100 Logs"
else:
   h2_content ="PRTG LOGS"


api_endpoint = f'https://{server_address}/api/table.csv?content=messages&columns=objid,datetime,parent,type,name,status,message&filter_drel={param}&count=*&username={username}&passhash={passhash}'
current_datetime = datetime.now().strftime("%Y%m%d-%H%M%S")

if "101-100" in server_address:
    file_path = f"prtg-{current_datetime}-101.100.csv"
elif "99-100" in server_address:
    file_path = f"prtg-{current_datetime}-99.100.csv"
elif "99-102" in server_address:
    file_path = f"prtg-{current_datetime}-99.102.csv"
else:
    # Default file path if server_address does not match any of the specified substrings
    file_path = f"prtg-{current_datetime}-default.csv"

response = requests.get(api_endpoint, stream=True)
response.raise_for_status()

with open(file_path, "wb") as file:
    for chunk in response.iter_content(chunk_size=8192):
        file.write(chunk)

print(f"CSV data saved to {file_path}")

df = pd.read_csv(file_path)

columns_to_drop = ['ID(RAW)', 'Date Time(RAW)', 'Parent(RAW)', 'Type(RAW)', 'Object(RAW)', 'Status(RAW)', 'Message']
df.drop(columns=columns_to_drop, inplace=True)

df.to_csv(file_path, index=False)

print("CSV data processed successfully.")
status_counts = df['Status'].value_counts()
data_by_status = defaultdict(lambda: defaultdict(list))

for _, row in df.iterrows():
    status = row['Status']
    type_ = row['Type']
    date_time = row['Date Time']
    object_ = row['Object']
    parent = row.get('Parent', '')  
    message = row.get('Message(RAW)', '') 
    sensid  = row.get('ID') 
    data_by_status[status][type_].append((date_time, object_, parent, message,sensid))

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

.tree li:hover {
  cursor: pointer; 
}


.tree li {
 
 
  
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
<h2>%s</h2>

<ul class="tree">
""" % h2_content

# Calculate total types for each status
total_types_by_status = {status: sum(len(objects) for objects in types.values()) for status, types in data_by_status.items()}

for status, types in data_by_status.items():
    status_class = ""
    if status == "Up":
        status_class = "status-up"
    elif status == "Down":
        status_class = "status-down"
    elif status == "Warning":
        status_class = "status-warning"

    html_content += f"<li onclick='toggleStatus(event)' class='{status_class}'>{status} <strong> ({total_types_by_status[status]})</strong><ul class='hidden'>"
    
    for type_, objects in types.items():
        html_content += f"<li onclick='toggleChildren(event)'>Sensor Type: {type_} <strong>({len(objects)})</strong><ul class='hidden'>"
        
        grouped_objects = defaultdict(list)
        for date_time, object_, parent, message, sensid in objects:
            grouped_objects[parent].append((date_time, object_, message, sensid))
        
        for parent, grouped_items in grouped_objects.items():
            html_content += f"<li onclick='toggleChildren(event)'>Device : {parent} <strong>({len(grouped_items)})</strong><ul class='hidden'>"
            
            grouped_objects_by_type = defaultdict(list)
            for date_time, object_, message, sensid in grouped_items:
                grouped_objects_by_type[object_].append((date_time, message, sensid))
            
            for obj, grouped_items_by_type in grouped_objects_by_type.items():
                #print("Object:", type_) 
                if "Group" in type_:
                    sensor_url = f"https://{server_address}/group.htm?id={sensid}"
                elif "Device" in type_:
                    sensor_url = f"https://{server_address}/device.htm?id={sensid}"
                else:
                    sensor_url = f"https://{server_address}/sensor.htm?id={sensid}"
                
                html_content += f"<li><strong>ID:<a href='{sensor_url}'> {sensid} </a>Sensor:</strong> {obj} <strong>({len(grouped_items_by_type)})</strong><ul class='hidden'>"
                
                for date_time, message, sensid in grouped_items_by_type:
                    html_content += f"<li>DateTime: {date_time}, Message: {message}</li>"
                
                html_content += "</ul></li>"
            
            html_content += "</ul></li>"
        
        html_content += "</ul></li>"
    
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

let h2 = document.querySelector("h2");

if (server_address.includes("prtg-99-102") ) {
  h2.innerHTML = "Prtg-99-102 Logs !!!";
} else {
  h2.innerHTML = "New heading text if condition is false";
}


</script>
</body>
</html>
"""


with open("status_summary.html", "w") as file:
    file.write(html_content)

print("HTML page generated successfully.")

# Open the HTML page in a web browser
webbrowser.open("status_summary.html")