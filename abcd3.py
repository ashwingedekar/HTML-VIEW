import xml.etree.ElementTree as ET
import csv

# XML file path
xml_file = "tab.xml"

# Parse XML
tree = ET.parse(xml_file)
root = tree.getroot()

# CSV file name
csv_file = "output.csv"

# Open CSV file in write mode
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write header row
    writer.writerow(['objid', 'datetime', 'datetime_raw', 'parent', 'type', 'type_raw', 'name', 'status', 'status_raw', 'message', 'message_raw'])

    # Loop through each <item> element
    for item in root.findall('.//item'):
        # Extract data from each item
        objid = item.find('objid').text if item.find('objid') is not None else ""
        datetime = item.find('datetime').text if item.find('datetime') is not None else ""
        datetime_raw = item.find('datetime_raw').text if item.find('datetime_raw') is not None else ""
        parent = item.find('parent').text if item.find('parent') is not None else ""
        type = item.find('type').text if item.find('type') is not None else ""
        type_raw = item.find('type_raw').text if item.find('type_raw') is not None else ""
        name = item.find('name').text if item.find('name') is not None else ""
        status = item.find('status').text if item.find('status') is not None else ""
        status_raw = item.find('status_raw').text if item.find('status_raw') is not None else ""
        message = item.find('message').text if item.find('message') is not None else ""
        message_raw = item.find('message_raw').text if item.find('message_raw') is not None else ""

        # Write data to CSV file
        writer.writerow([objid, datetime, datetime_raw, parent, type, type_raw, name, status, status_raw, message, message_raw])

print("CSV file has been created successfully.")
