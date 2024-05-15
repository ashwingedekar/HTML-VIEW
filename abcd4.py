import xml.etree.ElementTree as ET
import csv

# Path to the XML file
xml_file_path = "your_xml_file.xml"

# Parse the XML file
tree = ET.parse(xml_file_path)
root = tree.getroot()

# Open CSV file in write mode
csv_file_path = "output.csv"
with open(csv_file_path, 'w', newline='') as csvfile:
    fieldnames = ['objid', 'datetime', 'parent', 'type', 'name', 'status', 'message_raw']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write CSV header
    writer.writeheader()

    # Loop through each 'item' element
    for item in root.findall('.//item'):
        data = {}
        # Extract data from each child element
        data['objid'] = item.find('objid').text if item.find('objid') is not None else ""
        data['datetime'] = item.find('datetime').text if item.find('datetime') is not None else ""
        data['parent'] = item.find('parent').text if item.find('parent') is not None else ""
        data['type'] = item.find('type').text if item.find('type') is not None else ""
        data['name'] = item.find('name').text if item.find('name') is not None else ""
        data['status'] = item.find('status').text if item.find('status') is not None else ""
        data['message_raw'] = item.find('message_raw').text if item.find('message_raw') is not None else ""

        # Write data to CSV file
        writer.writerow(data)

print("CSV file generated successfully.")
