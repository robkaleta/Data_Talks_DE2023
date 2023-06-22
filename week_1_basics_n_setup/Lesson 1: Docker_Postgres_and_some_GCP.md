# Lesson 1: Docker, Postgres and some GCP

### Docker

Docker installation explained: https://github.com/ziritrion/ml-zoomcamp/blob/11_kserve/notes/05b_virtenvs.md#docker 

- Docker creates containers with software. 
- Host computers can contain multiple containers – host computer is the local machine in this case
- Containers are not aware of each other and do not conflict
- Docker images can be moved to other environments e.g. from local host to GCP
- Docker benefits:
    - Reproducibility
    - Good for local tests and experiments
    - Integration tests (CI/CD) Jenkins or github actions
    - Running pipelines on the cloud
    - Spark     
    - Serverless (AWS lambda, google functions)

 In terminal to start a docker do : 

    docker run -it  --entrypoint= bash python:3.9 
    
This will start an image with python 3.9

**To run a dockerfile and containerise an application:**

 Create a file called “Dockerfile” in the directory you’re working in – no extension
u
    FROM python:3.9.1

    RUN pip install pandas

    workdir /app
    COPY pipeline.py

    ENTRYPOINT ["bash"]

This Docker container defines an image running python and installing pandas. It creates and starts in folder called app and opens up in bash

First we need to build it: 

    docker build -t test:pandas . 
    
(dot means that image is built in current directory)

To run it do: 

    docker run -it test:pandas 
    
(last part is a name for that container)


We need to set up a postgres data base and connect it to PGAdmin. To avoid installing it we can use docker containers instead.

Because we're running 2 containers they need to be connected via docker network

```python
    # to create network
    docker network create pg-network

    docker run -it \
    -e POSTGRES_USER="root" \
    -e POSTGRES_PASSWORD="root" \
    -e POSTGRES_DB="ny_taxi" \
    -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
    -p 5432:5432 \
    --network=pg-network \
    --name pg-database \
    postgres:13
                
    docker run -it \
        -e PGADMIN_DEFAULT_EMAIL=admin@admin.com \
        -e PGADMIN_DEFAULT_PASSWORD=root \
        -p 8080:80 \
        --network=pg-network \
        --name pgadmin \
        dpage/pgadmin4
```
After this we can launch PGAdmin by typing `localhost:8080` in the browser and loggin in using PGADMIN credentials specified above.

## 1.2.4 Dockerizing the Ingestion Script

First thing is to convert the existing ingest notebook into a python script

```jupyter nbconvert --to=script Python_dockerised_script_Taxi_Ingest.ipynb```

All code is in the notebook above.

Main things I did with with docker:

- restarted an existing docker image for postgres and pgadmin
- Created a dockerfile which runs the ingest script in a python environment
- To build the image run `docker build -t taxi_ingest:v001 .` This will read what's in the Dockerfile and generate an image
- Then run it using the code below

        docker run -it \ --network=pg-network \ taxi_ingest:v001 \
            --user=root \
            --password=root \
            --host=pg-database \
            --port=5432 \
            --db=ny_taxi \
            --table=ny_taxi_trips \
            --url=${URL}

## 1.2.5 Running Postgres and pgAdmin with Docker-Compose

We will use docker compose instead of running separate containers and connecting them via a network. This will involve creating a YAML file.

Below is a docker-compose.yaml file put together for pgadmin and pg database

    services:
        pgdatabase:
            image: postgres:13
            environment:
            - POSTGRES_USER=root
            - POSTGRES_PASSWORD=root
            - POSTGRES_DB=ny_taxi
            volumes: 
            - "./ny_taxi_postgres_data:/var/lib/postgresql/data:rw"
            ports:
            - "5432:5432"
        pgadmin:
            image: dpage/pgadmin4
            environment:
            - PGADMIN_DEFAULT_EMAIL=admin@admin.com
            - PGADMIN_DEFAULT_PASSWORD=root
            ports:
            - "8080:80"
            volumes:
            - "./persist_pgadmin:/var/lib/pgadmin"
        
        volumes:
        persist_pgadmin:
        ny_taxi_postgres_data:

To run it use `docker-compose up` which will pick up the `docker-compose.yaml` file in working directory

`docker-compose up -d` will run docker in detached mode - terminal can be used for other things

`docker-compose down` will shut it down

Because the data did not ingest correctly - wrong column types I had to reingest it into Postgres run through `docker compose`. To do this 1. find the network name using `docker network ls` - there will be a default network created by `docker compose`. Substitue that value into the network argument of `docker run -it`

URL="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv.gz"
```python

docker run -it \
  --network=2_docker_sql_default \
  taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pgdatabase \
    --port=5432 \
    --db=ny_taxi \
    --table=yellow_taxi_trips \
    --url=${URL}
    
```
I've also run into a number of issues with multiple copies of docker images and containers. These functions proved to be very useful

`docker ps -a`: lists docker containers 

`docker images`: lists docker images

`docker rm <containerID>`: removes container

`docker rmi <imageID>`: removes image

`docker rm $(docker ps -a -f status=exited -f status=created -q)`: removes all inactive containers

To recap the docker process is as follows.

1. Create a `docker-compose.yaml` file with instructions on what is to be set up in a container.
2. Create `Dockerfile` which contains instructions about the image. In this case it specified python version, which modules to install, and what to do with the script.
3. Use `docker build` to create an image.
4. Start the container by running `docker compose up`
5. Use `docker run -it` to execute the code contained in the python script. 