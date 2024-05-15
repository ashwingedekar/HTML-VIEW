import xml.etree.ElementTree as ET
import csv

# XML file path
xml_file = "tab.xml"

# Parse XML
tree = ET.parse(xml_file)
root = tree.getroot()

# CSV file name
csv_file = "abcd.csv"

# Open CSV file in write mode
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write header row
    writer.writerow(['objid', 'datetime', 'datetime_raw', 'parent', 'type', 'type_raw', 'name', 'status', 'status_raw', 'message', 'message_raw'])

    # Loop through each <item> element
    for item in root.findall('.//item'):
        # Extract data from each item
        objid = item.find('objid').text
        datetime = item.find('datetime').text
        datetime_raw = item.find('datetime_raw').text
        parent = item.find('parent').text
        type = item.find('type').text
        type_raw = item.find('type_raw').text
        name = item.find('name').text
        status = item.find('status').text
        status_raw = item.find('status_raw').text
        message = item.find('message').text
        message_raw = item.find('message_raw').text

        # Write data to CSV file
        writer.writerow([objid, datetime, datetime_raw, parent, type, type_raw, name, status, status_raw, message, message_raw])

print("CSV file has been created successfully.")
