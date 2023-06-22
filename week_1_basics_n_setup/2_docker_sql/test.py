#!/usr/bin/env python
# coding: utf-8

import os
import argparse

def main(params):
    url = params.url
    output_gz = 'taxi_data.csv.gz'
    os.system(f"wget {url} -O {output_gz}")
    os.system(f"gunzip {output_gz}")

if __name__ =='__main__':
    # Command line arguments 
    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    # user, password, host, port, databasename, table name, csv url
    parser.add_argument('--url',  help='URL of the csv')

    args = parser.parse_args()
    main(args)
