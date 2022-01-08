# etl-music
Personal project to help me learn some data pipeline concepts. The idea of this project is to retrieve information from a personal mp3 collection, load this information on a sql table to make it possible to use it to fetch some data through spotify apis. These data collected from spotify are loaded in other sql table to make it easier to analyse it.
For this project, I used:
- **Docker-compose** for environment provisioning,
- **Python3** for data manipulation and transformation,
- **PostgreSQL** for DB,
- **Apache Airflow** for workflow/tasks management and log and
- **Apache Superset** for Data visualization.

## Technical discussion
### Environment
For the environment part, the project was made using **docker** with the feature **docker-composer** to combine different softwares. The final yaml file was written based on 2 existing official files from Apache-Airflow repository and Apache-Superset repository. In the yaml file, it was defined:
- Latest Airflow image
- Latest Superset image
- Postgre SQL, as the DB
- Redis, as the broker

Each service had its own container instance, connected to the same host.

### Pipeline
The pipeline consists in two phases. First phase: 
- scrape the folder files/Music for any .mp3 files, obtain their metadata, and save a file with the data;
- create the table to store the metadata;
- load the raw data into the table;

Second phase:
- API calls to obtain spotify information about artists; transformation of the data; write file with the data;
- create table to store the staged data;
- load the staged data into the table.
### Database
PostgreSQL database has been chosen to serve as backend for the airflow and to serve as tablespace to store data. The first table, to store raw data from scraped mp3 metadata, was chosen as a sql database because the schema was already known (from TinyTag package). Second table was filled with transformed data from spotify's API, ready to be queued or displayed by Superset.
### Data Manipulation/Transformation

### Known issues
