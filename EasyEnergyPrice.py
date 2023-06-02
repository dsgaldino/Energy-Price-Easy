#!/usr/bin/env python
# coding: utf-8

# # Energy Price
# 
# TThe code aims to update the 'EasyEnergyPrice.csv' CSV file with the latest daily energy prices. It makes requests to an API to retrieve price data, processes the data, and adds it to the existing CSV file. The code checks if the dataset is up to date, retrieves the most recent and/or earliest data, performs data cleaning and formatting operations, and finally saves the updated DataFrame to the CSV file. This ensures that the file contains the latest daily energy prices, including any updates for previous dates.

# #### Import Libraries

# In[1]:


import requests
import pandas as pd
from datetime import timedelta, datetime
import time
import sys


# #### Define the URL

# In[2]:


# URL components for the API
start_url = 'https://mijn.easyenergy.com/nl/api/tariff/getapxtariffs?startTimestamp='
middle_url = 'T00%3A00%3A00.000Z&endTimestamp='
end_url = 'T23%3A00%3A00.000Z&grouping=%22'


# #### Functions

# In[ ]:


# Get the minimum and maximum dates from the DataFrame
def get_min_max_dates(df):
    min_date = pd.to_datetime(df['Date'].min(), format='%Y-%m-%d').date()
    max_date = pd.to_datetime(df['Date'].max(), format='%Y-%m-%d').date()
    return min_date, max_date


# In[ ]:


# Fetch data from the API based on the start and end dates
def get_data_from_api(start_date, end_date):
    url = f'{start_url}{start_date.replace("/", "-")}{middle_url}{end_date.replace("/", "-")}{end_url}'
    response = requests.get(url)
    data = response.json()
    return pd.DataFrame(data)


# In[ ]:


# Adjust the given date by subtracting one day
def adjust_dates(date):
    date = date - timedelta(days=1)
    date_str = date.strftime('%Y-%m-%d')
    return date, date_str


# In[ ]:


def check_missing_dates(df):
    min_date, max_date = get_min_max_dates(df)
    # Create a complete date range from the minimum to the maximum date
    complete_dates = pd.date_range(start=min_date, end=max_date)
    # Find the missing dates by comparing the complete range with the dates in the DataFrame
    missing_dates = set(complete_dates) - set(df['Date'])
    formatted_missing_dates = [date.strftime('%Y-%m-%d') for date in missing_dates]

    missing_dates_by_year = {}
    for missing_date in missing_dates:
        year = missing_date.year
        if year not in missing_dates_by_year:
            missing_dates_by_year[year] = []
        missing_dates_by_year[year].append(missing_date.strftime('%Y-%m-%d'))

    return formatted_missing_dates, missing_dates_by_year


# #### Read the CSV file

# In[3]:


# Read the original dataset
df = pd.read_csv('EasyEnergyPrice.csv')


# #### Check the dates

# In[ ]:


# Get the minimum and maximum dates from the DataFrame
min_date, max_date = get_min_max_dates(df)
# Get today's date
today = datetime.today().date()

# Print the date information
print('Earliest date found in the dataset:', min_date)
print('Latest date found in the dataset:', max_date)
print('Today\'s date:', today)
print('\n')

# Calculate the difference in days between the latest date and today
dif_days = (today - max_date).days


# #### Get and cleaning the data

# In[5]:


if dif_days != 0:
    # If the difference is not zero, fetch data from the API for the missing dates
    print('The difference between the latest date and today is:', dif_days, 'days')
    print('\n')
    # Adjust the dates by subtracting one day
    max_date, max_date_str = adjust_dates(max_date)
    today, today_str = adjust_dates(today)
    # Fetch data from the API
    df_comb = get_data_from_api(max_date_str, today_str)
elif min_date >= pd.to_datetime("2012-01-01").date():
    # If the difference is zero and the minimum date is after January 1, 2012,
    # fetch data from the API for the early dates
    min_date, min_date_str = adjust_dates(min_date)
    early_date_obj = datetime.strptime(str(min_date), '%Y-%m-%d')
    # Fetch data from the API
    df_comb = pd.concat([df_comb, get_data_from_api(early_date_str, min_date_str)], ignore_index=True)
else:
    # If none of the above conditions are met, the dataset is already updated
    print('The dataset is updated!')
    print('\n')
    df_comb = pd.DataFrame()

if not df_comb.empty:
    # Process the combined DataFrame if it is not empty
    df_comb[['Date', 'Hour']] = df_comb['Timestamp'].str.split('T', expand=True)
    df_comb['Hour'] = df_comb['Hour'].str.slice(stop=5)
    df_comb.drop(['Timestamp', 'SupplierId'], axis=1, inplace=True)
    # Rename the columns for clarity
    df_comb = df_comb.rename(columns={
        'TariffUsage': 'Import Grid (EUR/kWh)',
        'TariffReturn': 'Export Grid (EUR/kWh)'
    })

# Concatenate the original DataFrame and the combined DataFrame
df = pd.concat([df, df_comb], ignore_index=True)


# #### Handling Missing Dates in the Dataset

# In[ ]:


# Get the updated minimum and maximum dates from the merged DataFrame
min_date, max_date = get_min_max_dates(df)

# Check for missing dates in the DataFrame
missing_dates, missing_dates_by_year = check_missing_dates(df)

# Fill any remaining missing values with NaT (Not-a-Time)
df.fillna(value=pd.NaT, inplace=True)
# Remove duplicate rows from the DataFrame
df.drop_duplicates(inplace=True)


# #### Save the data

# In[ ]:


# Save the updated DataFrame to a CSV file
df.to_csv('EasyEnergyPrice.csv', index=False)


# In[ ]:


# Print the success message
print('DATA UPDATED SUCCESSFULLY!')

# Pause for 10 seconds
time.sleep(10)

# Close the program
sys.exit()

