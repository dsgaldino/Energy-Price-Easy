#!/usr/bin/env python
# coding: utf-8

# In[9]:


import requests
import pandas as pd
import csv
from datetime import timedelta, datetime


# In[10]:


# Creating the DataFrame with the original information
df = pd.read_csv('EasyEnergyPrice.csv')


# In[11]:


# The earliest date in the dataset
min_date = pd.to_datetime(df['Date'].min(), format='%Y-%m-%d').date()

# The latest date in dataset
max_date = pd.to_datetime(df['Date'].max(), format='%Y-%m-%d').date()

# Today date
today = datetime.today().date()

print('Earliest date found in the dataset:', min_date)
print('Latest date found in the dataset:', max_date)
print('Today\'s date:', today)


# In[12]:


# Days difference
dif_days = (today - max_date).days

# Check if the dataset is updated
if dif_days != 0:
    print('The difference between the latest date and today is:', dif_days, 'days')
else:
    print('The dataset is updated!')


# In[13]:


start_url = 'https://mijn.easyenergy.com/nl/api/tariff/getapxtariffs?startTimestamp='
middle_url = 'T00%3A00%3A00.000Z&endTimestamp='
end_url = 'T23%3A00%3A00.000Z&grouping=%22'


# In[14]:


# Create a temporary DataFrame to store the daily price 
df_comb = pd.DataFrame() # Temporary DataFrame combine the prices with the original
df_tempE = pd.DataFrame() # Temporary DataFrame for prices (earlist dates)
df_tempL = pd.DataFrame() # Temporary DataFrame for prices (lastest dates)

# Updating the dataset with lastest dates
if dif_days != 0:
    # Adjusting dates    
    max_date = max_date + timedelta(days=1)
    today = today - timedelta(days=1)
    
    # Convert date to string 
    max_date_str = max_date.strftime('%Y-%m-%d')
    today_str = today.strftime('%Y-%m-%d')
    
    #Creating the URL
    url = f'{start_url}{max_date_str.replace("/", "-")}{middle_url}{today_str.replace("/", "-")}{end_url}'
   
    # Copy the information from the URL into a temporary DataFrame
    response = requests.get(url)
    data = response.json()
    df_tempL = pd.DataFrame(data)
    
    # Append the information from the temporary DataFrame to the combined DataFrame
    df_comb = pd.concat([df_comb, df_tempL], ignore_index=True)
    
# Updating the dataset with earlist dates

# Adjusting dates
min_date = min_date - timedelta(days=1)
early_year = str(min_date.year)
early_date = early_year + '-01-01'
early_date_obj = datetime.strptime(early_date, '%Y-%m-%d')
    
# Convert date to string 
min_date_str = min_date.strftime('%Y-%m-%d')
early_date_str = early_date_obj.strftime('%Y-%m-%d')

#Creating the URL
url = f'{start_url}{early_date_str.replace("/", "-")}{middle_url}{min_date_str.replace("/", "-")}{end_url}'

# Copy the information from the URL into a temporary DataFrame
response = requests.get(url)
data = response.json()
df_tempE = pd.DataFrame(data)

# Append the information from the temporary DataFrame to the combined DataFrame
df_comb = pd.concat([df_comb, df_tempE], ignore_index=True)


# In[15]:


# split Timestamp column into Date and Hour columns
df_comb[['Date', 'Hour']] = df_comb['Timestamp'].str.split('T', expand=True)
df_comb['Hour'] = df_comb['Hour'].str.slice(stop=5)

# drop Timestamp column
df_comb.drop('Timestamp', axis=1, inplace=True)
df_comb.drop('SupplierId', axis=1, inplace=True)

# rename TariffUsage and TariffReturn columns
df_comb = df_comb.rename(columns={
    'TariffUsage': 'Import Grid (EUR/kWh)',
    'TariffReturn': 'Export Grid (EUR/kWh)'
})

# Append the information from the temporary DataFrame to the original
df = pd.concat([df, df_comb], ignore_index=True)


# In[16]:


df.to_csv('EasyEnergyPrice.csv', index=False)

