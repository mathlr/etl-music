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
Airflow is an excelent tool to build data pipeline. Within its configurations, one can set peridicity, owners, dependency, retry-policies, alert-policies and log. The basic configurations were used in this pipeline. This pipeline was divided in two phases. First phase: 
- scrape the folder files/Music for any .mp3 files, obtain their metadata, and save a file with the data;
- create the table to store the metadata;
- load the raw data into the table;

Second phase:
- API calls to obtain spotify information about artists; transformation of the data; write file with the data;
- create table to store the staged data;
- load the staged data into the table.
### Database
The idea in this project is to have one main datalake, with the scraped 'raw' data from mp3 files; one datalake for the raw data returned by the API calls, to be maintained as historic data; and one table to perform selects and views from.

PostgreSQL database has been chosen to serve as backend for the airflow and to serve as tablespace to store data. The first table, to store raw data from scraped mp3 metadata, was chosen as a sql database because the schema was already known (from TinyTag package). Second table was not implemented yet, however it should use Cassandra to make it better. Third table was filled with transformed data from spotify's API, ready to be queued or displayed by Superset.

### Data Manipulation/Transformation
Data scraped from the mp3 files and retrieved by the spotify-API needed to be transformed prior to be staged and stored.
- For the mp3 scraping proccess, the object returned by the function of the library TinyTag has many attributes that were not interesting to store/analyse, so only selected attributes were filtered from data. The attributes could return None values, which were substituted by empty strings. Non-printable characters and line-break characters were excluded from the string-attributes before storage. A timestamp field was introduced to every object stored.
- Data returned by the spotfy-API needed transformation too. From the json returned, only a few fields were interesting for analysis. Whenever an artist was not found, the string "N/F" was written in its name. For the genres, the list needed to be converted in a way possible to be inserted directly on the SQL standard. To inform whenever more than one artist were brought by the search, a new field named 'accuracy' was filled.
### Known issues / Future development
#### Temporary storage
Every temporary file created is being stored inside the docker container, but this is not the best practice. The best way to proper store these files would be uploading them to a cloud storage (such as S3 from AWS) and retrieving them only when necessary.
#### Datalake for data downloaded by spotify API
The data downloaded by the search API have to be stored in a lake-type storage to maintain the historic data for re-processing needs. The schema of the data from the API could change any time, so the best way to store this kind of data is using a noSQL db. For the next releases, I will create a Cassandra db to store them.
