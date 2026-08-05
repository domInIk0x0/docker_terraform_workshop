#!/usr/bin/env python
# coding: utf-8

# In[11]:


import pandas as pd

prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz', nrows=100)
#df = pd.read_csv(prefix + 'yellow_tripdata_2021-01.csv.gz')


# In[13]:


df.head(5)


# In[14]:


df.dtypes


# In[15]:


df.shape


# In[16]:


dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]

df = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    nrows=100,
    dtype=dtype,
    parse_dates=parse_dates
)


# In[17]:


df.head()


# In[18]:


from sqlalchemy import create_engine
engine = create_engine('postgresql+psycopg://root:root@localhost:5433/ny_taxi')
print(pd.io.sql.get_schema(df, name='yellow_taxi_data', con=engine))


# In[19]:


df.head(n=0).to_sql(name='yellow_taxi_data', con=engine, if_exists='replace')


# In[ ]:


df_iter = pd.read_csv(
    prefix + 'yellow_tripdata_2021-01.csv.gz',
    dtype=dtype,
    parse_dates=parse_dates,
    iterator=True,
    chunksize=100000
)


# In[21]:


for df_chunk in df_iter:
    print(len(df_chunk))


# In[22]:


df_chunk.to_sql(name='yellow_taxi_data', con=engine, if_exists='append')


# In[ ]:


from tqdm.auto import tqdm
first = True

for df_chunk in tqdm(df_iter):

    if first:
        # Create table schema (no data)
        df_chunk.head(0).to_sql(
            name="yellow_taxi_data",
            con=engine,
            if_exists="replace"
        )
        first = False
        print("Table created")

    # Insert chunk
    df_chunk.to_sql(
        name="yellow_taxi_data",
        con=engine,
        if_exists="append"
    )

    print("Inserted:", len(df_chunk))

