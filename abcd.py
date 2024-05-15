import xml.etree.ElementTree as ET
import csv

# Parse the XML file
tree = ET.parse('tab.xml')
root = tree.getroot()

# Open CSV file in write mode
with open('tab.csv', 'w', newline='') as csvfile:
    fieldnames = ['datetime', 'parent', 'type', 'name', 'status', 'message_raw']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    # Write CSV header
    writer.writeheader()

    # Loop through each 'item' element
    # Loop through each 'item' element
    for item in root.findall('.//item'):
      data = {}
    # Extract data from each child element
      data['datetime'] = item.find('datetime').text
      data['parent'] = item.find('parent').text
      data['type'] = item.find('type').text
      data['name'] = item.find('name').text
      data['status'] = item.find('status').text
    # Check if 'message_raw' element exists
     

    # Write data to CSV file
    writer.writerow(data)


print("CSV file generated successfully.")
