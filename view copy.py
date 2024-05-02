import pandas as pd

# Read the Excel file into a DataFrame
df = pd.read_excel("abcd.xlsx")

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
<button class="button" style="background-color:yellow">Warning: {status_counts.get('Warning', 0)}</button>
<button class="button" style="background-color:pink">Down (Acknowledged): {status_counts.get('Down (Acknowledged)', 0)}</button>
<button class="button" style="background-color:grey">Unknown: {status_counts.get('Unknown', 0)}</button>
</body>
</html>
"""

# Write HTML to file
with open("status_summary.html", "w") as file:
    file.write(html_content)

print("HTML page generated successfully.")
