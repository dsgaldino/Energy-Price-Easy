#!/usr/bin/env python
# coding: utf-8

# # Energy Price
# 
# This application retrieves the price information provided by the Easy portal, 
# starting from the requested date up to today's date. The values are transformed from MWh to KWh.

# #### Import Libraries

# In[1]:


import requests
import pandas as pd
from datetime import timedelta, datetime


# #### Read the CSV file

# In[2]:


# Creating the DataFrame with the original information
df = pd.read_csv('EasyEnergyPrice.csv')


# #### Get the date of interest

# In[3]:


# The earliest date in the dataset
min_date = pd.to_datetime(df['Date'].min(), format='%Y-%m-%d').date()

# The latest date in the dataset
max_date = pd.to_datetime(df['Date'].max(), format='%Y-%m-%d').date()

# Today's date
today = datetime.today().date()

print('Earliest date found in the dataset:', min_date)
print('Latest date found in the dataset:', max_date)
print('Today\'s date:', today)


# In[4]:


# Days difference
dif_days = (today - max_date).days

# Check if the dataset is updated
if dif_days != 0:
    print('The difference between the latest date and today is:', dif_days, 'days')
else:
    print('The dataset is updated!')


# #### Dinamic URL

# In[5]:


start_url = 'https://mijn.easyenergy.com/nl/api/tariff/getapxtariffs?startTimestamp='
middle_url = 'T00%3A00%3A00.000Z&endTimestamp='
end_url = 'T23%3A00%3A00.000Z&grouping=%22'


# #### Get the data from the website

# In[6]:


# Create a temporary DataFrame to store the daily prices
df_comb = pd.DataFrame()  # Temporary DataFrame to combine the prices with the original

# Updating the dataset with the latest dates
if dif_days != 0:
    # Adjusting dates
    max_date = max_date + timedelta(days=1)
    today = today - timedelta(days=1)

    # Convert dates to strings
    max_date_str = max_date.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')

    # Creating the URL
    url = f'{start_url}{max_date_str.replace("/", "-")}{middle_url}{today_str.replace("/", "-")}{end_url}'

    # Copy the information from the URL into a temporary DataFrame
    response = requests.get(url)
    data = response.json()
    df_tempL = pd.DataFrame(data)

    # Append the information from the temporary DataFrame to the combined DataFrame
    df_comb = pd.concat([df_comb, df_tempL], ignore_index=True)



# In[20]:


# Updating the dataset with the earliest dates
if min_date >= pd.to_datetime("2012-01-01").date():
    # Adjusting dates
    min_date = min_date - timedelta(days=1)
    early_date_obj = datetime.strptime(str(min_date), '%Y-%m-%d')

    # Convert dates to strings
    min_date_str = min_date.strftime('%Y-%m-%d')
    early_date_str = early_date_obj.strftime('%Y-%m-%d')

    # Creating the URL
    url = f'{start_url}{early_date_str.replace("/", "-")}{middle_url}{min_date_str.replace("/", "-")}{end_url}'

    # Copy the information from the URL into a temporary DataFrame
    response = requests.get(url)
    data = response.json()
    df_tempE = pd.DataFrame(data)

    # Append the information from the temporary DataFrame to the combined DataFrame
    df_comb = pd.concat([df_comb, df_tempE], ignore_index=True)


# #### Cleaning the data

# In[23]:


if not df_comb.empty:
    # Split the Timestamp column into Date and Hour columns
    df_comb[['Date', 'Hour']] = df_comb['Timestamp'].str.split('T', expand=True)
    df_comb['Hour'] = df_comb['Hour'].str.slice(stop=5)

    # Drop the Timestamp and SupplierId columns
    df_comb.drop(['Timestamp', 'SupplierId'], axis=1, inplace=True)

    # Rename the TariffUsage and TariffReturn columns
    df_comb = df_comb.rename(columns={
        'TariffUsage': 'Import Grid (EUR/kWh)',
        'TariffReturn': 'Export Grid (EUR/kWh)'
    })


# #### Save the data

# In[24]:


# Append the information from the temporary DataFrame to the original DataFrame
df = pd.concat([df, df_comb], ignore_index=True)

df.to_csv('EasyEnergyPrice.csv', index=False)

