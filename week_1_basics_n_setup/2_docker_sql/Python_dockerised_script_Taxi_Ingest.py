#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from sqlalchemy import create_engine
from time import time
import argparse
import os

def main(params):
    user=params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db 
    table = params.table
    url = params.url

    csv_name = 'taxi_data.csv'
 
    # download the csv   
    output_gz = 'taxi_data.csv.gz'
    os.system(f"wget {url} -O {output_gz}")
    os.system(f"gunzip {output_gz}")
    # connect to Postgres
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')
   
  
    # create a chunked version of the dataframe
    try:
        df_iterator = pd.read_csv(csv_name, 
                                  chunksize = 100000, 
                                  parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'],
                                  dtype = {"store_and_fwd_flag":'string'})
    except:
        print('CSV not read succesfully')
  
  # create an empty table
    df =pd.read_csv(csv_name, nrows = 1,
                    parse_dates=['tpep_pickup_datetime', 'tpep_dropoff_datetime'],
                    dtype = {"store_and_fwd_flag":'string'})
    df.head(0).to_sql(name = table, con = engine, if_exists='replace')

    # loop over the chunks and ingest them into Postgres db
    for i, chunk in enumerate(df_iterator):
        t_start = time()
        chunk.to_sql(name = table, con = engine, if_exists= 'append')
        t_end = time()
        print(f"Processed chunk {i+1}, took {t_end - t_start:.2f} seconds ")

if __name__ =='__main__':
    # Command line arguments 
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    # user, password, host, port, databasename, table name, csv url
    parser.add_argument('--user',  help='Username for postgres')
    parser.add_argument('--password',  help='password for postgres')
    parser.add_argument('--host',  help='Host for postgres')
    parser.add_argument('--port',  help='port for postgres', type=int)
    parser.add_argument('--db',  help='Destination database for postgres')
    parser.add_argument('--table',  help='Destination table for postgres')
    parser.add_argument('--url',  help='URL of the csv')

    args = parser.parse_args()
    main(args)



