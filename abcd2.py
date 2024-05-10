import pandas as pd
from datetime import datetime, timedelta

# Load the CSV file into a DataFrame
df = pd.read_csv('tablee.csv')

# Assuming your date column is named 'Date Time', replace 'Date Time' with the correct column name
date_column = 'Date Time'

# Convert the 'Date Time' column to datetime format, specifying the date format
df[date_column] = pd.to_datetime(df[date_column], format='%d-%m-%Y %H:%M:%S')

# Get today's date
today = datetime.today().date()

# Calculate yesterday's date
yesterday = today - timedelta(days=1)

# Filter the DataFrame to retain only the data for today and yesterday
today_and_yesterday_data = df[(df[date_column].dt.date == today) | (df[date_column].dt.date == yesterday)]

# Now you can use today_and_yesterday_data for further analysis or save it to a new CSV file
today_and_yesterday_data.to_csv('today_and_yesterday_data.csv', index=False)
