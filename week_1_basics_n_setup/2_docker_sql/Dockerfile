FROM python:3.9.1

RUN apt-get install wget
RUN pip install pandas sqlalchemy psycopg2

WORKDIR /app
COPY Python_dockerised_script_Taxi_Ingest.py Python_dockerised_script_Taxi_Ingest.py 

ENTRYPOINT [ "python", "Python_dockerised_script_Taxi_Ingest.py" ]